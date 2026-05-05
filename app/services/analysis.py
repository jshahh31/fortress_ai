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

SYSTEM_PARSING = """You are an expert legal document parser. Analyze the provided contract text and extract:
1. Document type (lease, employment, NDA, etc.)
2. Parties involved (names, roles)
3. Key dates (effective date, expiration, renewal)
4. Document structure (sections, clauses numbering)

Return your analysis as a well-structured JSON object."""

SYSTEM_EXTRACTION = """You are an expert legal clause extraction AI. Given a parsed legal document, identify and extract:
1. All significant clauses with their section references
2. Key obligations for each party
3. Termination conditions
4. Liability limitations
5. Confidentiality provisions
6. Penalty/indemnification clauses
7. Governing law and jurisdiction

Return a JSON object with arrays of extracted clauses, each having: clause_name, section, text, parties_affected, obligation_type."""

SYSTEM_RISK = """You are a senior legal risk assessor. Evaluate the extracted clauses and provide:
1. Risk level for each clause: critical, high, medium, or low
2. Description of why the clause is risky
3. Suggestion for improvement
4. Industry standard comparison
5. Red flags that need immediate attention

Return a comprehensive JSON risk assessment with:
- verdict: "SIGN", "NEGOTIATE", "REJECT", or "SEEK_COUNSEL"
- risk_matrix: { critical: [...], high: [...], medium: [...], low: [...] }
- red_flags: [{ title, description, section, severity }]
- overall_risk_score: 0-100"""

SYSTEM_REPORT = """You are a senior legal report writer. Synthesize all analysis findings into a professional Contract Risk Assessment Report. 

The report should be written in clear, professional language suitable for both attorneys and individuals. Include:
1. Executive Summary (2-3 paragraphs)
2. Key findings and their implications
3. Specific recommendations tailored to the user's role
4. Action items prioritized by urgency

Write in markdown format. Be thorough but concise. Highlight critical issues prominently."""


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
        parsed = ""
        async for chunk in llm.stream(
            prompt=f"Parse this legal document:\n\n{text}{context_suffix}",
            system_prompt=SYSTEM_PARSING,
            temperature=0.3,
        ):
            parsed += chunk
            yield _sse({"event": "content_chunk", "data": {"chunk": chunk, "step_id": "parsing"}})
        
        yield _sse({"event": "step_update", "data": {"step_id": "parsing", "status": "completed"}})
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "parsing", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Document parsing failed: {str(e)}"}})
        return

    # ── Step 2: Clause Extraction ────────────────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "processing"}})
    try:
        extracted = ""
        async for chunk in llm.stream(
            prompt=f"Extract clauses from this parsed document:\n\n{parsed}",
            system_prompt=SYSTEM_EXTRACTION,
            temperature=0.3,
        ):
            extracted += chunk
            yield _sse({"event": "content_chunk", "data": {"chunk": chunk, "step_id": "extraction"}})
            
        yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "completed"}})
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        yield _sse({"event": "step_update", "data": {"step_id": "extraction", "status": "error"}})
        yield _sse({"event": "error", "data": {"message": f"Clause extraction failed: {str(e)}"}})
        return

    # ── Step 3: Risk Analysis ────────────────────────────────
    yield _sse({"event": "step_update", "data": {"step_id": "risk", "status": "processing"}})
    try:
        risk_analysis = ""
        async for chunk in llm.stream(
            prompt=f"Assess risks in these extracted clauses:\n\n{extracted}",
            system_prompt=SYSTEM_RISK,
            temperature=0.3,
        ):
            risk_analysis += chunk
            yield _sse({"event": "content_chunk", "data": {"chunk": chunk, "step_id": "risk"}})
            
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
            temperature=0.6,
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
