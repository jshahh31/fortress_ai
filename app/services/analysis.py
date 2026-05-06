"""
Analysis pipeline service.

Orchestrates a multi-step legal contract audit:
  1. Document Parsing (extract text structure)
  2. Clause Extraction (identify key clauses & entities)
  3. Risk Analysis (evaluate each clause for risk)
  4. Report Generation (synthesize final report)

Each step streams SSE progress events to the frontend.
Uses Qwen for extraction/analysis, Kimi for report synthesis.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import AsyncGenerator

from app.services import llm

logger = logging.getLogger(__name__)

# ─── System prompts for each pipeline stage ─────────────────

SYSTEM_PARSING = """You are an expert legal document parser. Carefully read the ENTIRE contract text provided and extract:

1. Document type: Identify the specific type (e.g., "Employment Agreement", "Lease Agreement", "NDA", "Service Agreement", "Vendor Agreement")
2. Parties: Extract ALL party names, roles, and addresses mentioned in the document
3. Key dates: Find effective date, expiration date, renewal dates, notice periods
4. Document structure: Identify all section numbers, headings, and clause references

IMPORTANT:
- Only extract information that is EXPLICITLY stated in the document
- If information is not present, use null or empty values
- Do not make assumptions or generate placeholder data
- Quote exact text when identifying parties and dates

Return ONLY a valid JSON object with this exact structure:
{
  "document_type": "string",
  "parties": [{"name": "string", "role": "string", "address": "string"}],
  "effective_date": "string or null",
  "expiration_date": "string or null",
  "key_dates": {"date_type": "date_value"},
  "sections": [{"number": "string", "title": "string"}]
}"""

# If the provided text does not contain contract substance, return ONLY:
# {"error":"INSUFFICIENT_DOCUMENT_TEXT","reason":"string"}

SYSTEM_EXTRACTION = """You are an expert legal clause extraction AI. You will receive the FULL TEXT of a legal document.

Your task: Extract ALL significant clauses with their EXACT text from the document.

Focus on these clause types:
1. Obligations and responsibilities of each party
2. Payment terms and pricing
3. Termination and cancellation conditions
4. Liability limitations and disclaimers
5. Confidentiality and non-disclosure provisions
6. Indemnification and penalty clauses
7. Intellectual property rights
8. Dispute resolution and governing law
9. Warranties and representations
10. Force majeure and other risk allocation

CRITICAL RULES:
- Extract the ACTUAL TEXT of each clause (not summaries)
- Include the exact section number/reference where found
- Only extract clauses that EXIST in the document
- If a clause type is not present, omit it from the output
- Do not generate hypothetical or template clauses

Return ONLY valid JSON:
{
  "clauses": [
    {
      "clause_name": "string",
      "section": "string",
      "full_text": "exact quoted text from document",
      "parties_affected": ["Party A", "Party B"],
      "clause_type": "obligation|payment|termination|liability|confidentiality|indemnification|ip|dispute|warranty|other"
    }
  ]
}"""

# If no real clauses are present in the source text, return ONLY:
# {"clauses": []}

SYSTEM_RISK = """You are a senior legal risk assessor. Analyze the extracted clauses for potential risks and unfavorable terms.

For EACH clause provided, assess:
1. Risk level: critical, high, medium, or low
2. WHY it poses a risk (be specific about the actual terms)
3. What could go wrong for the user
4. How it compares to industry standards
5. Concrete suggestions for negotiation

CRITICAL RULES:
- Base your assessment ONLY on the actual clause text provided
- Do not assess clauses that weren't extracted
- Be specific about which party is disadvantaged
- Identify one-sided or unfair terms
- Flag missing protections that should be present

Return ONLY valid JSON:
{
  "verdict": "SIGN|NEGOTIATE|REJECT|SEEK_COUNSEL",
  "overall_risk_score": 0-100,
  "risk_summary": "2-3 sentence overview",
  "risk_matrix": {
    "critical": [{"clause_name": "string", "section": "string", "risk_description": "string", "impact": "string", "recommendation": "string"}],
    "high": [...],
    "medium": [...],
    "low": [...]
  },
  "red_flags": [{"title": "string", "description": "string", "section": "string", "severity": "critical|high"}],
  "missing_protections": ["string"]
}"""

# If there are no clauses to assess, return ONLY:
# {"error":"NO_CLAUSES_TO_ANALYZE","reason":"string"}

SYSTEM_REPORT = """You are a senior legal report writer. Synthesize all analysis findings into a professional Contract Risk Assessment Report. 

The report should be written in clear, professional language suitable for both attorneys and individuals. Include:
1. Executive Summary (2-3 paragraphs)
2. Key findings and their implications
3. Specific recommendations tailored to the user's role
4. Action items prioritized by urgency

Write in markdown format. Be thorough but concise. Highlight critical issues prominently.

CRITICAL WRITING RULES:
- Use precise, non-repetitive language
- Do not output filler, word salad, or repeated tokens
- Keep the total report under 450 words
- Base all claims only on parsed/extracted/risk data provided"""


# ─── Pipeline orchestrator ──────────────────────────────────

async def run_pipeline(
    text: str,
    contract_type: str | None = None,
    user_type: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Run the full audit pipeline, yielding SSE events for each step.

    Event format (newline-delimited JSON):
        {"event": "step_update", "data": {"step_id": "...", "status": "processing"}}
        {"event": "content_chunk", "data": {"chunk": "...", "step_id": "report"}}
        {"event": "done", "data": {}}
    """

    steps = [
        {"id": "parsing", "label": "Document Parsing", "description": "Analyzing document structure and metadata"},
        {"id": "extraction", "label": "Clause Extraction", "description": "Identifying key clauses and obligations"},
        {"id": "risk", "label": "Risk Analysis", "description": "Evaluating risk levels for each clause"},
        {"id": "report", "label": "Report Generation", "description": "Synthesizing final assessment report"},
    ]

    # Emit initial step list
    yield _sse({"event": "steps_init", "data": {"steps": steps}})

    context_suffix = ""
    if contract_type:
        context_suffix += f"\nContract Type: {contract_type}"
    if user_type:
        context_suffix += f"\nUser Role: {user_type}"

    # ── Step 1: Document Parsing ─────────────────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "parsing", "status": "processing"}})
    try:
        parsed_raw = await llm.generate(
            prompt=f"Parse this legal document:\n\n{text}{context_suffix}",
            system_prompt=SYSTEM_PARSING,
            temperature=0.1,
            max_tokens=2000,
        )
        parsed_json = _parse_json_response(parsed_raw)

        if _is_insufficient_document(parsed_json):
            raise ValueError("Insufficient document text detected for structured parsing")

        if not _looks_like_contract_document(parsed_json):
            raise ValueError(
                "Uploaded document does not appear to be a contract/agreement. "
                "Please upload a contract (e.g., NDA, MSA, SOW, Vendor Agreement, Lease)."
            )

        parsed = json.dumps(parsed_json, indent=2)
        yield _sse({"event": "content_chunk", "data": {"chunk": parsed, "step_id": "parsing"}})
        
        yield _sse({"event": "step_update", "data": {"step_id": "parsing", "status": "completed"}})
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "parsing", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Document parsing failed: {str(e)}"}})
        return

    # ── Step 2: Clause Extraction ────────────────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "processing"}})
    try:
        extracted_raw = await llm.generate(
            prompt=f"FULL DOCUMENT TEXT:\n\n{text}\n\n---\n\nParsed metadata for context:\n{parsed}{context_suffix}",
            system_prompt=SYSTEM_EXTRACTION,
            temperature=0.1,
            max_tokens=3000,
        )
        extracted_json = _parse_json_response(extracted_raw)

        if _has_no_usable_clauses(extracted_json):
            raise ValueError(
                "No contract clauses could be extracted from this document. "
                "Please upload a complete contract with clause text."
            )

        extracted = json.dumps(extracted_json, indent=2)
        yield _sse({"event": "content_chunk", "data": {"chunk": extracted, "step_id": "extraction"}})
            
        yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "completed"}})
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Clause extraction failed: {str(e)}"}})
        return

    # ── Step 3: Risk Analysis ────────────────────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "risk", "status": "processing"}})
    try:
        risk_raw = await llm.generate(
            prompt=f"Assess risks in these extracted clauses:\n\n{extracted}",
            system_prompt=SYSTEM_RISK,
            temperature=0.1,
            max_tokens=2500,
        )
        risk_json = _parse_json_response(risk_raw)
        risk_analysis = json.dumps(risk_json, indent=2)
        yield _sse({"event": "content_chunk", "data": {"chunk": risk_analysis, "step_id": "risk"}})
            
        yield _sse({"event": "step_update", "data": {"step_id": "risk", "status": "completed"}})
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "risk", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Risk analysis failed: {str(e)}"}})
        return

    # ── Step 4: Report Generation (streamed) ─────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "report", "status": "processing"}})
    try:
        report_prompt = (
            f"Write a comprehensive Contract Risk Assessment Report.\n\n"
            f"Parsed Document:\n{parsed}\n\n"
            f"Extracted Clauses:\n{extracted}\n\n"
            f"Risk Assessment:\n{risk_analysis}"
        )
        if user_type:
            report_prompt += f"\n\nTailor recommendations for: {user_type}"

        async for chunk in llm.stream(
            prompt=report_prompt,
            system_prompt=SYSTEM_REPORT,
            temperature=0.3,
        ):
            yield _sse({"event": "content_chunk", "data": {"chunk": chunk, "step_id": "report"}})

        yield _sse({"event": "step_update", "data": {"step_id": "report", "status": "completed"}})
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "report", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Report generation failed: {str(e)}"}})
        return

    # ── Done ─────────────────────────────────────────────────
    yield _sse({"event": "done", "data": {"risk_analysis": risk_analysis}})


def _sse(payload: dict) -> str:
    """Format a dict as an SSE data line."""
    return f"data: {json.dumps(payload)}\n\n"


def _parse_json_response(raw: str) -> dict:
    """Parse model output as JSON, tolerating fenced blocks and minor wrappers."""
    text = (raw or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Fast path
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Fallback: extract outermost object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response does not contain a valid JSON object")

    parsed = json.loads(text[start:end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Model JSON response is not an object")
    return parsed


def _is_insufficient_document(parsed: dict) -> bool:
    """Heuristic guard for 'no real document text' parsing outcomes."""
    if parsed.get("error") == "INSUFFICIENT_DOCUMENT_TEXT":
        return True

    sections = parsed.get("sections") or []
    parties = parsed.get("parties") or []
    key_dates = parsed.get("key_dates") or {}
    doc_type = (parsed.get("document_type") or "").strip().lower()

    if not sections and not key_dates and len(parties) <= 1 and doc_type in {"", "other", "vendor_agreement"}:
        return True
    return False


def _looks_like_contract_document(parsed: dict) -> bool:
    """Allow only contract-like document types for this contract audit pipeline."""
    doc_type = (parsed.get("document_type") or "").strip().lower()
    if not doc_type:
        return False

    contract_markers = (
        "agreement",
        "contract",
        "nda",
        "lease",
        "msa",
        "sow",
        "statement of work",
        "service",
        "vendor",
        "license",
        "employment",
        "subscription",
        "purchase",
    )

    return any(marker in doc_type for marker in contract_markers)


def _has_no_usable_clauses(extracted: dict) -> bool:
    """Return True when extraction does not contain meaningful clause entries."""
    clauses = extracted.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        return True

    usable = 0
    for clause in clauses:
        if not isinstance(clause, dict):
            continue
        full_text = (clause.get("full_text") or "").strip()
        if len(full_text) >= 20:
            usable += 1

    return usable == 0
