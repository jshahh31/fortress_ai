#!/usr/bin/env python3
"""
Interactive script to validate PDF parsing and agent analysis.
Run this to test the complete pipeline with visual output.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import get_parser
from app.agents.graph import run_legal_audit


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def validate_parsing(pdf_path: Path) -> dict:
    """Validate PDF parsing and return results."""
    print_section(f"PARSING: {pdf_path.name}")
    
    parser = get_parser()
    pdf_bytes = pdf_path.read_bytes()
    
    print(f"📄 File size: {len(pdf_bytes):,} bytes")
    
    # Parse without tables (fast)
    import time
    start = time.time()
    parsed = parser.parse_pdf(pdf_bytes, extract_tables=False)
    parse_time = time.time() - start
    
    print(f"⚡ Parse time: {parse_time*1000:.1f}ms")
    print(f"📊 Pages: {parsed.page_count}")
    print(f"📦 Blocks: {len(parsed.blocks)}")
    print(f"📝 Text length: {len(parsed.text):,} characters")
    print(f"📋 Metadata: {parsed.metadata}")
    
    # Analyze block types
    headers = [b for b in parsed.blocks if b.block_type == "header"]
    text_blocks = [b for b in parsed.blocks if b.block_type == "text"]
    
    print(f"\n🏷️  Block Analysis:")
    print(f"   - Headers: {len(headers)}")
    print(f"   - Text blocks: {len(text_blocks)}")
    
    if headers:
        print(f"\n📑 Detected Headers:")
        for i, header in enumerate(headers[:10], 1):
            print(f"   {i}. {header.text[:60]}")
            if i >= 10 and len(headers) > 10:
                print(f"   ... and {len(headers) - 10} more")
                break
    
    # Show text preview
    print(f"\n📄 Text Preview (first 500 chars):")
    print("-" * 70)
    print(parsed.text[:500])
    if len(parsed.text) > 500:
        print("...")
    print("-" * 70)
    
    # Check for key contract terms
    contract_terms = [
        "agreement", "contract", "term", "payment", "liability",
        "confidential", "termination", "governing law", "indemnif"
    ]
    
    found_terms = [term for term in contract_terms if term in parsed.text.lower()]
    print(f"\n🔍 Contract Terms Found: {len(found_terms)}/{len(contract_terms)}")
    print(f"   {', '.join(found_terms)}")
    
    return {
        "parsed": parsed,
        "parse_time": parse_time,
        "headers": headers,
        "found_terms": found_terms
    }


async def validate_agent_analysis(parsed_text: str, filename: str):
    """Validate agent analysis pipeline."""
    print_section("AGENT ANALYSIS PIPELINE")
    
    print("🤖 Running multi-agent analysis...")
    print("   Orchestrator → Researcher → Analyst → Auditor")
    
    try:
        import time
        start = time.time()
        
        final_state = await run_legal_audit(
            query=f"Analyze this contract for legal risks and compliance issues",
            text_context=parsed_text
        )
        
        analysis_time = time.time() - start
        
        print(f"\n✅ Analysis completed in {analysis_time:.1f}s")
        
        # Extract results
        research_report = final_state.get("research_report", "")
        risk_analysis = final_state.get("risk_analysis", {})
        final_report = final_state.get("final_report_md", "")
        errors = final_state.get("errors", [])
        
        print(f"\n📊 Analysis Results:")
        print(f"   - Research report: {len(research_report)} chars")
        print(f"   - Risk analysis keys: {list(risk_analysis.keys())}")
        print(f"   - Final report: {len(final_report)} chars")
        print(f"   - Errors: {len(errors)}")
        
        if errors:
            print(f"\n⚠️  Errors encountered:")
            for error in errors:
                print(f"   - {error}")
        
        # Show risk analysis details
        if risk_analysis:
            print(f"\n🚨 Risk Analysis:")
            
            red_flags = risk_analysis.get("red_flags", [])
            if red_flags:
                print(f"\n   Red Flags ({len(red_flags)}):")
                for i, flag in enumerate(red_flags[:5], 1):
                    severity = flag.get("severity", "Unknown")
                    issue = flag.get("issue", "No description")
                    print(f"   {i}. [{severity}] {issue}")
                if len(red_flags) > 5:
                    print(f"   ... and {len(red_flags) - 5} more")
            
            penalties = risk_analysis.get("penalties", [])
            if penalties:
                print(f"\n   Penalties ({len(penalties)}):")
                for i, penalty in enumerate(penalties[:3], 1):
                    ptype = penalty.get("type", "Unknown")
                    impact = penalty.get("impact", "No description")
                    print(f"   {i}. {ptype}: {impact[:60]}")
            
            obligations = risk_analysis.get("obligations", [])
            if obligations:
                print(f"\n   Obligations ({len(obligations)}):")
                for i, obl in enumerate(obligations[:3], 1):
                    task = obl.get("task", "No description")
                    print(f"   {i}. {task[:60]}")
            
            summary = risk_analysis.get("summary", "")
            if summary:
                print(f"\n   Summary:")
                print(f"   {summary[:200]}")
                if len(summary) > 200:
                    print("   ...")
        
        # Show final report preview
        if final_report:
            print(f"\n📋 Final Report Preview:")
            print("-" * 70)
            print(final_report[:500])
            if len(final_report) > 500:
                print("...")
            print("-" * 70)
        
        return {
            "success": True,
            "analysis_time": analysis_time,
            "risk_analysis": risk_analysis,
            "final_report": final_report
        }
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main validation workflow."""
    print_section("PDF PARSING & AGENT VALIDATION TOOL")
    
    # Check for PDF files
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ No 'uploads' directory found")
        print("   Creating sample PDF for testing...")
        
        # Create a test PDF
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "MASTER SERVICES AGREEMENT", fontsize=18)
        page.insert_text((72, 120), "1. TERM", fontsize=14)
        page.insert_text((72, 145), "This Agreement is effective for 12 months.", fontsize=11)
        page.insert_text((72, 180), "2. PAYMENT TERMS", fontsize=14)
        page.insert_text((72, 205), "Payment due within 30 days.", fontsize=11)
        page.insert_text((72, 240), "3. LIABILITY", fontsize=14)
        page.insert_text((72, 265), "Liability limited to fees paid.", fontsize=11)
        
        test_path = Path("test_contract.pdf")
        doc.save(test_path)
        doc.close()
        
        pdf_files = [test_path]
        print(f"✅ Created test PDF: {test_path}")
    else:
        pdf_files = list(uploads_dir.glob("*.pdf"))
        if not pdf_files:
            print("❌ No PDF files found in uploads directory")
            return
        
        print(f"📁 Found {len(pdf_files)} PDF files")
    
    # Select PDF to test
    if len(pdf_files) == 1:
        selected_pdf = pdf_files[0]
    else:
        print("\nAvailable PDFs:")
        for i, pdf in enumerate(pdf_files[:10], 1):
            size = pdf.stat().st_size
            print(f"  {i}. {pdf.name} ({size:,} bytes)")
        
        try:
            choice = input(f"\nSelect PDF (1-{min(len(pdf_files), 10)}) or press Enter for first: ").strip()
            if choice:
                selected_pdf = pdf_files[int(choice) - 1]
            else:
                selected_pdf = pdf_files[0]
        except (ValueError, IndexError):
            selected_pdf = pdf_files[0]
    
    # Validate parsing
    parse_results = validate_parsing(selected_pdf)
    
    # Ask if user wants to run agent analysis
    print("\n" + "=" * 70)
    run_agents = input("Run agent analysis? (y/N): ").strip().lower()
    
    if run_agents == 'y':
        parsed_text = parse_results["parsed"].text
        asyncio.run(validate_agent_analysis(parsed_text, selected_pdf.name))
    else:
        print("\n⏭️  Skipping agent analysis")
    
    print_section("VALIDATION COMPLETE")
    print("✅ PDF parsing validated successfully")
    
    if parse_results["found_terms"]:
        print(f"✅ Contract structure detected ({len(parse_results['found_terms'])} terms)")
    
    if parse_results["headers"]:
        print(f"✅ Document headers identified ({len(parse_results['headers'])} headers)")
    
    print("\n💡 Tips for improving parsing:")
    print("   - Ensure PDFs have selectable text (not scanned images)")
    print("   - Use extract_tables=True for documents with tables")
    print("   - Check that headers are properly formatted in source PDF")
    print("   - Review agent prompts to leverage layout information")


if __name__ == "__main__":
    main()


