from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple


@dataclass
class Section:
    """A referenceable document section."""

    number: str
    title: str
    level: int
    page_num: int
    content: str = ""
    clause_type: str = "general"
    start_block_index: int = -1
    end_block_index: int = -1


class DocumentStructureBuilder:
    """Build a section hierarchy and clause index from parsed document blocks."""

    _NUMBERED_SECTION_PATTERN = re.compile(
        r"^\s*((?:\d+\.)*\d+)\s*(?:[\)\-:]|\.)?\s+(.+?)\s*$"
    )
    _UPPER_HEADER_PATTERN = re.compile(r"^[A-Z][A-Z\s/&\-]{2,}$")

    _CLAUSE_KEYWORDS: Dict[str, Tuple[str, ...]] = {
        "payment": ("payment", "fee", "invoice", "billing", "compensation"),
        "termination": ("termination", "terminate", "cure period", "breach"),
        "liability": ("liability", "indemn", "damages", "limitation"),
        "confidentiality": ("confidential", "non-disclosure", "nda", "privacy"),
        "compliance": ("compliance", "regulation", "gdpr", "hipaa", "sox", "law"),
        "security": ("security", "cyber", "encryption", "incident", "access control"),
        "governing_law": ("governing law", "jurisdiction", "venue", "arbitration"),
        "ip": ("intellectual property", "ip", "ownership", "license", "copyright"),
    }

    def build(
        self, blocks: Sequence[Any]
    ) -> Tuple[List[Section], Dict[str, Section], Dict[str, Any]]:
        sections = self.extract_sections(blocks)
        section_map = self._build_section_map(sections)
        structure = {
            "hierarchy": self._build_hierarchy(sections),
            "key_clauses": self._build_key_clause_index(sections),
            "section_count": len(sections),
        }
        return sections, section_map, structure

    def extract_sections(self, blocks: Sequence[Any]) -> List[Section]:
        """Extract section headings and associate them with source pages."""
        sections: List[Section] = []
        seen_keys: set[Tuple[str, str]] = set()

        for block_index, block in enumerate(blocks):
            raw_text = (getattr(block, "text", "") or "").strip()
            if not raw_text:
                continue

            parsed = self._parse_heading(
                text=raw_text,
                block_type=(getattr(block, "block_type", "text") or "text"),
                section_index=len(sections) + 1,
            )
            if parsed is None:
                continue

            number, title, level = parsed
            dedupe_key = (number.lower(), title.lower())
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            sections.append(
                Section(
                    number=number,
                    title=title,
                    level=level,
                    page_num=int(getattr(block, "page_num", 0) or 0),
                    start_block_index=block_index,
                    end_block_index=block_index,
                )
            )

        self._populate_section_content(sections, blocks)
        return sections

    def _parse_heading(self, text: str, block_type: str, section_index: int) -> Tuple[str, str, int] | None:
        numbered_match = self._NUMBERED_SECTION_PATTERN.match(text)
        if numbered_match is None and ("." in text or ";" in text):
            # Some PDFs merge adjacent lines into one block; recover trailing section markers.
            fragments = re.split(r"(?<=[\.;])\s+", text)
            for fragment in reversed(fragments):
                numbered_match = self._NUMBERED_SECTION_PATTERN.match(fragment.strip())
                if numbered_match:
                    break

        if numbered_match:
            number = numbered_match.group(1).strip().rstrip(".")
            title = numbered_match.group(2).strip()
            if title:
                return number, title, number.count(".") + 1

        is_header = block_type == "header"
        is_upper = bool(self._UPPER_HEADER_PATTERN.match(text))
        short_enough = len(text) <= 140
        sentence_like = "." in text and not text.isupper()
        if (is_header or is_upper) and short_enough and not sentence_like:
            synthetic = f"H{section_index}"
            return synthetic, text, 1

        return None

    def _populate_section_content(self, sections: List[Section], blocks: Sequence[Any]) -> None:
        if not sections:
            return

        for idx, section in enumerate(sections):
            start = section.start_block_index + 1
            next_start = sections[idx + 1].start_block_index if idx + 1 < len(sections) else len(blocks)
            if start >= next_start:
                section.content = ""
                section.end_block_index = section.start_block_index
            else:
                content_lines = [
                    (getattr(blocks[i], "text", "") or "").strip()
                    for i in range(start, next_start)
                    if (getattr(blocks[i], "text", "") or "").strip()
                ]
                section.content = "\n".join(content_lines).strip()
                section.end_block_index = max(start, next_start - 1)

            section.clause_type = self._identify_clause_type(section.title, section.content)

    def _identify_clause_type(self, title: str, content: str) -> str:
        haystack = f"{title} {content}".lower()
        for clause_type, keywords in self._CLAUSE_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return clause_type
        return "general"

    def _build_section_map(self, sections: Sequence[Section]) -> Dict[str, Section]:
        section_map: Dict[str, Section] = {}
        for section in sections:
            section_map[section.number] = section
            section_map[section.number.lower()] = section
            section_map[section.title.lower()] = section
            if section.number and section.number.upper().startswith("H") is False:
                section_map[f"section {section.number}".lower()] = section
        return section_map

    def _build_hierarchy(self, sections: Sequence[Section]) -> List[Dict[str, Any]]:
        roots: List[Dict[str, Any]] = []
        stack: List[Dict[str, Any]] = []

        for section in sections:
            node: Dict[str, Any] = {
                "number": section.number,
                "title": section.title,
                "page_num": section.page_num,
                "level": section.level,
                "clause_type": section.clause_type,
                "children": [],
            }

            while stack and stack[-1]["level"] >= section.level:
                stack.pop()

            if stack:
                stack[-1]["children"].append(node)
            else:
                roots.append(node)

            stack.append(node)

        return roots

    def _build_key_clause_index(self, sections: Sequence[Section]) -> Dict[str, List[str]]:
        key_clauses: Dict[str, List[str]] = {}
        for section in sections:
            if section.clause_type == "general":
                continue

            reference = f"{section.number} {section.title} (p.{section.page_num})"
            key_clauses.setdefault(section.clause_type, []).append(reference)

        return key_clauses
