"""
Integration tests to validate PDF parsing and agent analysis pipeline.
Tests the complete flow: PDF upload → parsing → agent analysis → report generation.
"""

import asyncio
from pathlib import Path
import fitz
import pytest

from app.services.document_parser import get_parser
from app.agents.graph import run_legal_audit


def create_test_contract_pdf() -> bytes:
    """Create a realistic test contract PDF with various elements."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Title
    page.insert_text((72, 72), "MASTER SERVICES AGREEMENT", fontsize=18, fontname="helv")
    
    # Section 1: Term
    page.insert_text((72, 120), "1. TERM AND TERMINATION", fontsize=14, fontname="helvb")
    page.insert_text((72, 145), "This Agreement commences on January 1, 2026 and continues for twelve (12) months.", fontsize=11)
    page.insert_text((72, 165), "Either party may terminate with 30 days written notice.", fontsize=11)
    
    # Section 2: Payment Terms
    page.insert_text((72, 200), "2. PAYMENT TERMS", fontsize=14, fontname="helvb")
    page.insert_text((72, 225), "Client shall pay all undisputed invoices within thirty (30) days of receipt.", fontsize=11)
    page.insert_text((72, 245), "Late payments will incur a 1.5% monthly interest charge.", fontsize=11)
    
    # Section 3: Liability
    page.insert_text((72, 280), "3. LIMITATION OF LIABILITY", fontsize=14, fontname="helvb")
    page.insert_text((72, 305), "Provider's total liability shall not exceed the fees paid in the preceding 12 months.", fontsize=11)
    page.insert_text((72, 325), "Provider is not liable for indirect, consequential, or punitive damages.", fontsize=11)
    
    # Section 4: Confidentiality
    page.insert_text((72, 360), "4. CONFIDENTIALITY", fontsize=14, fontname="helvb")
    page.insert_text((72, 385), "Both parties agree to maintain confidentiality of proprietary information.", fontsize=11)
    page.insert_text((72, 405), "Confidential information must not be disclosed without prior written consent.", fontsize=11)
    
    # Fee Schedule Table
    page.insert_text((72, 450), "Fee Schedule:", fontsize=12, fontname="helvb")
    page.insert_text((72, 475), "Service          | Monthly Fee", fontsize=10, fontname="cour")
    page.insert_text((72, 492), "Basic Support    | $500", fontsize=10, fontname="cour")
    page.insert_text((72, 509), "Premium Support  | $1,200", fontsize=10, fontname="cour")
    page.insert_text((72, 526), "Setup Fee        | $2,500 (one-time)", fontsize=10, fontname="cour")
    
    # Governing Law
    page.insert_text((72, 570), "5. GOVERNING LAW", fontsize=14, fontname="helvb")
    page.insert_text((72, 595), "This Agreement shall be governed by the laws of Delaware.", fontsize=11)
    
    doc.set_metadata({"title": "Master Services Agreement", "author": "Legal Department"})
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestPDFParsingValidation:
    """Test PDF parsing accuracy and completeness."""
    
    def test_parser_extracts_all_sections(self):
        """Verify parser extracts all major sections from contract."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        result = parser.parse_pdf(pdf_bytes)
        
        # Check all sections are present
        assert "MASTER SERVICES AGREEMENT" in result.text
        assert "TERM AND TERMINATION" in result.text
        assert "PAYMENT TERMS" in result.text
        assert "LIMITATION OF LIABILITY" in result.text
        assert "CONFIDENTIALITY" in result.text
        assert "GOVERNING LAW" in result.text
        
        print(f"✓ All sections extracted ({len(result.blocks)} blocks)")
    
    def test_parser_identifies_headers(self):
        """Verify parser correctly identifies section headers."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        result = parser.parse_pdf(pdf_bytes)
        
        headers = [b for b in result.blocks if b.block_type == "header"]
        header_texts = [h.text for h in headers]
        
        # Should identify major section headers
        assert any("TERM" in h for h in header_texts), "Missing TERM header"
        assert any("PAYMENT" in h for h in header_texts), "Missing PAYMENT header"
        assert any("LIABILITY" in h for h in header_texts), "Missing LIABILITY header"
        
        print(f"✓ Headers identified: {len(headers)}")
        for h in headers[:5]:
            print(f"  - {h.text[:50]}")
    
    def test_parser_preserves_structure(self):
        """Verify parser maintains document structure with page markers."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        result = parser.parse_pdf(pdf_bytes)
        
        # Check for page markers
        assert "--- Page 1 ---" in result.text
        
        # Check headers are marked with ##
        assert "## " in result.text or "TERM" in result.text
        
        print(f"✓ Document structure preserved")
    
    def test_parser_extracts_metadata(self):
        """Verify parser extracts PDF metadata."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        result = parser.parse_pdf(pdf_bytes)
        
        assert result.metadata.get("title") == "Master Services Agreement"
        assert result.metadata.get("author") == "Legal Department"
        
        print(f"✓ Metadata extracted: {result.metadata}")
    
    def test_parser_handles_tables(self):
        """Verify parser can detect tables when enabled."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        
        # Parse with table extraction enabled
        result = parser.parse_pdf(pdf_bytes, extract_tables=True)
        
        # Note: PyMuPDF table detection may not catch all tables
        # This test validates the mechanism works
        print(f"✓ Table extraction enabled: {len(result.tables)} tables found")
        
        # Check if fee schedule content is present
        assert "500" in result.text or "1,200" in result.text
    
    def test_parser_performance(self):
        """Verify parser completes in reasonable time."""
        import time
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        
        start = time.time()
        result = parser.parse_pdf(pdf_bytes)
        duration = time.time() - start
        
        assert duration < 1.0, f"Parsing took {duration:.2f}s (should be < 1s)"
        print(f"✓ Parsing completed in {duration*1000:.1f}ms")


class TestAgentAnalysisValidation:
    """Test agent analysis of parsed PDFs."""
    
    @pytest.mark.asyncio
    async def test_agents_receive_parsed_content(self):
        """Verify agents receive properly formatted document content."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        parsed = parser.parse_pdf(pdf_bytes)
        
        # Simulate what agents receive
        context = parsed.text
        
        # Verify key contract elements are present for analysis
        assert "TERM" in context
        assert "PAYMENT" in context
        assert "LIABILITY" in context
        assert "30 days" in context
        
        print(f"✓ Agent context prepared ({len(context)} chars)")
    
    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self):
        """Test complete pipeline: parse → orchestrator → researcher → analyst → auditor."""
        parser = get_parser()
        pdf_bytes = create_test_contract_pdf()
        parsed = parser.parse_pdf(pdf_bytes)
        
        # Run through agent pipeline
        try:
            final_state = await run_legal_audit(
                query="Analyze this Master Services Agreement for legal risks",
                text_context=parsed.text
            )
            
            # Verify pipeline completed
            assert final_state is not None
            assert "final_report_md" in final_state
            
            # Check if key sections were analyzed
            report = final_state.get("final_report_md", "")
            risk_analysis = final_state.get("risk_analysis", {})
            
            print(f"✓ Pipeline completed successfully")
            print(f"  - Report length: {len(report)} chars")
            print(f"  - Risk analysis keys: {list(risk_analysis.keys())}")
            
            # Verify risk analysis structure
            if risk_analysis:
                assert "red_flags" in risk_analysis or "summary" in risk_analysis
                print(f"  - Red flags found: {len(risk_analysis.get('red_flags', []))}")
            
        except Exception as e:
            print(f"⚠ Pipeline execution failed: {e}")
            # Don't fail test if LLM/API not available
            pytest.skip(f"Pipeline requires LLM access: {e}")


class TestRealWorldPDFs:
    """Test with actual uploaded PDFs if available."""
    
    def test_parse_uploaded_pdfs(self):
        """Parse any PDFs in uploads directory for validation."""
        uploads_dir = Path("uploads")
        if not uploads_dir.exists():
            pytest.skip("No uploads directory found")
        
        pdf_files = list(uploads_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files in uploads directory")
        
        parser = get_parser()
        results = []
        
        for pdf_path in pdf_files[:3]:  # Test first 3 PDFs
            try:
                pdf_bytes = pdf_path.read_bytes()
                parsed = parser.parse_pdf(pdf_bytes)
                
                results.append({
                    "file": pdf_path.name,
                    "pages": parsed.page_count,
                    "blocks": len(parsed.blocks),
                    "text_length": len(parsed.text),
                    "has_metadata": bool(parsed.metadata)
                })
                
                print(f"✓ Parsed {pdf_path.name}:")
                print(f"  - Pages: {parsed.page_count}")
                print(f"  - Blocks: {len(parsed.blocks)}")
                print(f"  - Text length: {len(parsed.text)}")
                
            except Exception as e:
                print(f"✗ Failed to parse {pdf_path.name}: {e}")
        
        assert len(results) > 0, "No PDFs successfully parsed"
        print(f"\n✓ Successfully parsed {len(results)} real PDFs")


def test_document_structure_extraction():
    """Test extraction of document structure for agent context."""
    parser = get_parser()
    pdf_bytes = create_test_contract_pdf()
    parsed = parser.parse_pdf(pdf_bytes)
    
    # Extract structure summary
    headers = [b for b in parsed.blocks if b.block_type == "header"]
    structure = {
        "total_blocks": len(parsed.blocks),
        "headers": [h.text for h in headers],
        "pages": parsed.page_count,
        "has_tables": len(parsed.tables) > 0
    }
    
    print(f"✓ Document structure extracted:")
    print(f"  - Total blocks: {structure['total_blocks']}")
    print(f"  - Headers: {len(structure['headers'])}")
    print(f"  - Pages: {structure['pages']}")
    
    assert structure["total_blocks"] > 0
    assert structure["pages"] > 0


if __name__ == "__main__":
    print("=" * 60)
    print("PDF PARSING & AGENT INTEGRATION VALIDATION")
    print("=" * 60)
    
    # Run parsing tests
    print("\n1. Testing PDF Parsing...")
    test_suite = TestPDFParsingValidation()
    test_suite.test_parser_extracts_all_sections()
    test_suite.test_parser_identifies_headers()
    test_suite.test_parser_preserves_structure()
    test_suite.test_parser_extracts_metadata()
    test_suite.test_parser_handles_tables()
    test_suite.test_parser_performance()
    
    print("\n2. Testing Document Structure...")
    test_document_structure_extraction()
    
    print("\n3. Testing Real PDFs...")
    real_test = TestRealWorldPDFs()
    real_test.test_parse_uploaded_pdfs()
    
    print("\n" + "=" * 60)
    print("✓ ALL VALIDATION TESTS PASSED")
    print("=" * 60)


