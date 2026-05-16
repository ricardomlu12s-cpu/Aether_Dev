from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Protocol

from ..config import CHROMA_COLLECTION, LANCEDB_TABLE, VECTOR_BACKEND, VECTOR_STORE_PATH

TOKEN_RE = re.compile(r"[\w一-鿿]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def embed_text(text: str) -> dict[str, float]:
    counts = Counter(tokenize(text))
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
    return {k: v / norm for k, v in counts.items()}


def cosine_sparse(a: dict[str, float], b: dict[str, float]) -> float:
    return sum(value * b.get(key, 0.0) for key, value in a.items())


class InvertedIndex:
    """Sparse inverted index for O(|query_terms|) memory retrieval."""

    def __init__(self):
        self.index: dict[str, list[tuple[str, float]]] = defaultdict(list)

    def build(self, rows: list[dict]) -> None:
        self.index.clear()
        for row in rows:
            self._add(row["id"], row.get("embedding", {}))

    def upsert(self, doc_id: str, embedding: dict[str, float]) -> None:
        self.remove(doc_id)
        self._add(doc_id, embedding)

    def remove(self, doc_id: str) -> None:
        for term in list(self.index):
            self.index[term] = [(did, w) for did, w in self.index[term] if did != doc_id]
            if not self.index[term]:
                del self.index[term]

    def query(self, query_embedding: dict[str, float], top_k: int = 5) -> list[tuple[str, float]]:
        scores: dict[str, float] = defaultdict(float)
        for term, q_weight in query_embedding.items():
            for doc_id, doc_weight in self.index.get(term, []):
                scores[doc_id] += q_weight * doc_weight
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def _add(self, doc_id: str, embedding: dict[str, float]) -> None:
        for term, weight in embedding.items():
            self.index[term].append((doc_id, weight))

    def status(self) -> dict:
        return {"terms": len(self.index), "postings": sum(len(p) for p in self.index.values())}


class VectorStore(Protocol):
    backend_name: str

    def upsert(self, embedding_id: str, text: str, metadata: dict) -> None:
        ...

    def query(self, text: str, limit: int = 5) -> list[dict]:
        ...

    def delete(self, embedding_id: str) -> None:
        ...

    def status(self) -> dict:
        ...


class LocalVectorStore:
    backend_name = "local"

    def __init__(self, path: Path = VECTOR_STORE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        self._rebuild_index()

    def _load(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, rows: list[dict]) -> None:
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def _rebuild_index(self) -> None:
        self.index = InvertedIndex()
        self.index.build(self._load())

    def upsert(self, embedding_id: str, text: str, metadata: dict) -> None:
        rows = [row for row in self._load() if row["id"] != embedding_id]
        embedding = embed_text(text)
        rows.append(
            {
                "id": embedding_id,
                "text": text,
                "embedding": embedding,
                "metadata": metadata,
            }
        )
        self._save(rows)
        self.index.upsert(embedding_id, embedding)

    def query(self, text: str, limit: int = 5) -> list[dict]:
        query_embedding = embed_text(text)
        ranked = self.index.query(query_embedding, top_k=limit)
        if not ranked:
            return []
        rows_by_id = {row["id"]: row for row in self._load()}
        result = []
        for doc_id, score in ranked:
            row = rows_by_id.get(doc_id)
            if row:
                result.append({**row, "score": score})
        return result

    def delete(self, embedding_id: str) -> None:
        self._save([row for row in self._load() if row["id"] != embedding_id])
        self.index.remove(embedding_id)

    def status(self) -> dict:
        base = {"backend": self.backend_name, "path": str(self.path)}
        base.update(self.index.status())
        return base


class ChromaVectorStore:
    backend_name = "chroma"

    def __init__(self, path: Path = VECTOR_STORE_PATH):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is not installed. Install optional dependency chromadb.") from exc
        self.client = chromadb.PersistentClient(path=str(path.parent / "chroma"))
        self.collection = self.client.get_or_create_collection(CHROMA_COLLECTION)

    def upsert(self, embedding_id: str, text: str, metadata: dict) -> None:
        self.collection.upsert(ids=[embedding_id], documents=[text], metadatas=[metadata])

    def query(self, text: str, limit: int = 5) -> list[dict]:
        result = self.collection.query(query_texts=[text], n_results=limit)
        rows = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if result.get("distances") else [0.0] * len(ids)
        for idx, embedding_id in enumerate(ids):
            rows.append(
                {
                    "id": embedding_id,
                    "text": docs[idx],
                    "metadata": metas[idx] or {},
                    "score": 1.0 / (1.0 + float(distances[idx])),
                }
            )
        return rows

    def delete(self, embedding_id: str) -> None:
        self.collection.delete(ids=[embedding_id])

    def status(self) -> dict:
        return {"backend": self.backend_name, "collection": CHROMA_COLLECTION}


class LanceVectorStore(LocalVectorStore):
    backend_name = "lancedb_compatible_local"


def load_vector_store() -> VectorStore:
    if VECTOR_BACKEND == "chroma":
        return ChromaVectorStore()
    if VECTOR_BACKEND == "lancedb":
        return LanceVectorStore()
    return LocalVectorStore()


vector_store = load_vector_store()
