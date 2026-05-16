from __future__ import annotations

import json
import uuid

from ..database import connect, utc_now
from .event_bus import event_bus
from .vector_store import vector_store


def summarize(text: str, limit: int = 120) -> str:
    cleaned = " ".join(text.split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "..."


class MemoryService:
    def write(
        self,
        content: str,
        level: str = "L2",
        summary: str | None = None,
        importance_score: float = 0.5,
        emotional_weight: float = 0.0,
        source_message_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        memory_id = str(uuid.uuid4())
        embedding_id = f"memory:{memory_id}"
        now = utc_now()
        memory_summary = summary or summarize(content)
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO memories(
                  id, level, content, summary, importance_score, emotional_weight,
                  embedding_id, source_message_id, created_at, updated_at, decay_score, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    level,
                    content,
                    memory_summary,
                    importance_score,
                    emotional_weight,
                    embedding_id,
                    source_message_id,
                    now,
                    now,
                    0.0,
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
        vector_store.upsert(embedding_id, content, {"memory_id": memory_id, "level": level})
        event_bus.publish("memory.written", {"memory_id": memory_id, "level": level})
        return self.get(memory_id)

    def get(self, memory_id: str) -> dict:
        with connect() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        return dict(row)

    def query(self, text: str, limit: int = 5) -> list[dict]:
        vector_results = vector_store.query(text, limit=limit)
        if not vector_results:
            return []
        memory_ids = [item["metadata"]["memory_id"] for item in vector_results]
        score_by_id = {item["metadata"]["memory_id"]: item["score"] for item in vector_results}
        placeholders = ",".join("?" for _ in memory_ids)
        with connect() as conn:
            rows = conn.execute(f"SELECT * FROM memories WHERE id IN ({placeholders})", memory_ids).fetchall()
            conn.executemany(
                "UPDATE memories SET last_accessed_at = ? WHERE id = ?",
                [(utc_now(), memory_id) for memory_id in memory_ids],
            )
        result = []
        for row in rows:
            item = dict(row)
            item["score"] = score_by_id[item["id"]]
            result.append(item)
        result.sort(key=lambda item: item["score"], reverse=True)
        event_bus.publish("memory.retrieved", {"query": text, "count": len(result)})
        return result

    def delete(self, memory_id: str) -> bool:
        memory = self.get(memory_id)
        with connect() as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        if memory.get("embedding_id"):
            vector_store.delete(memory["embedding_id"])
        event_bus.publish("memory.deleted", {"memory_id": memory_id})
        return True

    def update_level(self, memory_id: str, level: str) -> dict:
        now = utc_now()
        with connect() as conn:
            conn.execute(
                "UPDATE memories SET level = ?, updated_at = ? WHERE id = ?",
                (level, now, memory_id),
            )
        event_bus.publish("memory.level_updated", {"memory_id": memory_id, "level": level})
        return self.get(memory_id)

    def status(self) -> dict:
        return vector_store.status()

    def list_recent(self, limit: int = 50) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def maybe_write_from_message(self, message_id: str, content: str) -> dict | None:
        if len(content.strip()) < 18:
            return None
        important_markers = ["记住", "目标", "要求", "项目", "必须", "喜欢", "不喜欢", "架构"]
        importance = 0.8 if any(marker in content for marker in important_markers) else 0.45
        if importance < 0.5:
            return None
        return self.write(
            content=content,
            level="L2",
            summary=summarize(content),
            importance_score=importance,
            source_message_id=message_id,
            metadata={"source": "auto_extract"},
        )

    def run_rem(self) -> dict:
        with connect() as conn:
            rows = conn.execute(
                "SELECT content FROM messages ORDER BY created_at DESC LIMIT 12"
            ).fetchall()
        if not rows:
            return {"created": False, "reason": "no messages"}
        summary = summarize(" / ".join(row["content"] for row in reversed(rows)), limit=400)
        memory = self.write(
            content=summary,
            level="L2",
            summary=f"REM summary: {summarize(summary, 160)}",
            importance_score=0.6,
            metadata={"source": "manual_rem"},
        )
        event_bus.publish("rem.completed", {"memory_id": memory["id"]})
        return {"created": True, "memory": memory}


memory_service = MemoryService()
