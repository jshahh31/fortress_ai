"""
Test Phase 2 structure-aware analysis features.
Validates section references, deduplication, and coverage metrics.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import get_parser
from app.services.section_utils import (
    get_section_context,
    validate_section_references,
    get_related_sections,
    calculate_coverage_metrics,
    get_key_clauses_summary
)
from app.services.analysis import _deduplicate_findings, _compare_risk_level


def test_section_reference_validation():
    """Test section reference validation."""
    print("\n" + "="*80)
    print("  TEST 1: Section Reference Validation")
    print("="*80)
    
    # Parse a real contract
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    if not pdf_path.exists():
        print(f"❌ Contract not found: {pdf_path}")
        return False
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    print(f"✅ Parsed document: {parsed.page_count} pages, {len(parsed.sections)} sections")
    
    # Test with valid and invalid references
    test_analysis = {
        "findings": [
            {"section": "1.2", "page": 1, "title": "Valid Reference"},
            {"section": "999.9", "page": 999, "title": "Invalid Reference"},
            {"section": "1.3", "page": 1, "title": "Another Valid"}
        ]
    }
    
    errors = validate_section_references(test_analysis, parsed)
    
    print(f"\nValidation Results:")
    print(f"  - Total findings: {len(test_analysis['findings'])}")
    print(f"  - Validation errors: {len(errors)}")
    
    if errors:
        print(f"\n  Errors found:")
        for error in errors:
            print(f"    ❌ {error}")
    
    # Should have exactly 1 error (999.9)
    success = len(errors) == 1 and "999.9" in errors[0]
    print(f"\n{'✅' if success else '❌'} Validation test {'PASSED' if success else 'FAILED'}")
    return success


def test_deduplication():
    """Test deduplication logic."""
    print("\n" + "="*80)
    print("  TEST 2: Deduplication Logic")
    print("="*80)
    
    # Parse document
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    # Create test findings with duplicates
    test_findings = [
        {
            "section": "1.2",
            "title": "Contract Monitor Issue",
            "risk": "High",
            "page": 1
        },
        {
            "section": "1.2",
            "title": "contract monitor issue",  # Duplicate (case insensitive)
            "risk": "Medium",  # Lower risk
            "page": 1
        },
        {
            "section": "1.2",
            "title": "Different Issue",  # Different title, same section
            "risk": "Low",
            "page": 1
        },
        {
            "section": "1.3",
            "title": "Contractor Definition",
            "risk": "Medium",
            "page": 1
        }
    ]
    
    print(f"\nBefore deduplication: {len(test_findings)} findings")
    for i, f in enumerate(test_findings, 1):
        print(f"  {i}. Section {f['section']}: {f['title']} ({f['risk']})")
    
    deduplicated = _deduplicate_findings(test_findings, parsed)
    
    print(f"\nAfter deduplication: {len(deduplicated)} findings")
    for i, f in enumerate(deduplicated, 1):
        print(f"  {i}. Section {f['section']}: {f['title']} ({f['risk']})")
    
    # Should have 3 findings (removed the Medium risk duplicate)
    success = len(deduplicated) == 3
    
    # Verify the High risk version was kept
    section_12_findings = [f for f in deduplicated if f['section'] == '1.2']
    has_high_risk = any(f['risk'] == 'High' for f in section_12_findings)
    has_medium_risk = any(f['risk'] == 'Medium' and 'monitor' in f['title'].lower() for f in section_12_findings)
    
    success = success and has_high_risk and not has_medium_risk
    
    print(f"\n{'✅' if success else '❌'} Deduplication test {'PASSED' if success else 'FAILED'}")
    print(f"  - Removed duplicates: {len(test_findings) - len(deduplicated)}")
    print(f"  - Kept higher risk version: {has_high_risk}")
    print(f"  - Removed lower risk duplicate: {not has_medium_risk}")
    
    return success


def test_coverage_metrics():
    """Test coverage calculation."""
    print("\n" + "="*80)
    print("  TEST 3: Coverage Metrics")
    print("="*80)
    
    # Parse document
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    # Create analysis with some findings
    test_analysis = {
        "findings": [
            {"section": "1.2", "risk": "High"},
            {"section": "1.3", "risk": "Medium"},
            {"section": "1.4", "risk": "Low"}
        ]
    }
    
    metrics = calculate_coverage_metrics(test_analysis, parsed)
    
    print(f"\nCoverage Metrics:")
    print(f"  - Total sections: {metrics.get('total_sections', 0)}")
    print(f"  - Analyzed sections: {metrics.get('analyzed_sections', 0)}")
    print(f"  - Coverage: {metrics.get('section_coverage_pct', 0)}%")
    
    if 'key_clause_coverage_pct' in metrics:
        print(f"  - Key clause coverage: {metrics.get('key_clause_coverage_pct', 0)}%")
    
    if 'missing_key_clauses' in metrics:
        missing = metrics['missing_key_clauses']
        print(f"  - Missing key clauses: {len(missing)}")
        if missing:
            print(f"\n  First 3 missing clauses:")
            for clause in missing[:3]:
                print(f"    - Section {clause['section']}: {clause['title']} ({clause['type']})")
    
    success = metrics.get('analyzed_sections', 0) == 3
    print(f"\n{'✅' if success else '❌'} Coverage test {'PASSED' if success else 'FAILED'}")
    
    return success


def test_section_context():
    """Test section context retrieval."""
    print("\n" + "="*80)
    print("  TEST 4: Section Context Retrieval")
    print("="*80)
    
    # Parse document
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    # Test getting context for a section
    section_ref = "1.2"
    context = get_section_context(parsed, section_ref)
    
    if context:
        print(f"\n✅ Retrieved context for Section {section_ref}:")
        print(f"  - Title: {context['title']}")
        print(f"  - Page: {context['page']}")
        print(f"  - Type: {context['type']}")
        print(f"  - Level: {context['level']}")
        print(f"  - Content length: {len(context['content'])} chars")
        print(f"  - Related blocks: {context.get('block_count', 0)}")
        success = True
    else:
        print(f"❌ Failed to retrieve context for Section {section_ref}")
        success = False
    
    # Test invalid reference
    invalid_context = get_section_context(parsed, "999.9")
    if invalid_context is None:
        print(f"\n✅ Correctly returned None for invalid section 999.9")
    else:
        print(f"\n❌ Should have returned None for invalid section")
        success = False
    
    print(f"\n{'✅' if success else '❌'} Section context test {'PASSED' if success else 'FAILED'}")
    return success


def test_related_sections():
    """Test related section finding."""
    print("\n" + "="*80)
    print("  TEST 5: Related Sections")
    print("="*80)
    
    # Parse document
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    # Get related sections for 1.2
    section_ref = "1.2"
    related = get_related_sections(parsed, section_ref, "general")
    
    print(f"\nRelated sections for {section_ref}:")
    print(f"  - Found {len(related)} related sections")
    
    if related:
        print(f"\n  First 5 related sections:")
        for sec in related[:5]:
            print(f"    - {sec['number']}: {sec['title']} ({sec.get('relationship', 'related')})")
    
    success = len(related) > 0
    print(f"\n{'✅' if success else '❌'} Related sections test {'PASSED' if success else 'FAILED'}")
    
    return success


def test_key_clauses_summary():
    """Test key clauses summary."""
    print("\n" + "="*80)
    print("  TEST 6: Key Clauses Summary")
    print("="*80)
    
    # Parse document
    parser = get_parser()
    pdf_path = Path("scratch/med_dir_actualcontract.pdf")
    
    with open(pdf_path, "rb") as f:
        parsed = parser.parse_pdf(f.read())
    
    summary = get_key_clauses_summary(parsed)
    
    print(f"\nKey Clauses Summary:")
    print(f"  - Clause types found: {len(summary)}")
    
    for clause_type, sections in summary.items():
        print(f"\n  {clause_type.upper()}: {len(sections)} sections")
        for sec in sections[:3]:
            print(f"    - Section {sec['number']}: {sec['title']} (Page {sec['page']})")
        if len(sections) > 3:
            print(f"    - ... and {len(sections) - 3} more")
    
    success = len(summary) > 0
    print(f"\n{'✅' if success else '❌'} Key clauses test {'PASSED' if success else 'FAILED'}")
    
    return success


def main():
    """Run all Phase 2 validation tests."""
    print("\n" + "="*80)
    print("  PHASE 2 FEATURE VALIDATION")
    print("="*80)
    print("\nTesting structure-aware analysis features with real contract...")
    
    results = []
    
    try:
        results.append(("Section Reference Validation", test_section_reference_validation()))
        results.append(("Deduplication Logic", test_deduplication()))
        results.append(("Coverage Metrics", test_coverage_metrics()))
        results.append(("Section Context Retrieval", test_section_context()))
        results.append(("Related Sections", test_related_sections()))
        results.append(("Key Clauses Summary", test_key_clauses_summary()))
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    
    if passed == total:
        print("\n🎉 All Phase 2 features validated successfully!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
