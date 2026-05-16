from __future__ import annotations

import json
import uuid

from ..database import connect, utc_now


class EventBus:
    def publish(self, event_type: str, payload: dict) -> str:
        event_id = str(uuid.uuid4())
        with connect() as conn:
            conn.execute(
                "INSERT INTO runtime_events(id, event_type, payload_json, created_at, status) VALUES (?, ?, ?, ?, ?)",
                (event_id, event_type, json.dumps(payload, ensure_ascii=False), utc_now(), "new"),
            )
        return event_id

    def recent(self, limit: int = 50) -> list[dict]:
        with connect() as conn:
            rows = conn.execute(
                "SELECT * FROM runtime_events ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]


event_bus = EventBus()

