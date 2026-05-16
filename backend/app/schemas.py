from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class ChatMessageRequest(BaseModel):
    conversation_id: str | None = None
    content: str = Field(min_length=1)
    language: str = "auto"


class MemoryWriteRequest(BaseModel):
    content: str = Field(min_length=1)
    level: str = "L2"
    summary: str | None = None
    importance_score: float = 0.5
    emotional_weight: float = 0.0
    source_message_id: str | None = None
    metadata: dict[str, Any] = {}


class MemoryQueryResponse(BaseModel):
    id: str
    level: str
    content: str
    summary: str
    score: float


class EmotionUpdateRequest(BaseModel):
    pleasure_delta: float = 0.0
    arousal_delta: float = 0.0
    dominance_delta: float = 0.0
    energy_delta: float = 0.0

