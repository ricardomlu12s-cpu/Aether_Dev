from __future__ import annotations

import json

from ..database import connect, utc_now


DEFAULT_MODEL_SETTINGS = {
    "provider": "openai_compatible",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
}

DEFAULT_LANGUAGE = "zh"

SETTINGS_SCHEMA = {
    "model": {"type": "object", "default": DEFAULT_MODEL_SETTINGS},
    "language": {"type": "string", "default": DEFAULT_LANGUAGE},
}


class SettingsService:
    def get(self, key: str) -> dict | str | None:
        with connect() as conn:
            row = conn.execute("SELECT value_json FROM app_settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            schema = SETTINGS_SCHEMA.get(key)
            if schema is None:
                return None
            default = schema["default"]
            self.set(key, default)
            return default
        value = json.loads(row["value_json"])
        return value

    def set(self, key: str, value) -> None:
        now = utc_now()
        with connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_settings(key, value_json, updated_at) VALUES (?, ?, ?)",
                (key, json.dumps(value, ensure_ascii=False), now),
            )

    def all_settings(self) -> dict:
        result = {}
        for key in SETTINGS_SCHEMA:
            result[key] = self.get(key)
        return result

    def update_model(self, provider: str | None = None, model: str | None = None,
                     base_url: str | None = None, api_key: str | None = None) -> dict:
        current = self.get("model") or dict(DEFAULT_MODEL_SETTINGS)
        if provider is not None:
            current["provider"] = provider
        if model is not None:
            current["model"] = model
        if base_url is not None:
            current["base_url"] = base_url
        if api_key is not None:
            current["api_key"] = api_key
        self.set("model", current)
        from .model_gateway import model_gateway
        model_gateway.reload()
        return current

    def update_language(self, language: str) -> str:
        self.set("language", language)
        return language


settings_service = SettingsService()
