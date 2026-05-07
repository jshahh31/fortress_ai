import io
from pathlib import Path

import fitz
import pytest

from app.services.document_parser import get_parser

REAL_PDF = Path(r"C:\Users\Sunny\Downloads\med_dir_actualcontract.pdf")


def _make_large_pdf_bytes(page_count: int = 20) -> bytes:
    doc = fitz.open()
    for i in range(page_count):
        page = doc.new_page()
        page.insert_text((72, 72), f"Sample Contract Page {i + 1}", fontsize=14)
        page.insert_text((72, 100), "This agreement contains obligations, payment terms, and liabilities.", fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _pdf_bytes() -> bytes:
    if REAL_PDF.exists():
        return REAL_PDF.read_bytes()
    return _make_large_pdf_bytes()


# ── PyMuPDF (no table detection — default fast path) ─────────

@pytest.mark.benchmark(group="parsers")
def test_pymupdf_performance(benchmark):
    parser = get_parser()
    pdf_bytes = _pdf_bytes()

    result = benchmark(parser._parse_with_pymupdf, pdf_bytes, False)

    assert result.page_count > 0
    assert len(result.blocks) > 0


# ── PyMuPDF (with table detection) ───────────────────────────

@pytest.mark.benchmark(group="parsers")
def test_pymupdf_with_tables_performance(benchmark):
    parser = get_parser()
    pdf_bytes = _pdf_bytes()

    result = benchmark(parser._parse_with_pymupdf, pdf_bytes, True)

    assert result.page_count > 0


# ── PyPDF2 ───────────────────────────────────────────────────

@pytest.mark.benchmark(group="parsers")
def test_pypdf2_performance(benchmark):
    parser = get_parser()
    pdf_bytes = _pdf_bytes()

    result = benchmark(parser._parse_with_pypdf2, pdf_bytes)

    assert result.page_count > 0
