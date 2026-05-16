from __future__ import annotations

import json
import uuid

from ..database import connect, utc_now


def audit(actor: str, action: str, target_type: str, target_id: str | None = None, metadata: dict | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO audit_logs(id, actor, action, target_type, target_id, created_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                actor,
                action,
                target_type,
                target_id,
                utc_now(),
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )


def recent_audit(limit: int = 50) -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) for row in rows]

