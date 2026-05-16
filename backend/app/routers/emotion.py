from __future__ import annotations

from fastapi import APIRouter

from ..schemas import EmotionUpdateRequest
from ..services.emotion_engine import emotion_engine

router = APIRouter()


@router.get("/emotion/status")
def status() -> dict:
    return emotion_engine.decay()


@router.post("/emotion/update")
def update(payload: EmotionUpdateRequest) -> dict:
    return emotion_engine.update(
        pleasure=payload.pleasure_delta,
        arousal=payload.arousal_delta,
        dominance=payload.dominance_delta,
        energy=payload.energy_delta,
    )

