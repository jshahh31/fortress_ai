import fitz
import pytest

from app.services.document_parser import ParsedDocument, TableData, get_parser


def _make_pdf_bytes(*lines: tuple[str, float]) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for text, size in lines:
        page.insert_text((72, y), text, fontsize=size)
        y += max(18, int(size) + 6)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_singleton_pattern():
    assert get_parser() is get_parser()


def test_parse_pdf_returns_parsed_document():
    parser = get_parser()
    result = parser.parse_pdf(_make_pdf_bytes(("Agreement", 16), ("Body clause", 11)))
    assert isinstance(result, ParsedDocument)


def test_parse_pdf_extracts_text_and_blocks():
    parser = get_parser()
    result = parser.parse_pdf(_make_pdf_bytes(("Master Services Agreement", 16), ("Payment terms apply.", 11)))

    assert "Master Services Agreement" in result.text
    assert "Payment terms apply." in result.text
    assert result.page_count == 1
    assert len(result.blocks) >= 1


def test_parse_pdf_extracts_metadata():
    parser = get_parser()

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Title Block", fontsize=14)
    doc.set_metadata({"title": "Sample Contract"})
    pdf_bytes = doc.tobytes()
    doc.close()

    result = parser.parse_pdf(pdf_bytes)
    assert result.metadata.get("title") == "Sample Contract"


def test_block_classification_header_detection():
    parser = get_parser()
    result = parser.parse_pdf(_make_pdf_bytes(("TERMINATION", 18), ("Either party may terminate.", 10)))

    header_blocks = [b for b in result.blocks if b.block_type == "header"]
    assert header_blocks
    assert any("TERMINATION" in b.text for b in header_blocks)


def test_table_formatting():
    parser = get_parser()
    tables = [
        TableData(
            bbox=(0.0, 0.0, 100.0, 100.0),
            rows=[["Fee", "Amount"], ["Setup", "$500"]],
            page_num=1,
            col_count=2,
            row_count=2,
        )
    ]

    formatted = parser._format_tables(tables)
    assert "Table 1" in formatted
    assert "Fee | Amount" in formatted


def test_fallback_to_pypdf2(monkeypatch):
    parser = get_parser()
    expected = ParsedDocument(text="fallback", blocks=[], tables=[], metadata={}, page_count=1)

    def _raise(_):
        raise RuntimeError("boom")

    def _fallback(_):
        return expected

    monkeypatch.setattr("app.services.document_parser.settings.USE_PYMUPDF", True)
    monkeypatch.setattr(parser, "_parse_with_pymupdf", _raise)
    monkeypatch.setattr(parser, "_parse_with_pypdf2", _fallback)

    result = parser.parse_pdf(b"dummy")
    assert result is expected
