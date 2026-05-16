from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.settings_service import settings_service

router = APIRouter()


class ModelSettingsUpdate(BaseModel):
    provider: str | None = None
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None


class LanguageUpdate(BaseModel):
    language: str = Field(min_length=1)


@router.get("/settings")
def get_settings() -> dict:
    return settings_service.all_settings()


@router.get("/settings/{key}")
def get_setting(key: str) -> dict:
    value = settings_service.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Unknown setting key: {key}")
    return {"key": key, "value": value}


@router.put("/settings/model")
def update_model(payload: ModelSettingsUpdate) -> dict:
    return settings_service.update_model(
        provider=payload.provider,
        model=payload.model,
        base_url=payload.base_url,
        api_key=payload.api_key,
    )


@router.put("/settings/language")
def update_language(payload: LanguageUpdate) -> dict:
    language = settings_service.update_language(payload.language)
    return {"language": language}
