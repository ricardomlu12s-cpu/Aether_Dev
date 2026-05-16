from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import ConversationCreate
from ..services.chat_service import chat_service

router = APIRouter()


@router.get("/conversations")
def list_conversations() -> list[dict]:
    return chat_service.list_conversations()


@router.post("/conversations")
def create_conversation(payload: ConversationCreate) -> dict:
    return chat_service.create_conversation(payload.title)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: str) -> list[dict]:
    try:
        chat_service.get_conversation(conversation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return chat_service.list_messages(conversation_id)

