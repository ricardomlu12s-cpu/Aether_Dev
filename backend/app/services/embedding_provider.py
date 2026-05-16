from __future__ import annotations

import json
import math
from collections import Counter
from typing import Protocol
from urllib import request
from urllib.error import HTTPError, URLError

from ..config import (
    EMBEDDING_API_KEY,
    EMBEDDING_BASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
)


class EmbeddingProvider(Protocol):
    name: str
    dim: int

    def embed(self, text: str) -> list[float]:
        ...

    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        ...


class LocalEmbeddingProvider:
    name = "local"
    dim = 0  # variable, sparse

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Local provider returns sparse dicts, use embed_sparse()")

    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("Local provider returns sparse dicts, use batch_embed_sparse()")

    @staticmethod
    def embed_sparse(text: str) -> dict[str, float]:
        from .vector_store import embed_text
        return embed_text(text)

    @staticmethod
    def batch_embed_sparse(texts: list[str]) -> list[dict[str, float]]:
        return [LocalEmbeddingProvider.embed_sparse(t) for t in texts]


class OpenAIEmbeddingProvider:
    name = "openai_compatible"
    dim = 1536

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        return self.batch_embed([text])[0]

    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise RuntimeError("AETHER_EMBEDDING_API_KEY is required for OpenAI embedding provider")
        payload = {"model": self.model, "input": texts}
        req = request.Request(
            f"{self.base_url}/embeddings",
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
            raise RuntimeError(f"embedding provider HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"embedding provider unavailable: {exc}") from exc
        return [item["embedding"] for item in sorted(data["data"], key=lambda d: d["index"])]


def cosine_dense(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


class EmbeddingGateway:
    def __init__(self) -> None:
        self.provider: EmbeddingProvider = self._load_provider()

    def _load_provider(self) -> EmbeddingProvider:
        if EMBEDDING_PROVIDER in {"openai", "openai_compatible"}:
            return OpenAIEmbeddingProvider(EMBEDDING_BASE_URL, EMBEDDING_API_KEY, EMBEDDING_MODEL)
        return LocalEmbeddingProvider()

    def embed(self, text: str):
        return self.provider.embed(text)

    def batch_embed(self, texts: list[str]):
        return self.provider.batch_embed(texts)

    def status(self) -> dict:
        return {
            "provider": self.provider.name,
            "configured_provider": EMBEDDING_PROVIDER,
            "model": EMBEDDING_MODEL if self.provider.name != "local" else None,
            "base_url": EMBEDDING_BASE_URL if self.provider.name != "local" else None,
        }


embedding_gateway = EmbeddingGateway()
