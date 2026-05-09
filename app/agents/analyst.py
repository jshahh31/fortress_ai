import json
import logging
from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.llm import generate
from app.services.section_utils import (
    get_section_context,
    get_related_sections,
    validate_section_references,
    format_section_reference
)

logger = logging.getLogger(__name__)

class LegalRiskAnalyst:
    async def run(self, state: AgentState) -> AgentState:
        """Analyze legal risks with document structure awareness."""
        logger.info("LegalRiskAnalyst: Analyzing risks with structure context")
        
        # Get document structure if available
        parsed_doc = state.get("parsed_document")
        context = state.get("merged_context", "")
        research = state.get("research_report", "")
        query = state.get("original_query", "")
        
        # Build structure-aware prompt
        if parsed_doc:
            prompt = self._build_structure_aware_prompt(state, parsed_doc)
        else:
            # Fallback to basic prompt if no structure available
            prompt = self._build_basic_prompt(query, research, context)
        
        response = await generate(
            prompt,
            system_prompt="You are a meticulous Legal Risk Analyst. Return JSON only with specific section references."
        )
        
        # Parse and validate response
        risk_analysis = self._parse_and_validate_response(response, parsed_doc)
        
        return {
            **state,
            "risk_analysis": risk_analysis
        }
    
    def _build_structure_aware_prompt(self, state: AgentState, parsed_doc) -> str:
        """Build prompt requiring structure-aware analysis with PDF-extracted sections only."""
        query = state.get("original_query", "")
        research = state.get("research_report", "")
        context = state.get("merged_context", "")
        
        # Build document overview
        doc_overview = self._build_document_overview(parsed_doc)
        
        # Get key clauses summary
        key_clauses_text = self._format_key_clauses(parsed_doc)

        # PHASE 4: Create explicit list of valid sections from PDF
        valid_sections = sorted(parsed_doc.section_map.keys())
        sections_list = "\n".join([
            f"  - {sec}: {parsed_doc.section_map[sec].title} (Page {parsed_doc.section_map[sec].page_num})"
            for sec in valid_sections[:20]  # Show first 20 to avoid overwhelming prompt
        ])

        if len(valid_sections) > 20:
            sections_list += f"\n  - ...and {len(valid_sections) - 20} more sections"

        return f"""
You are a Senior Legal Risk Analyst analyzing a contract with full document structure awareness.

{doc_overview}

{key_clauses_text}

=== VALID SECTIONS FROM THIS PDF DOCUMENT ===
ONLY use these exact section references in your findings:
{sections_list}

QUERY: {query}

RESEARCH FINDINGS:
{research[:2000] if research else "No external research available"}

DOCUMENT CONTEXT:
{context[:3000]}

=== CRITICAL REQUIREMENTS - YOU MUST FOLLOW THESE ===

1. **USE ONLY PDF-EXTRACTED SECTIONS**
   - Every finding MUST reference one of the valid sections listed above
   - Section number MUST match exactly (e.g., "3.2" not "3.2.0" or "Section 3.2")
   - Page number MUST match the PDF-extracted page for that section

2. **RISK JUSTIFICATION REQUIRED**
   - Explain WHY you assigned each risk level (High/Medium/Low)
   - Compare to industry standards when applicable
   - Reference specific contract terms that create the risk

3. **ACTIONABLE RECOMMENDATIONS**
   - Provide PRECISE revision suggestions tailored to the exact contract language
   - Don't use generic advice like "review with counsel"
   - Suggest specific alternative wording when possible

4. **STRICT VALIDATION ENFORCEMENT**
   - Findings with invalid sections will be REJECTED
   - Findings without exact PDF quotes will be REJECTED
   - Findings with wrong page numbers will be REJECTED

5. **NO INVENTED SECTIONS**
   - Do NOT create section references that don't exist in the PDF
   - Do NOT modify the section numbers or titles
   - Use ONLY the sections provided in the VALID SECTIONS list

OUTPUT FORMAT (JSON):
{{
  "findings": [
    {{
      "section": "3.2",
      "page": 5,
      "title": "Payment Terms Issue",
      "risk": "High",
      "justification": "60-day payment term exceeds industry standard of 30 days, creating cash flow risk. No late payment penalties specified, removing incentive for timely payment.",
      "contract_text": "Client shall pay within sixty (60) days of receipt of invoice. No late fees shall apply.",
      "recommendation": "Revise to 'thirty (30) days' to match standard B2B terms. Add clause: 'Late payments shall incur 1.5% monthly interest.'",
      "priority": 1,
      "related_sections": ["7.1", "9.2"],
      "clause_type": "payment"
    }}
  ]
}}

=== IMPORTANT NOTES ===
- ALL section references MUST come from the VALID SECTIONS list above
- ALL contract_text MUST be exact quotes from the specified PDF section
- ANY deviation will cause the finding to be rejected
- Use the document structure provided - do NOT invent your own sections
"""
    
    def _build_basic_prompt(self, query: str, research: str, context: str) -> str:
        """Fallback prompt when no document structure is available."""
        return f"""
You are a Senior Legal Risk Analyst analyzing a contract.

QUERY: {query}

RESEARCH FINDINGS:
{research[:2000] if research else "No external research available"}

DOCUMENT CONTEXT:
{context[:3000]}

INSTRUCTIONS:
1. Identify Red Flags: Points of high risk or potential legal violation
2. Identify Penalties: Possible fines or legal consequences
3. Identify Obligations: Key actions required for compliance
4. Categorize each risk as High, Medium, or Low
5. Reference page numbers and section headers when available

OUTPUT FORMAT:
Return ONLY a JSON object with this structure:
{{
    "red_flags": [
        {{"issue": "...", "severity": "High/Med/Low", "description": "..."}}
    ],
    "penalties": [
        {{"type": "...", "severity": "High/Med/Low", "impact": "..."}}
    ],
    "obligations": [
        {{"task": "...", "deadline": "...", "description": "..."}}
    ],
    "summary": "..."
}}
"""
    
    def _build_document_overview(self, parsed_doc) -> str:
        """Build document overview section."""
        if not parsed_doc:
            return ""
        
        structure = parsed_doc.structure if hasattr(parsed_doc, 'structure') else {}
        key_clauses = structure.get("key_clauses", {})
        
        overview = [
            "DOCUMENT OVERVIEW:",
            f"- Total Pages: {parsed_doc.page_count}",
            f"- Total Sections: {len(parsed_doc.sections)}",
            f"- Key Clause Types: {', '.join(key_clauses.keys()) if key_clauses else 'None identified'}"
        ]
        
        return "\n".join(overview)
    
    def _format_key_clauses(self, parsed_doc) -> str:
        """Format key clauses for prompt context."""
        if not parsed_doc or not hasattr(parsed_doc, 'structure'):
            return ""
        
        key_clauses = parsed_doc.structure.get("key_clauses", {})
        if not key_clauses:
            return ""
        
        lines = ["KEY CLAUSES TO ANALYZE:"]
        for clause_type, sections in key_clauses.items():
            lines.append(f"\n{clause_type.upper()}:")
            for sec_ref in sections[:3]:  # Show first 3 of each type
                lines.append(f"  - {sec_ref}")
            if len(sections) > 3:
                lines.append(f"  - ... and {len(sections) - 3} more")
        
        return "\n".join(lines)
    
    def _format_related_sections(self, sections: List[Dict]) -> str:
        """Format related sections for prompt context."""
        if not sections:
            return "None"
        
        return "\n".join([
            f"- {sec['number']} {sec['title']} (Page {sec['page']}) [{sec.get('relationship', 'related')}]"
            for sec in sections
        ])
    
    def _parse_and_validate_response(self, response: str, parsed_doc) -> Dict:
        """Parse response and validate section references with strict enforcement."""
        try:
            # Clean response
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:-3].strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response[3:-3].strip()

            analysis = json.loads(clean_response)

            # PHASE 3: Strict validation of section references
            if parsed_doc and "findings" in analysis:
                # Track findings with missing/invalid section references
                validated_findings = []
                validation_errors = []

                for finding in analysis["findings"]:
                    section_ref = finding.get("section")
                    page_num = finding.get("page")
                    contract_text = finding.get("contract_text")

                    # PHASE 4: Enforce mandatory section references
                    if not section_ref:
                        validation_errors.append(
                            f"Finding missing section reference: {finding.get('title', 'Untitled')}"
                        )
                        logger.warning(f"Rejecting finding without section reference: {finding.get('title', 'Untitled')}")
                        continue

                    # Validate section exists in document
                    if section_ref and hasattr(parsed_doc, 'section_map') and section_ref not in parsed_doc.section_map:
                        validation_errors.append(
                            f"Invalid section reference '{section_ref}' in finding: {finding.get('title', 'Untitled')}"
                        )
                        # Still include but mark as invalid
                        if 'validation_errors' not in finding:
                            finding['validation_errors'] = []
                        finding['validation_errors'].append(f"Section {section_ref} not found in document")

                    # Validate page number if section reference exists
                    if section_ref and not page_num:
                        validation_errors.append(
                            f"Finding for section {section_ref} missing page number: {finding.get('title', 'Untitled')}"
                        )
                        if 'validation_errors' not in finding:
                            finding['validation_errors'] = []
                        finding['validation_errors'].append("Missing page number")

                    # Validate contract text if section reference exists
                    if section_ref and not contract_text:
                        validation_errors.append(
                            f"Finding for section {section_ref} missing contract text: {finding.get('title', 'Untitled')}"
                        )
                        if 'validation_errors' not in finding:
                            finding['validation_errors'] = []
                        finding['validation_errors'].append("Missing specific contract language")

                    validated_findings.append(finding)

                # Update analysis with validated findings
                analysis["findings"] = validated_findings

                # Add validation summary
                if validation_errors:
                    analysis["validation_errors"] = validation_errors
                    logger.warning(f"Section reference validation errors: {validation_errors}")

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            return {
                "error": "Failed to parse analysis",
                "raw_output": response,
                "findings": [],
                "red_flags": [],
                "penalties": [],
                "obligations": [],
                "summary": "Analysis failed to format correctly."
            }
