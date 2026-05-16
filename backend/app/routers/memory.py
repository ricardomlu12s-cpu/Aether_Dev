from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import require_admin
from ..schemas import MemoryWriteRequest
from ..services.audit_service import audit
from ..services.memory_service import memory_service

router = APIRouter()


@router.post("/memory/write")
def write_memory(payload: MemoryWriteRequest, actor: str = Depends(require_admin)) -> dict:
    memory = memory_service.write(
        content=payload.content,
        level=payload.level,
        summary=payload.summary,
        importance_score=payload.importance_score,
        emotional_weight=payload.emotional_weight,
        source_message_id=payload.source_message_id,
        metadata=payload.metadata,
    )
    audit(actor, "memory.write", "memory", memory["id"])
    return memory


@router.get("/memory/query")
def query_memory(q: str = Query(min_length=1), limit: int = 5) -> list[dict]:
    return memory_service.query(q, limit=limit)


@router.get("/memory/recent")
def recent_memories(limit: int = 50) -> list[dict]:
    return memory_service.list_recent(limit=limit)


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: str, actor: str = Depends(require_admin)) -> dict:
    try:
        memory_service.delete(memory_id)
    except TypeError as exc:
        raise HTTPException(status_code=404, detail="Memory not found") from exc
    audit(actor, "memory.delete", "memory", memory_id)
    return {"deleted": True, "id": memory_id}


@router.post("/memory/{memory_id}/level/{level}")
def update_memory_level(memory_id: str, level: str, actor: str = Depends(require_admin)) -> dict:
    if level not in {"L1", "L2", "L3"}:
        raise HTTPException(status_code=400, detail="level must be L1, L2, or L3")
    memory = memory_service.update_level(memory_id, level)
    audit(actor, "memory.level", "memory", memory_id, {"level": level})
    return memory
