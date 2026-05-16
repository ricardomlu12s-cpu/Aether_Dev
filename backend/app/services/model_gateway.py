from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib import request
from urllib.error import HTTPError, URLError

from ..config import MODEL_API_KEY, MODEL_BASE_URL, MODEL_NAME, MODEL_PROVIDER

@dataclass(frozen=True)
class ModelContext:
    user_input: str
    l1_messages: list[dict]
    memories: list[dict]
    emotion_state: dict


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
            raise RuntimeError("AETHER_MODEL_API_KEY is required for OpenAI-compatible provider")

        memory_block = "\n".join(f"- {item['summary']}" for item in context.memories[:6]) or "- none"
        l1_block = "\n".join(f"{item['role']}: {item['content']}" for item in context.l1_messages[-10:])
        prompt = (
            "You are Aether Dev, a developer-side digital life system under construction. "
            "Answer clearly and keep developer continuity. Do not reveal chain-of-thought.\n\n"
            f"Emotion state: {context.emotion_state}\n"
            f"Relevant memories:\n{memory_block}\n\n"
            f"Recent conversation:\n{l1_block}\n\n"
            f"User input:\n{context.user_input}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Return only the spoken response text."},
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
            with request.urlopen(req, timeout=60) as response:
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

    def _load_provider(self) -> ModelProvider:
        if MODEL_PROVIDER in {"openai", "openai_compatible"}:
            return OpenAICompatibleProvider(MODEL_BASE_URL, MODEL_API_KEY, MODEL_NAME)
        return MockModelProvider()

    def generate(self, context: ModelContext) -> ModelResult:
        return self.provider.generate(context)

    def status(self) -> dict:
        return {
            "provider": self.provider.name,
            "configured_provider": MODEL_PROVIDER,
            "model": MODEL_NAME if self.provider.name != "mock" else None,
            "base_url": MODEL_BASE_URL if self.provider.name != "mock" else None,
            "ready_for_adapters": ["openai", "claude", "local_model"],
        }


model_gateway = ModelGateway()
