"""Conversation CRUD routes."""

import uuid
from fastapi import APIRouter, HTTPException

from app.db.store import store
from app.schemas.chat import (
    ConversationCreateRequest,
    ConversationUpdateRequest,
    ConversationOut,
    ConversationSummaryOut,
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummaryOut])
async def list_conversations():
    """List all conversations (pinned first, then by timestamp desc)."""
    return await store.list_conversations()


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(req: ConversationCreateRequest):
    """Create a new conversation."""
    conv_id = uuid.uuid4().hex[:12]
    conv = await store.create_conversation(
        id=conv_id,
        title=req.title or "New Analysis",
        contract_type=req.contract_type.value if req.contract_type else None,
        user_type=req.user_type.value if req.user_type else None,
    )
    return conv


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: str):
    """Get a conversation with all messages."""
    conv = await store.get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(conversation_id: str, req: ConversationUpdateRequest):
    """Rename or pin/unpin a conversation."""
    conv = await store.update_conversation(
        id=conversation_id,
        title=req.title,
        is_pinned=req.is_pinned,
    )
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    deleted = await store.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return SuccessResponse(message="Conversation deleted")
