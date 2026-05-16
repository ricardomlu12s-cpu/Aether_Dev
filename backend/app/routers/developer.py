from __future__ import annotations

from fastapi import APIRouter, Depends

from ..auth import require_admin
from ..config import APP_VERSION, DATA_DIR
from ..database import connect
from ..services.audit_service import audit, recent_audit
from ..services.emotion_engine import emotion_engine
from ..services.event_bus import event_bus
from ..services.memory_service import memory_service
from ..services.model_gateway import model_gateway
from ..services.plugin_runtime import plugin_runtime

router = APIRouter()


@router.get("/developer/runtime")
def runtime(actor: str = Depends(require_admin)) -> dict:
    with connect() as conn:
        conversation_count = conn.execute("SELECT COUNT(*) AS c FROM conversations").fetchone()["c"]
        message_count = conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"]
        memory_count = conn.execute("SELECT COUNT(*) AS c FROM memories").fetchone()["c"]
    return {
        "version": APP_VERSION,
        "data_dir": str(DATA_DIR),
        "conversation_count": conversation_count,
        "message_count": message_count,
        "memory_count": memory_count,
        "vector_store": memory_service.status(),
        "model": model_gateway.status(),
        "emotion": emotion_engine.status(),
        "plugins": plugin_runtime.list_plugins(),
        "events": event_bus.recent(20),
    }


@router.get("/developer/logs")
def logs(actor: str = Depends(require_admin)) -> list[dict]:
    return event_bus.recent(100)


@router.get("/developer/audit")
def audit_logs(actor: str = Depends(require_admin)) -> list[dict]:
    return recent_audit(100)


@router.post("/developer/rem/run")
def run_rem(actor: str = Depends(require_admin)) -> dict:
    audit(actor, "rem.run", "memory")
    event_bus.publish("rem.started", {"actor": actor})
    return memory_service.run_rem()
