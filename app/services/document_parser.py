from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DocumentBlock:
    """A text block with basic layout information."""

    text: str
    block_type: str
    bbox: Tuple[float, float, float, float]
    page_num: int
    font_size: float
    is_bold: bool


@dataclass
class TableData:
    """Extracted table data from a page."""

    bbox: Tuple[float, float, float, float]
    rows: List[List[str]]
    page_num: int
    col_count: int
    row_count: int


@dataclass
class ParsedDocument:
    """Complete document parse result."""

    text: str
    blocks: List[DocumentBlock]
    tables: List[TableData]
    metadata: Dict[str, Any]
    page_count: int


class DocumentParser:
    """Hybrid PDF parser with PyMuPDF primary and PyPDF2 fallback."""

    def parse_pdf(self, pdf_bytes: bytes, extract_tables: bool = False) -> ParsedDocument:
        if settings.USE_PYMUPDF:
            try:
                return self._parse_with_pymupdf(pdf_bytes, extract_tables=extract_tables)
            except Exception as exc:
                logger.warning("PyMuPDF parse failed, falling back to PyPDF2: %s", exc)

        return self._parse_with_pypdf2(pdf_bytes)

    def _parse_with_pymupdf(self, pdf_bytes: bytes, extract_tables: bool = False) -> ParsedDocument:
        import fitz

        blocks: List[DocumentBlock] = []
        tables: List[TableData] = []
        text_parts: List[str] = []

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            metadata = dict(doc.metadata or {})
            page_count = doc.page_count

            for page_index in range(page_count):
                page = doc.load_page(page_index)
                page_num = page_index + 1

                text_parts.append(f"--- Page {page_num} ---")
                page_dict = page.get_text("dict")

                for raw_block in page_dict.get("blocks", []):
                    if raw_block.get("type") != 0:
                        continue

                    block_text, font_size, is_bold = self._extract_block_text(raw_block)
                    block_text = block_text.strip()
                    if not block_text:
                        continue

                    bbox = tuple(raw_block.get("bbox", (0.0, 0.0, 0.0, 0.0)))
                    block_type = self._classify_block(block_text, font_size, is_bold)
                    block = DocumentBlock(
                        text=block_text,
                        block_type=block_type,
                        bbox=bbox,
                        page_num=page_num,
                        font_size=font_size,
                        is_bold=is_bold,
                    )
                    blocks.append(block)

                    if block_type == "header":
                        text_parts.append(f"## {block_text}")
                    else:
                        text_parts.append(block_text)

                if extract_tables:
                    detected_tables = self._extract_tables(page, page_num)
                    tables.extend(detected_tables)

            if tables:
                text_parts.append("")
                text_parts.append("=== TABLES DETECTED ===")
                text_parts.append(self._format_tables(tables))

        return ParsedDocument(
            text="\n\n".join(part for part in text_parts if part.strip()),
            blocks=blocks,
            tables=tables,
            metadata=metadata,
            page_count=page_count,
        )

    def _parse_with_pypdf2(self, pdf_bytes: bytes) -> ParsedDocument:
        try:
            import PyPDF2
        except ImportError:
            return ParsedDocument(
                text="",
                blocks=[],
                tables=[],
                metadata={},
                page_count=0,
            )

        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        except Exception as exc:
            logger.warning("PyPDF2 fallback parse failed: %s", exc)
            return ParsedDocument(
                text="",
                blocks=[],
                tables=[],
                metadata={},
                page_count=0,
            )

        text_parts: List[str] = []
        blocks: List[DocumentBlock] = []

        for page_index, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue

            page_num = page_index + 1
            text_parts.append(f"--- Page {page_num} ---")
            text_parts.append(page_text)
            blocks.append(
                DocumentBlock(
                    text=page_text,
                    block_type="text",
                    bbox=(0.0, 0.0, 0.0, 0.0),
                    page_num=page_num,
                    font_size=0.0,
                    is_bold=False,
                )
            )

        metadata = dict(getattr(reader, "metadata", {}) or {})
        return ParsedDocument(
            text="\n\n".join(text_parts),
            blocks=blocks,
            tables=[],
            metadata=metadata,
            page_count=len(reader.pages),
        )

    @staticmethod
    def _extract_block_text(raw_block: Dict[str, Any]) -> Tuple[str, float, bool]:
        lines = raw_block.get("lines", [])
        parts: List[str] = []
        font_sizes: List[float] = []
        has_bold = False

        for line in lines:
            for span in line.get("spans", []):
                text = (span.get("text") or "").strip()
                if text:
                    parts.append(text)

                size = float(span.get("size", 0.0) or 0.0)
                if size > 0:
                    font_sizes.append(size)

                font_name = (span.get("font") or "").lower()
                if "bold" in font_name:
                    has_bold = True

        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0.0
        return " ".join(parts), avg_font_size, has_bold

    @staticmethod
    def _classify_block(text: str, font_size: float, is_bold: bool) -> str:
        short_line = len(text) <= 140
        likely_header = short_line and (font_size >= 12.0 or is_bold)
        return "header" if likely_header else "text"

    @staticmethod
    def _extract_tables(page: Any, page_num: int) -> List[TableData]:
        table_data: List[TableData] = []
        try:
            table_finder = page.find_tables()
            found_tables = getattr(table_finder, "tables", [])
            for table in found_tables:
                rows = table.extract() or []
                if not rows:
                    continue
                row_count = len(rows)
                col_count = max((len(r) for r in rows), default=0)
                bbox = tuple(getattr(table, "bbox", (0.0, 0.0, 0.0, 0.0)))
                table_data.append(
                    TableData(
                        bbox=bbox,
                        rows=[[cell or "" for cell in row] for row in rows],
                        page_num=page_num,
                        col_count=col_count,
                        row_count=row_count,
                    )
                )
        except Exception as exc:
            logger.debug("Table extraction failed on page %s: %s", page_num, exc)

        return table_data

    @staticmethod
    def _format_tables(tables: List[TableData]) -> str:
        sections: List[str] = []
        for idx, table in enumerate(tables, start=1):
            sections.append(
                f"Table {idx} (page {table.page_num}, rows={table.row_count}, cols={table.col_count})"
            )
            for row in table.rows:
                sections.append(" | ".join(cell.strip() for cell in row))
            sections.append("")
        return "\n".join(sections).strip()


_parser: DocumentParser | None = None


def get_parser() -> DocumentParser:
    global _parser
    if _parser is None:
        _parser = DocumentParser()
    return _parser
