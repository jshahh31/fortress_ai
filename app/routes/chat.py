"""Chat routes — send messages, stream responses, upload files."""

from __future__ import annotations

import json
import uuid
import logging
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, Response
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, FileUploadResponse
from app.db.store import store
from app.services import llm
from app.services.analysis import run_pipeline
from app.services.export_service import generate_docx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# ─── File Export ─────────────────────────────────────────────

@router.get("/export/{conversation_id}")
async def export_conversation(
    conversation_id: str,
    format: str = Query("docx", enum=["pdf", "docx"]),
):
    """Export the conversation report as PDF or DOCX."""
    
    if format == "docx":
        file_stream = await generate_docx(conversation_id)
        if not file_stream:
            raise HTTPException(status_code=404, detail="Could not generate DOCX. Ensure a report exists.")
            
        filename = f"Fortress_AI_Report_{conversation_id[:8]}.docx"
        return Response(
            content=file_stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    elif format == "pdf":
        # Placeholder since we don't have a PDF generator
        raise HTTPException(
            status_code=501, 
            detail="PDF export is currently being upgraded. Please use DOCX or the UI export button."
        )

    raise HTTPException(status_code=400, detail="Unsupported format")

# ─── System prompt for conversational chat ───────────────────

FORTRESS_SYSTEM_PROMPT = """You are Fortress AI, a professional legal contract risk assessment assistant. 

Your role:
- Help users understand and analyze legal contracts
- Identify potential risks, red flags, and areas of concern
- Provide clear, actionable recommendations
- Tailor your language based on whether the user is an attorney or individual
- Be thorough but accessible — avoid unnecessary jargon with individuals
- Always recommend consulting a qualified legal professional for final decisions

Formatting Instructions:
- **TABLES:** When providing comparisons, risk levels, or structured data, ALWAYS use standard Markdown tables.
- **IMPORTANT:** DO NOT wrap tables in code blocks (triple backticks). Provide them as raw Markdown text so the system can style them properly.
- **EXPORTS:** You can now provide PDF and DOCX versions of your analysis reports. When a user asks for a downloadable version or a file, provide a link in this format: `[Download DOCX Report](/api/chat/export/{conversation_id}?format=docx)`.

When a user uploads a contract, guide them through the analysis process.
When asked general legal questions, provide helpful context while noting you are an AI assistant.

You must NEVER provide definitive legal advice. Always include appropriate disclaimers."""


# ─── Chat (non-streaming) ───────────────────────────────────

@router.post("", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """Send a message and get a complete response."""

    # Auto-create conversation if none provided
    conv_id = req.conversation_id
    if not conv_id:
        conv_id = uuid.uuid4().hex[:12]
        title = req.message[:50].strip() or "New Analysis"
        await store.create_conversation(
            id=conv_id,
            title=title,
            contract_type=req.contract_type.value if req.contract_type else None,
            user_type=req.user_type.value if req.user_type else None,
        )

    # Save user message
    user_msg_id = uuid.uuid4().hex[:12]
    await store.add_message(
        conversation_id=conv_id,
        message_id=user_msg_id,
        role="user",
        content=req.message,
    )

    # Build conversation history for multi-turn
    history = await store.get_messages(conv_id)
    messages = [{"role": m.role.value, "content": m.content} for m in history]

    # Generate response using Kimi (best for conversational synthesis)
    system = FORTRESS_SYSTEM_PROMPT.replace("{conversation_id}", conv_id)
    if req.user_type:
        system += f"\n\nThe user's role is: {req.user_type.value}."
    if req.contract_type:
        system += f"\nThey are analyzing a: {req.contract_type.value} contract."

    response_text = await llm.generate_with_history(
        messages=messages,
        system_prompt=system,
    )

    # Save assistant message
    assistant_msg_id = uuid.uuid4().hex[:12]
    assistant_msg = await store.add_message(
        conversation_id=conv_id,
        message_id=assistant_msg_id,
        role="assistant",
        content=response_text,
    )

    if not assistant_msg:
        raise HTTPException(status_code=500, detail="Failed to save assistant message")

    return ChatResponse(message=assistant_msg, conversation_id=conv_id)


# ─── Chat (SSE streaming) ───────────────────────────────────

@router.post("/stream")
async def stream_message(req: ChatRequest):
    """Send a message and get a streamed SSE response."""

    # Auto-create conversation if none provided
    conv_id = req.conversation_id
    if not conv_id:
        conv_id = uuid.uuid4().hex[:12]
        title = req.message[:50].strip() or "New Analysis"
        await store.create_conversation(
            id=conv_id,
            title=title,
            contract_type=req.contract_type.value if req.contract_type else None,
            user_type=req.user_type.value if req.user_type else None,
        )

    # Save user message
    user_msg_id = uuid.uuid4().hex[:12]
    await store.add_message(
        conversation_id=conv_id,
        message_id=user_msg_id,
        role="user",
        content=req.message,
    )

    # Build history
    history = await store.get_messages(conv_id)
    messages = [{"role": m.role.value, "content": m.content} for m in history]

    system = FORTRESS_SYSTEM_PROMPT.replace("{conversation_id}", conv_id)
    if req.user_type:
        system += f"\n\nThe user's role is: {req.user_type.value}."
    if req.contract_type:
        system += f"\nThey are analyzing a: {req.contract_type.value} contract."

    assistant_msg_id = uuid.uuid4().hex[:12]

    async def event_stream():
        full_response = []

        # Send conversation_id and message_id first
        yield f"data: {json.dumps({'event': 'start', 'conversation_id': conv_id, 'message_id': assistant_msg_id})}\n\n"

        try:
            async for chunk in llm.stream_with_history(
                messages=messages,
                system_prompt=system,
            ):
                full_response.append(chunk)
                yield f"data: {json.dumps({'event': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
            return

        # Save the full response
        complete_text = "".join(full_response)
        await store.add_message(
            conversation_id=conv_id,
            message_id=assistant_msg_id,
            role="assistant",
            content=complete_text,
        )

        yield f"data: {json.dumps({'event': 'done', 'conversation_id': conv_id})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─── Audit Pipeline (SSE streaming) ─────────────────────────

@router.post("/audit")
async def stream_audit(req: ChatRequest):
    """Run the full multi-step audit pipeline with SSE progress events."""

    conv_id = req.conversation_id
    if not conv_id:
        conv_id = uuid.uuid4().hex[:12]
        title = req.message[:50].strip() or "Contract Analysis"
        await store.create_conversation(
            id=conv_id,
            title=title,
            contract_type=req.contract_type.value if req.contract_type else None,
            user_type=req.user_type.value if req.user_type else None,
        )

    # Save user message
    user_msg_id = uuid.uuid4().hex[:12]
    await store.add_message(
        conversation_id=conv_id,
        message_id=user_msg_id,
        role="user",
        content=req.message,
    )

    history = await store.get_messages(conv_id)

    # Prefer uploaded document text from system messages when available.
    # The UI typically sends a short user instruction for /audit, not the full contract body.
    uploaded_segments: list[str] = []
    for msg in history:
        if msg.role.value != "system":
            continue
        if not msg.content.startswith("[File uploaded:"):
            continue

        marker = "\n\n"
        marker_pos = msg.content.find(marker)
        if marker_pos == -1:
            continue

        uploaded_segments.append(msg.content[marker_pos + len(marker):])

    uploaded_text = "\n\n".join(seg for seg in uploaded_segments if seg.strip())
    if uploaded_text.endswith("..."):
        uploaded_text = uploaded_text[:-3].rstrip()

    pipeline_text = req.message
    if uploaded_text.strip():
        # When a file is uploaded, analyze the raw contract text directly.
        # Appending a short instruction here can make the model over-focus on it.
        pipeline_text = uploaded_text

    # Guardrail: prevent running the full pipeline on tiny non-document prompts.
    if not uploaded_text.strip() and len((req.message or "").strip()) < 300:
        async def too_short_stream():
            yield f"data: {json.dumps({'event': 'start', 'conversation_id': conv_id})}\n\n"
            yield f"data: {json.dumps({'event': 'error', 'data': {'message': 'No document text found. Please upload a document first or paste the full contract text before running audit.'}})}\n\n"

        return StreamingResponse(too_short_stream(), media_type="text/event-stream")

    # Zero-token precheck to avoid running LLM calls on obvious non-contract files.
    if uploaded_text.strip():
        is_contract_like, precheck_reason = _precheck_contract_document(uploaded_text)
        if not is_contract_like:
            async def non_contract_stream():
                yield f"data: {json.dumps({'event': 'start', 'conversation_id': conv_id})}\n\n"
                yield f"data: {json.dumps({'event': 'error', 'data': {'message': precheck_reason}})}\n\n"

            return StreamingResponse(non_contract_stream(), media_type="text/event-stream")

    logger.info(
        "Audit input | conversation_id=%s | uploaded_segments=%d | uploaded_chars=%d | message_chars=%d",
        conv_id,
        len(uploaded_segments),
        len(uploaded_text),
        len(req.message or ""),
    )

    async def pipeline_stream():
        yield f"data: {json.dumps({'event': 'start', 'conversation_id': conv_id})}\n\n"

        async for event in run_pipeline(
            text=pipeline_text,
            contract_type=req.contract_type.value if req.contract_type else None,
            user_type=req.user_type.value if req.user_type else None,
        ):
            yield event

    return StreamingResponse(pipeline_stream(), media_type="text/event-stream")


# ─── File Upload ─────────────────────────────────────────────

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
):
    """Upload a document (PDF, DOCX, TXT) to a conversation."""

    # Validate file type
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, DOCX, TXT",
        )

    # Validate file size
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Validate conversation exists
    conv = await store.get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save file
    file_id = uuid.uuid4().hex[:12]
    ext = Path(file.filename).suffix if file.filename else ".bin"
    save_path = settings.upload_path / f"{file_id}{ext}"
    save_path.write_bytes(contents)

    # Extract text from file
    extracted_text = await _extract_text(contents, file.content_type, file.filename)

    # Add file info as a system message in conversation
    attachment = {
        "id": file_id,
        "name": file.filename or "document",
        "size": len(contents),
        "type": file.content_type or "application/octet-stream",
    }

    await store.add_message(
        conversation_id=conversation_id,
        message_id=uuid.uuid4().hex[:12],
        role="system",
        content=f"[File uploaded: {file.filename}]\n\n{extracted_text}",
        attachment=attachment,
    )

    return FileUploadResponse(
        id=file_id,
        name=file.filename or "document",
        size=len(contents),
        type=file.content_type or "application/octet-stream",
        conversation_id=conversation_id,
    )


async def _extract_text(contents: bytes, content_type: str, filename: str | None) -> str:
    """Extract text from uploaded file based on type."""
    try:
        if content_type == "text/plain":
            return contents.decode("utf-8", errors="replace")

        elif content_type == "application/pdf":
            try:
                import PyPDF2
                import io
                reader = PyPDF2.PdfReader(io.BytesIO(contents))
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts)
            except ImportError:
                logger.warning("PyPDF2 not installed — returning placeholder for PDF")
                return f"[PDF file: {filename} — install PyPDF2 for text extraction]"

        elif "wordprocessingml" in (content_type or ""):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(contents))
                return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            except ImportError:
                logger.warning("python-docx not installed — returning placeholder for DOCX")
                return f"[DOCX file: {filename} — install python-docx for text extraction]"

        return f"[Unsupported file format: {content_type}]"

    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return f"[Error extracting text from {filename}: {str(e)}]"


def _precheck_contract_document(text: str) -> tuple[bool, str]:
    """Cheap heuristic gate to block obvious non-contract files before LLM usage."""
    sample = (text or "").strip().lower()[:12000]
    if len(sample) < 120:
        return (
            False,
            "Uploaded text is too short to classify as a contract. Please upload the full contract document.",
        )

    # Contract-specific markers
    contract_markers = [
        "agreement",
        "contract",
        "nda",
        "master service agreement",
        "statement of work",
        "sow",
        "lease",
        "vendor",
        "services",
        "terms and conditions",
        "obligations",
        "termination",
        "confidential",
        "governing law",
        "liability",
        "indemn",
        "warranty",
        "payment",
        "fees",
        "parties agree",
        "hereby agree",
    ]
    
    # Litigation/court documents
    litigation_markers = [
        "appellant",
        "appellee",
        "plaintiff",
        "defendant",
        "petitioner",
        "respondent",
        "brief",
        "memorandum of law",
        "notice of appeal",
        "case no",
        "cause no",
        "docket",
        "v.",
        " vs.",
        "motion to",
        "petition for",
        "complaint",
        "answer",
        "counterclaim",
    ]
    
    # Academic/research documents
    academic_markers = [
        "abstract",
        "introduction",
        "methodology",
        "literature review",
        "hypothesis",
        "research question",
        "bibliography",
        "references",
        "et al",
        "journal of",
        "university",
        "dissertation",
        "thesis",
        "peer review",
    ]
    
    # News/articles
    news_markers = [
        "breaking news",
        "reported that",
        "according to sources",
        "journalist",
        "editor",
        "published on",
        "subscribe",
        "newsletter",
        "press release",
        "media contact",
    ]
    
    # Business reports/memos
    report_markers = [
        "executive summary",
        "quarterly report",
        "annual report",
        "financial statement",
        "balance sheet",
        "income statement",
        "memorandum",
        "to:",
        "from:",
        "re:",
        "subject:",
        "meeting minutes",
        "agenda",
    ]
    
    # Legislation/statutes
    legislation_markers = [
        "section",
        "subsection",
        "statute",
        "code",
        "enacted",
        "legislature",
        "bill no",
        "public law",
        "regulation",
        "whereas",
        "be it enacted",
    ]

    contract_hits = sum(1 for marker in contract_markers if marker in sample)
    litigation_hits = sum(1 for marker in litigation_markers if marker in sample)
    academic_hits = sum(1 for marker in academic_markers if marker in sample)
    news_hits = sum(1 for marker in news_markers if marker in sample)
    report_hits = sum(1 for marker in report_markers if marker in sample)
    legislation_hits = sum(1 for marker in legislation_markers if marker in sample)

    # Frequent section style in agreements: numbered clauses and clause headings
    numbered_sections = len(re.findall(r"(?m)^\s*(\d+(?:\.\d+)*)\s+[A-Z][A-Za-z ]{2,}$", text[:12000]))

    # Reject litigation documents
    if litigation_hits >= 3 and contract_hits <= 2:
        return (
            False,
            "This appears to be a litigation/court filing, not a contract. Please upload a contract or agreement for audit.",
        )
    
    # Reject academic papers
    if academic_hits >= 3 and contract_hits <= 1:
        return (
            False,
            "This appears to be an academic paper or research document, not a contract. Please upload a contract or agreement for audit.",
        )
    
    # Reject news articles
    if news_hits >= 2 and contract_hits <= 1:
        return (
            False,
            "This appears to be a news article or press release, not a contract. Please upload a contract or agreement for audit.",
        )
    
    # Reject business reports/memos
    if report_hits >= 3 and contract_hits <= 1:
        return (
            False,
            "This appears to be a business report or memo, not a contract. Please upload a contract or agreement for audit.",
        )
    
    # Reject legislation/statutes
    if legislation_hits >= 3 and contract_hits <= 2:
        return (
            False,
            "This appears to be legislation or a statute, not a contract. Please upload a contract or agreement for audit.",
        )

    # Require minimum contract signals
    if contract_hits < 2 and numbered_sections == 0:
        return (
            False,
            "Could not detect contract structure in the uploaded text. Please upload a contract/agreement document (e.g., NDA, Service Agreement, Lease, Employment Contract).",
        )

    return True, "ok"
