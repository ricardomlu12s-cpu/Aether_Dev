from __future__ import annotations

import json
import ssl
from dataclasses import dataclass, field
from typing import Protocol
from urllib import request
from urllib.error import HTTPError, URLError

import certifi

from ..config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME, MODEL_PROVIDER

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


LANGUAGE_PROMPTS = {
    "zh": "请用中文回答。",
    "en": "Please respond in English.",
    "ja": "日本語で回答してください。",
    "ko": "한국어로 응답해 주세요.",
    "fr": "Veuillez répondre en français.",
    "de": "Bitte antworten Sie auf Deutsch.",
    "auto": "",
}


@dataclass(frozen=True)
class ModelContext:
    user_input: str
    l1_messages: list[dict] = field(default_factory=list)
    memories: list[dict] = field(default_factory=list)
    emotion_state: dict = field(default_factory=dict)
    language: str = "auto"


@dataclass(frozen=True)
class ModelResult:
    spoken_words: str
    prompt_summary: str
    provider: str


class ModelProvider(Protocol):
    name: str

    def generate(self, context: ModelContext) -> ModelResult:
        ...


class MockModelProvider:
    name = "mock"

    def generate(self, context: ModelContext) -> ModelResult:
        memory_line = "；".join(item["summary"] for item in context.memories[:3]) or "暂无相关长期记忆"
        spoken = (
            f"已记录。当前我会基于这次输入继续推进：{context.user_input}\n\n"
            f"相关记忆：{memory_line}"
        )
        return ModelResult(
            spoken_words=spoken,
            prompt_summary=f"L1 messages={len(context.l1_messages)}, retrieved_memories={len(context.memories)}",
            provider=self.name,
        )


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate(self, context: ModelContext) -> ModelResult:
        if not self.api_key:
            raise RuntimeError("API key is required. Please configure it in Settings.")

        lang_instruction = LANGUAGE_PROMPTS.get(context.language, "")
        memory_block = "\n".join(f"- {item['summary']}" for item in context.memories[:6]) or "- none"
        l1_block = "\n".join(f"{item['role']}: {item['content']}" for item in context.l1_messages[-10:])
        system_prompt = (
            "You are Aether Dev, a developer-side digital life system under construction. "
            "Answer clearly and keep developer continuity. Do not reveal chain-of-thought."
        )
        if lang_instruction:
            system_prompt += f" {lang_instruction}"

        prompt = (
            f"Emotion state: {context.emotion_state}\n"
            f"Relevant memories:\n{memory_block}\n\n"
            f"Recent conversation:\n{l1_block}\n\n"
            f"User input:\n{context.user_input}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60, context=_SSL_CONTEXT) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"model provider HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"model provider unavailable: {exc}") from exc

        spoken = data["choices"][0]["message"]["content"]
        return ModelResult(
            spoken_words=spoken,
            prompt_summary=f"provider={self.name}, model={self.model}, L1={len(context.l1_messages)}, memories={len(context.memories)}",
            provider=self.name,
        )


class ModelGateway:
    def __init__(self) -> None:
        self.provider: ModelProvider = self._load_provider()

    def _read_model_settings(self) -> dict:
        try:
            from ..database import connect
            with connect() as conn:
                row = conn.execute("SELECT value_json FROM app_settings WHERE key = 'model'").fetchone()
            if row:
                return json.loads(row["value_json"])
        except Exception:
            pass
        return {}

    def _load_provider(self) -> ModelProvider:
        settings = self._read_model_settings()
        provider = settings.get("provider") or MODEL_PROVIDER
        if provider in {"openai", "openai_compatible"}:
            base_url = settings.get("base_url") or MODEL_BASE_URL
            api_key = settings.get("api_key") or MODEL_API_KEY
            model = settings.get("model") or MODEL_NAME
            if api_key:
                return OpenAICompatibleProvider(base_url, api_key, model)
        return MockModelProvider()

    def reload(self) -> None:
        self.provider = self._load_provider()

    def generate(self, context: ModelContext) -> ModelResult:
        return self.provider.generate(context)

    def status(self) -> dict:
        settings = self._read_model_settings()
        return {
            "provider": self.provider.name,
            "configured_provider": settings.get("provider") or MODEL_PROVIDER,
            "model": settings.get("model") or MODEL_NAME,
            "base_url": settings.get("base_url") or MODEL_BASE_URL,
            "ready_for_adapters": ["openai", "deepseek", "claude", "local_model"],
        }


model_gateway = ModelGateway()
