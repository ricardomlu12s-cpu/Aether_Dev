from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "Aether Dev"
APP_VERSION = "0.1.0"


def app_support_dir() -> Path:
    configured = os.getenv("AETHER_DATA_DIR")
    base = Path(configured) if configured else Path.home() / "Library" / "Application Support" / APP_NAME
    try:
        base.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        base = Path(__file__).resolve().parents[2] / ".aether_data"
        try:
            base.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            base = Path("/private/tmp") / APP_NAME
            base.mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(exist_ok=True)
    (base / "vector_store").mkdir(exist_ok=True)
    (base / "plugins").mkdir(exist_ok=True)
    (base / "backups").mkdir(exist_ok=True)
    return base


DATA_DIR = app_support_dir()
DATABASE_PATH = Path(os.getenv("AETHER_DATABASE_PATH", DATA_DIR / "aether.sqlite3"))
VECTOR_STORE_PATH = Path(os.getenv("AETHER_VECTOR_STORE_PATH", DATA_DIR / "vector_store" / "memories.json"))
LOG_PATH = Path(os.getenv("AETHER_LOG_PATH", DATA_DIR / "logs" / "backend.log"))
PLUGIN_DIR = Path(os.getenv("AETHER_PLUGIN_DIR", Path(__file__).resolve().parents[2] / "plugins"))
ADMIN_TOKEN = os.getenv("AETHER_ADMIN_TOKEN", "dev-admin-token")
L1_MESSAGE_LIMIT = int(os.getenv("AETHER_L1_MESSAGE_LIMIT", "12"))
MODEL_PROVIDER = os.getenv("AETHER_MODEL_PROVIDER", "mock")
MODEL_API_KEY = os.getenv("AETHER_MODEL_API_KEY", "")
MODEL_NAME = os.getenv("AETHER_MODEL_NAME", "gpt-4.1-mini")
MODEL_BASE_URL = os.getenv("AETHER_MODEL_BASE_URL", "https://api.openai.com/v1")
VECTOR_BACKEND = os.getenv("AETHER_VECTOR_BACKEND", "local")
EMBEDDING_PROVIDER = os.getenv("AETHER_EMBEDDING_PROVIDER", "local")
EMBEDDING_MODEL = os.getenv("AETHER_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_API_KEY = os.getenv("AETHER_EMBEDDING_API_KEY", MODEL_API_KEY)
EMBEDDING_BASE_URL = os.getenv("AETHER_EMBEDDING_BASE_URL", MODEL_BASE_URL)
CHROMA_COLLECTION = os.getenv("AETHER_CHROMA_COLLECTION", "aether_memories")
LANCEDB_TABLE = os.getenv("AETHER_LANCEDB_TABLE", "aether_memories")
