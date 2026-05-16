from __future__ import annotations

from fastapi import APIRouter, WebSocket

from ..schemas import ChatMessageRequest
from ..services.chat_service import chat_service

router = APIRouter()


@router.post("/chat/message")
def send_message(payload: ChatMessageRequest) -> dict:
    return chat_service.send_message(payload.content, payload.conversation_id, payload.language)


@router.websocket("/ws/chat/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: str) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        content = data.get("content", "")
        result = chat_service.send_message(content, conversation_id)
        await websocket.send_json(result)

