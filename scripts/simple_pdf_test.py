#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple PDF parsing test script - no agent dependencies.
Tests PDF parsing on files in scratch/ directory.
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import get_parser


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_pdf(pdf_path: Path):
    """Test parsing a single PDF."""
    print_section(f"Testing: {pdf_path.name}")
    
    try:
        # Read PDF
        pdf_bytes = pdf_path.read_bytes()
        print(f"File size: {len(pdf_bytes):,} bytes")
        
        # Parse PDF
        parser = get_parser()
        import time
        start = time.time()
        parsed = parser.parse_pdf(pdf_bytes, extract_tables=False)
        parse_time = time.time() - start
        
        # Show results
        print(f"Parse time: {parse_time*1000:.1f}ms")
        print(f"Pages: {parsed.page_count}")
        print(f"Blocks: {len(parsed.blocks)}")
        print(f"Text length: {len(parsed.text):,} characters")
        
        if parsed.metadata:
            print(f"Metadata:")
            for key, value in parsed.metadata.items():
                if value:
                    print(f"   - {key}: {value}")
        
        # Analyze blocks
        headers = [b for b in parsed.blocks if b.block_type == "header"]
        text_blocks = [b for b in parsed.blocks if b.block_type == "text"]
        
        print(f"\nBlock Analysis:")
        print(f"   - Headers: {len(headers)}")
        print(f"   - Text blocks: {len(text_blocks)}")
        
        # Show headers
        if headers:
            print(f"\nDetected Headers:")
            for i, header in enumerate(headers[:10], 1):
                print(f"   {i}. {header.text[:70]}")
            if len(headers) > 10:
                print(f"   ... and {len(headers) - 10} more")
        
        # Show text preview
        print(f"\nText Preview (first 600 chars):")
        print("-" * 70)
        preview = parsed.text[:600]
        print(preview)
        if len(parsed.text) > 600:
            print("...")
        print("-" * 70)
        
        # Check for contract terms
        text_lower = parsed.text.lower()
        contract_terms = {
            "agreement": "agreement" in text_lower,
            "contract": "contract" in text_lower,
            "term": "term" in text_lower,
            "payment": "payment" in text_lower,
            "liability": "liability" in text_lower or "liable" in text_lower,
            "confidential": "confidential" in text_lower,
            "termination": "termination" in text_lower or "terminate" in text_lower,
            "governing law": "governing law" in text_lower,
            "indemnif": "indemnif" in text_lower,
        }
        
        found = [term for term, present in contract_terms.items() if present]
        print(f"\nContract Terms Found: {len(found)}/{len(contract_terms)}")
        if found:
            print(f"   [+] {', '.join(found)}")
        
        missing = [term for term, present in contract_terms.items() if not present]
        if missing:
            print(f"   [-] Missing: {', '.join(missing)}")
        
        # Validation
        print(f"\nValidation:")
        issues = []
        
        if parsed.page_count == 0:
            issues.append("No pages detected")
        if len(parsed.blocks) < 5:
            issues.append("Very few blocks detected (< 5)")
        if len(parsed.text) < 100:
            issues.append("Very little text extracted (< 100 chars)")
        if len(headers) == 0:
            issues.append("No headers detected")
        if len(found) < 3:
            issues.append("Few contract terms found (< 3)")
        
        if issues:
            print("   [!] Potential Issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   [+] All checks passed!")
        
        return {
            "success": True,
            "pages": parsed.page_count,
            "blocks": len(parsed.blocks),
            "headers": len(headers),
            "text_length": len(parsed.text),
            "terms_found": len(found),
            "parse_time": parse_time
        }
        
    except Exception as e:
        print(f"\n[ERROR] Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def main():
    """Main test workflow."""
    print_section("PDF PARSING TEST - SCRATCH DIRECTORY")
    
    # Find PDFs in scratch directory
    scratch_dir = Path("scratch")
    if not scratch_dir.exists():
        print("[ERROR] scratch/ directory not found")
        return
    
    pdf_files = list(scratch_dir.glob("*.pdf"))
    if not pdf_files:
        print("[ERROR] No PDF files found in scratch/")
        return
    
    print(f"\nFound {len(pdf_files)} PDF files in scratch/:")
    for i, pdf in enumerate(pdf_files, 1):
        size = pdf.stat().st_size
        print(f"   {i}. {pdf.name} ({size:,} bytes)")
    
    # Test each PDF
    results = []
    for pdf_path in pdf_files:
        result = test_pdf(pdf_path)
        result["filename"] = pdf_path.name
        results.append(result)
    
    # Summary
    print_section("SUMMARY")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\nResults:")
    print(f"   [+] Successful: {len(successful)}/{len(results)}")
    print(f"   [-] Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print(f"\n[SUCCESS] Successfully Parsed:")
        for r in successful:
            print(f"   - {r['filename']}")
            print(f"     Pages: {r['pages']}, Blocks: {r['blocks']}, Headers: {r['headers']}")
            print(f"     Text: {r['text_length']:,} chars, Terms: {r['terms_found']}/9")
            print(f"     Parse time: {r['parse_time']*1000:.1f}ms")
    
    if failed:
        print(f"\n[FAILED] Failed to Parse:")
        for r in failed:
            print(f"   - {r['filename']}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)
    
    if successful:
        print("\n[TIP] Next Steps:")
        print("   1. Review the extracted text above")
        print("   2. Verify headers are correctly identified")
        print("   3. Check if contract terms are detected")
        print("   4. Test with agent analysis (requires langgraph)")


if __name__ == "__main__":
    main()


