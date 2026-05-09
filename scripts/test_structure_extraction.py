#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the new document structure extraction with real contracts.
"""

import sys
import os
from pathlib import Path
from pprint import pprint

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import get_parser

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_contract_structure(pdf_path: Path):
    """Test structure extraction on a real contract."""
    print_section(f"Testing Structure: {pdf_path.name}")

    # Parse the contract
    parser = get_parser()
    pdf_bytes = pdf_path.read_bytes()
    parsed = parser.parse_pdf(pdf_bytes)

    # Show basic info
    print(f"File: {pdf_path.name}")
    print(f"Pages: {parsed.page_count}")
    print(f"Blocks: {len(parsed.blocks)}")
    print(f"Sections: {len(parsed.sections)}")
    print(f"Structure Keys: {list(parsed.structure.keys())}")

    # Show structure details
    print(f"\nStructure Analysis:")
    print(f"   - Hierarchy Levels: {len(parsed.structure.get('hierarchy', []))}")
    print(f"   - Key Clauses: {len(parsed.structure.get('key_clauses', {}))}")
    print(f"   - Section Count: {parsed.structure.get('section_count', 0)}")

    # Show first 10 sections
    if parsed.sections:
        print(f"\nFirst 10 Sections:")
        for i, section in enumerate(parsed.sections[:10], 1):
            print(f"   {i}. {section.number} {section.title} (Page {section.page_num}, Level {section.level})")
            print(f"      - Type: {section.clause_type}")
            print(f"      - Content preview: {section.content[:60]}...")

        if len(parsed.sections) > 10:
            print(f"   ... and {len(parsed.sections) - 10} more sections")

    # Show key clauses
    if 'key_clauses' in parsed.structure:
        clauses = parsed.structure['key_clauses']
        if clauses:
            print(f"\nKey Clauses Found:")
            for clause_type, sections in clauses.items():
                if sections:
                    print(f"   - {clause_type}: {len(sections)} sections")
                    for sec in sections[:3]:  # Show first 3 of each type
                        print(f"     * {sec['number']} {sec['title']}")

    # Show hierarchy
    if 'hierarchy' in parsed.structure:
        hierarchy = parsed.structure['hierarchy']
        if hierarchy:
            print(f"\nDocument Hierarchy (first 3 levels):")
            for i, level in enumerate(hierarchy[:3], 1):
                print(f"   Level {i}: {len(level)} sections")
                for sec in level[:5]:  # Show first 5 per level
                    print(f"     * {sec['number']} {sec['title']}")
                if len(level) > 5:
                    print(f"     ... and {len(level) - 5} more")

    # Test reference mapping
    print(f"\nReference Mapping Test:")
    test_sections = ["1", "1.1", "2", "3"]  # Common section numbers to test
    for sec_num in test_sections:
        if sec_num in parsed.section_map:
            section = parsed.section_map[sec_num]
            print(f"   [OK] Section {sec_num}: {section.title} (Page {section.page_num})")
        else:
            print(f"   [MISSING] Section {sec_num}: Not found")

    return parsed

def main():
    """Main test workflow."""
    print_section("DOCUMENT STRUCTURE EXTRACTION TEST")

    # Find PDFs in scratch directory
    scratch_dir = Path("scratch")
    if not scratch_dir.exists():
        print("[ERROR] scratch/ directory not found")
        return

    pdf_files = list(scratch_dir.glob("*.pdf"))
    if not pdf_files:
        print("[ERROR] No PDF files found in scratch/")
        return

    print(f"Found {len(pdf_files)} PDF files in scratch/:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf.name}")

    # Test the contract with most pages (likely most structure)
    contract_to_test = max(pdf_files, key=lambda p: p.stat().st_size)
    print(f"\nSelected for testing: {contract_to_test.name}")

    # Run the test
    parsed = test_contract_structure(contract_to_test)

    # Validation summary
    print_section("SUMMARY")

    issues = []
    successes = []

    # Check section detection
    if len(parsed.sections) > 0:
        successes.append(f"[OK] Found {len(parsed.sections)} sections")
    else:
        issues.append("[ERROR] No sections detected")

    # Check hierarchy
    if 'hierarchy' in parsed.structure and parsed.structure['hierarchy']:
        successes.append(f"[OK] Built hierarchy with {len(parsed.structure['hierarchy'])} levels")
    else:
        issues.append("[ERROR] No hierarchy built")

    # Check key clauses
    if 'key_clauses' in parsed.structure and parsed.structure['key_clauses']:
        found_clauses = sum(len(v) for v in parsed.structure['key_clauses'].values())
        successes.append(f"[OK] Identified {found_clauses} key clauses")
    else:
        issues.append("[ERROR] No key clauses identified")

    # Check reference mapping
    if parsed.section_map:
        successes.append(f"[OK] Created reference map with {len(parsed.section_map)} entries")
    else:
        issues.append("[ERROR] No reference mapping created")

    # Print results
    print("Results:")
    for success in successes:
        print(f"   {success}")

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\nAll checks passed!")

    # Show what agents will receive
    print_section("AGENT CONTEXT")
    print("Agents will receive this structured data:")
    print(f"\nDocument Structure Summary:")
    print(f"- {len(parsed.sections)} sections across {parsed.page_count} pages")
    print(f"- {len(parsed.structure.get('hierarchy', []))} hierarchy levels")
    print(f"- {sum(len(v) for v in parsed.structure.get('key_clauses', {}).values())} key clauses")

    if parsed.sections:
        print(f"\nSample Section Data:")
        sample = parsed.sections[0]
        print(f"""{{
    'number': '{sample.number}',
    'title': '{sample.title}',
    'page': {sample.page_num},
    'level': {sample.level},
    'type': '{sample.clause_type}',
    'content_preview': '{sample.content[:50]}...'
}}""")

if __name__ == "__main__":
    main()

# Made with Bob
