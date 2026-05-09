"""
Utility functions for working with document sections and structure.
Provides section referencing, validation, and relationship mapping.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from app.services.document_parser import ParsedDocument
from app.services.document_structure import Section
import logging
import re

logger = logging.getLogger(__name__)

def get_section_context(parsed: ParsedDocument, section_ref: str) -> Optional[Dict[str, Any]]:
    """
    Get full context for a section reference.

    Args:
        parsed: ParsedDocument containing structure
        section_ref: Section number (e.g., "3.2")

    Returns:
        Dictionary with section details or None if not found
    """
    if not parsed or not parsed.section_map or section_ref not in parsed.section_map:
        logger.debug(f"Section {section_ref} not found in document")
        return None

    section = parsed.section_map[section_ref]

    # Get related content blocks
    related_blocks = []
    if hasattr(section, 'start_block_index') and section.start_block_index >= 0:
        end_idx = (section.end_block_index + 1) if hasattr(section, 'end_block_index') else (section.start_block_index + 5)
        related_blocks = parsed.blocks[section.start_block_index:min(end_idx, len(parsed.blocks))]

    return {
        "number": section.number,
        "title": section.title,
        "page": section.page_num,
        "level": section.level,
        "type": section.clause_type,
        "content": section.content,
        "full_text": f"## {section.number} {section.title}\n\n{section.content}",
        "related_blocks": [b.text for b in related_blocks],
        "block_count": len(related_blocks)
    }

def validate_section_references(analysis: Dict, parsed: ParsedDocument) -> List[str]:
    """
    Validate all section references in analysis exist in document.

    Args:
        analysis: Risk analysis dictionary
        parsed: ParsedDocument with section map

    Returns:
        List of error messages for invalid references
    """
    if not parsed or not hasattr(parsed, 'section_map') or not parsed.section_map:
        return ["Document has no section map for validation"]

    errors = []
    findings = analysis.get("findings", [])

    for i, finding in enumerate(findings, 1):
        section_ref = finding.get("section")
        if section_ref and section_ref not in parsed.section_map:
            errors.append(f"Finding {i}: Invalid section reference '{section_ref}'")

        # Validate page number if provided
        page_num = finding.get("page")
        if page_num and section_ref and section_ref in parsed.section_map:
            actual_page = parsed.section_map[section_ref].page_num
            if page_num != actual_page:
                errors.append(f"Finding {i}: Page mismatch for section {section_ref} (stated: {page_num}, actual: {actual_page})")

    return errors

def get_related_sections(parsed: ParsedDocument, section_ref: str, clause_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Find sections related by clause type or hierarchy.

    Args:
        parsed: ParsedDocument with structure
        section_ref: Current section number
        clause_type: Optional clause type filter

    Returns:
        List of related section dictionaries
    """
    if not parsed or not parsed.sections or section_ref not in parsed.section_map:
        return []

    current = parsed.section_map[section_ref]
    related = []
    seen = {section_ref}  # Avoid duplicates

    # 1. Same clause type sections
    if clause_type:
        for sec in parsed.sections:
            if (sec.clause_type == clause_type and
                sec.number != section_ref and
                sec.number not in seen):
                related.append({
                    "number": sec.number,
                    "title": sec.title,
                    "page": sec.page_num,
                    "type": sec.clause_type,
                    "relationship": "same_clause_type"
                })
                seen.add(sec.number)

    # 2. Parent/child relationships
    if "." in section_ref:
        # Check parent
        parent_ref = ".".join(section_ref.split(".")[:-1])
        if parent_ref in parsed.section_map and parent_ref not in seen:
            parent = parsed.section_map[parent_ref]
            related.append({
                "number": parent.number,
                "title": parent.title,
                "page": parent.page_num,
                "type": parent.clause_type,
                "relationship": "parent"
            })
            seen.add(parent.number)

        # Check children
        prefix = section_ref + "."
        for sec in parsed.sections:
            if sec.number.startswith(prefix) and sec.number not in seen:
                related.append({
                    "number": sec.number,
                    "title": sec.title,
                    "page": sec.page_num,
                    "type": sec.clause_type,
                    "relationship": "child"
                })
                seen.add(sec.number)

    # 3. Same level sections (siblings)
    if "." in section_ref:
        parent_ref = ".".join(section_ref.split(".")[:-1])
        base_num = section_ref.split(".")[-1]

        for sec in parsed.sections:
            if (sec.number.startswith(parent_ref + ".") and
                sec.number != section_ref and
                sec.number not in seen and
                sec.number.split(".")[-1].isdigit()):
                related.append({
                    "number": sec.number,
                    "title": sec.title,
                    "page": sec.page_num,
                    "type": sec.clause_type,
                    "relationship": "sibling"
                })
                seen.add(sec.number)

    # 4. Cross-referenced sections (from content)
    content_refs = _find_content_references(current.content)
    for ref in content_refs:
        if (ref in parsed.section_map and
            ref not in seen and
            ref != section_ref):
            ref_sec = parsed.section_map[ref]
            related.append({
                "number": ref,
                "title": ref_sec.title,
                "page": ref_sec.page_num,
                "type": ref_sec.clause_type,
                "relationship": "content_reference"
            })
            seen.add(ref)

    return related

def _find_content_references(content: str) -> Set[str]:
    """
    Find section references in text content.
    Looks for patterns like "Section 3.2", "Clause 5.1", "3.2.4", etc.
    """
    # Patterns for section references
    patterns = [
        r'\bSection\s+(\d+(?:\.\d+)*)\b',  # "Section 3.2"
        r'\bClause\s+(\d+(?:\.\d+)*)\b',   # "Clause 5.1"
        r'\b(\d+(?:\.\d+)*)\b\s*(?:\([sS]ee|[rR]ef(?:erence)?|[aA]bove|[bB]elow)\b',  # "3.2 (see...)"
        r'\bArticle\s+(\d+(?:\.\d+)*)\b', # "Article 7"
        r'\bParagrap?h\s+(\d+(?:\.\d+)*)\b' # "Paragraph 2.1"
    ]

    references = set()

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean up the reference
            ref = match.strip(".,;:!")
            if ref and len(ref) <= 10:  # Reasonable length for section number
                references.add(ref)

    return references

def calculate_coverage_metrics(analysis: Dict, parsed: ParsedDocument) -> Dict[str, Any]:
    """
    Calculate coverage metrics for how thoroughly the document was analyzed.

    Args:
        analysis: Risk analysis with findings
        parsed: ParsedDocument with structure

    Returns:
        Dictionary with coverage metrics
    """
    if not parsed or not hasattr(parsed, 'sections'):
        return {
            "error": "No document structure available",
            "total_sections": 0,
            "analyzed_sections": 0
        }

    findings = analysis.get("findings", [])
    analyzed_sections = {f.get("section") for f in findings if f.get("section")}

    # Basic metrics
    metrics = {
        "total_sections": len(parsed.sections),
        "analyzed_sections": len(analyzed_sections),
        "section_coverage_pct": round((len(analyzed_sections) / len(parsed.sections)) * 100, 1) if parsed.sections else 0
    }

    # Key clause metrics
    key_clauses = parsed.structure.get("key_clauses", {}) if hasattr(parsed, 'structure') else {}
    total_key_sections = sum(len(sections) for sections in key_clauses.values()) if key_clauses else 0
    covered_key_sections = 0
    missing_key_clauses = []

    if total_key_sections > 0:
        for clause_type, sections in key_clauses.items():
            for sec_ref in sections:
                # Parse reference format: "3.2 Payment Terms (p.5)"
                parts = sec_ref.split(" (p.")
                if len(parts) == 2:
                    number_title = parts[0].split(" ", 1)
                    if len(number_title) == 2:
                        number, title = number_title
                        page = int(parts[1].rstrip(")"))
                        
                        if number in analyzed_sections:
                            covered_key_sections += 1
                        else:
                            missing_key_clauses.append({
                                "section": number,
                                "title": title,
                                "type": clause_type,
                                "page": page
                            })

        metrics.update({
            "key_clause_types": len(key_clauses),
            "total_key_sections": total_key_sections,
            "covered_key_sections": covered_key_sections,
            "key_clause_coverage_pct": round((covered_key_sections / total_key_sections) * 100, 1),
            "missing_key_clauses": missing_key_clauses
        })

    # Coverage by clause type
    coverage_by_type = {}
    for sec in parsed.sections:
        clause_type = sec.clause_type
        if clause_type not in coverage_by_type:
            coverage_by_type[clause_type] = {"total": 0, "analyzed": 0}
        coverage_by_type[clause_type]["total"] += 1
        if sec.number in analyzed_sections:
            coverage_by_type[clause_type]["analyzed"] += 1

    for clause_type in coverage_by_type:
        total = coverage_by_type[clause_type]["total"]
        analyzed = coverage_by_type[clause_type]["analyzed"]
        coverage_by_type[clause_type]["coverage_pct"] = round((analyzed / total) * 100, 1) if total else 0

    metrics["coverage_by_type"] = coverage_by_type

    return metrics

def format_section_reference(section: Section) -> str:
    """
    Format a section as a readable reference string.
    
    Args:
        section: The section to format
        
    Returns:
        Formatted string like "Section 3.2: Payment Terms (Page 5)"
    """
    return f"Section {section.number}: {section.title} (Page {section.page_num})"


def get_section_by_page(parsed: ParsedDocument, page_num: int) -> List[Section]:
    """
    Get all sections on a specific page.
    
    Args:
        parsed: The parsed document
        page_num: Page number to search
        
    Returns:
        List of sections on that page
    """
    if not parsed or not parsed.sections:
        return []
    return [sec for sec in parsed.sections if sec.page_num == page_num]


def get_key_clauses_summary(parsed: ParsedDocument) -> Dict[str, List[Dict]]:
    """
    Get a summary of key clauses organized by type.
    
    Args:
        parsed: The parsed document
        
    Returns:
        Dictionary mapping clause types to section details
    """
    if not parsed or not hasattr(parsed, 'structure'):
        return {}
    
    key_clauses = {}
    
    for clause_type, references in parsed.structure.get("key_clauses", {}).items():
        sections = []
        for ref in references:
            # Parse reference format: "3.2 Payment Terms (p.5)"
            parts = ref.split(" (p.")
            if len(parts) == 2:
                number_title = parts[0].split(" ", 1)
                if len(number_title) == 2:
                    number, title = number_title
                    page = int(parts[1].rstrip(")"))
                    sections.append({
                        "number": number,
                        "title": title,
                        "page": page
                    })
        
        key_clauses[clause_type] = sections
    
    return key_clauses


def find_missing_key_clauses(analyzed_sections: Set[str], parsed: ParsedDocument) -> List[Dict[str, Any]]:
    """
    Find key clauses that were not analyzed.
    
    Args:
        analyzed_sections: Set of section numbers that were analyzed
        parsed: The parsed document
        
    Returns:
        List of missing key clause details
    """
    if not parsed or not hasattr(parsed, 'structure'):
        return []
    
    missing = []
    key_clauses = parsed.structure.get("key_clauses", {})
    
    for clause_type, references in key_clauses.items():
        for ref in references:
            # Parse reference format: "3.2 Payment Terms (p.5)"
            parts = ref.split(" (p.")
            if len(parts) == 2:
                number_title = parts[0].split(" ", 1)
                if len(number_title) == 2:
                    number, title = number_title
                    page = int(parts[1].rstrip(")"))
                    
                    if number not in analyzed_sections:
                        missing.append({
                            "section": number,
                            "title": title,
                            "type": clause_type,
                            "page": page
                        })
    
    return missing


