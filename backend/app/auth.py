from __future__ import annotations

from fastapi import Header, HTTPException

from .config import ADMIN_TOKEN


def require_admin(authorization: str | None = Header(default=None)) -> str:
    expected = f"Bearer {ADMIN_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Admin token required")
    return "local-admin"

