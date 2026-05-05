"""Chat routes — send messages, stream responses, upload files."""

from __future__ import annotations

import json
import uuid
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, Response
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

    async def pipeline_stream():
        yield f"data: {json.dumps({'event': 'start', 'conversation_id': conv_id})}\n\n"

        async for event in run_pipeline(
            text=req.message,
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
        content=f"[File uploaded: {file.filename}]\n\n{extracted_text[:2000]}..." if len(extracted_text) > 2000 else f"[File uploaded: {file.filename}]\n\n{extracted_text}",
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
