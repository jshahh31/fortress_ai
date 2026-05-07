import fitz
import pytest

from app.services.document_parser import get_parser


def _make_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "SERVICE AGREEMENT", fontsize=16)
    page.insert_text((72, 100), "Payment due within 30 days.", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.mark.asyncio
async def test_upload_pdf_with_pymupdf():
    parser = get_parser()
    result = parser.parse_pdf(_make_pdf_bytes())
    assert "SERVICE AGREEMENT" in result.text


@pytest.mark.asyncio
async def test_upload_preserves_layout_markers():
    parser = get_parser()
    result = parser.parse_pdf(_make_pdf_bytes())
    assert "--- Page 1 ---" in result.text


@pytest.mark.asyncio
async def test_upload_handles_invalid_pdf_bytes():
    parser = get_parser()
    result = parser.parse_pdf(b"not-a-pdf")
    assert result.page_count == 0 or result.text == ""
