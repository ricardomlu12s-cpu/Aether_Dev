from __future__ import annotations

import json
import uuid

from ..config import L1_MESSAGE_LIMIT
from ..database import connect, utc_now
from .emotion_engine import emotion_engine
from .event_bus import event_bus
from .memory_service import memory_service
from .model_gateway import ModelContext, model_gateway


class ChatService:
    def create_conversation(self, title: str = "New Conversation") -> dict:
        conversation_id = str(uuid.uuid4())
        now = utc_now()
        with connect() as conn:
            conn.execute(
                "INSERT INTO conversations(id, title, created_at, updated_at, metadata_json) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, title, now, now, "{}"),
            )
        return self.get_conversation(conversation_id)

    def list_conversations(self) -> list[dict]:
        with connect() as conn:
            rows = conn.execute("SELECT * FROM conversations ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict:
        with connect() as conn:
            row = conn.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        if row is None:
            raise ValueError("Conversation not found")
        return dict(row)

    def list_messages(self, conversation_id: str) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (conversation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _insert_message(self, conversation_id: str, role: str, content: str, emotion_snapshot: dict | None = None) -> dict:
        message_id = str(uuid.uuid4())
        now = utc_now()
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO messages(
                  id, conversation_id, role, content, created_at, token_count,
                  emotion_snapshot_json, memory_tags_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    now,
                    len(content.split()),
                    json.dumps(emotion_snapshot or {}, ensure_ascii=False),
                    "[]",
                    "{}",
                ),
            )
            conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        event_bus.publish("message.created", {"message_id": message_id, "conversation_id": conversation_id, "role": role})
        return {"id": message_id, "conversation_id": conversation_id, "role": role, "content": content, "created_at": now}

    def _l1_context(self, conversation_id: str) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?",
                (conversation_id, L1_MESSAGE_LIMIT),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def send_message(self, content: str, conversation_id: str | None = None) -> dict:
        if conversation_id is None:
            conversation = self.create_conversation(title=content[:32] or "New Conversation")
            conversation_id = conversation["id"]
        else:
            self.get_conversation(conversation_id)

        emotion = emotion_engine.apply_text_event(content)
        user_message = self._insert_message(conversation_id, "user", content, emotion)
        retrieved = memory_service.query(content, limit=5)
        l1_context = self._l1_context(conversation_id)

        model_result = model_gateway.generate(
            ModelContext(
                user_input=content,
                l1_messages=l1_context,
                memories=retrieved,
                emotion_state=emotion,
            )
        )
        spoken = model_result.spoken_words
        assistant_message = self._insert_message(conversation_id, "assistant", spoken, emotion)
        event_bus.publish("message.responded", {"message_id": assistant_message["id"], "conversation_id": conversation_id})

        memory_written = memory_service.maybe_write_from_message(user_message["id"], content)
        developer_trace = {
            "retrieved_memories": [
                {"id": item["id"], "level": item["level"], "summary": item["summary"], "score": item["score"]}
                for item in retrieved
            ],
            "emotion_state": emotion,
            "memory_write_decision": "written" if memory_written else "not_written",
            "prompt_summary": model_result.prompt_summary,
            "model_provider": model_result.provider,
        }
        return {
            "message_id": assistant_message["id"],
            "conversation_id": conversation_id,
            "spoken_words": spoken,
            "developer_trace": developer_trace,
        }


chat_service = ChatService()
