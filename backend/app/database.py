from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .config import DATABASE_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version TEXT PRIMARY KEY,
              applied_at TEXT NOT NULL,
              description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversations (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS messages (
              id TEXT PRIMARY KEY,
              conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at TEXT NOT NULL,
              token_count INTEGER NOT NULL DEFAULT 0,
              emotion_snapshot_json TEXT NOT NULL DEFAULT '{}',
              memory_tags_json TEXT NOT NULL DEFAULT '[]',
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS memories (
              id TEXT PRIMARY KEY,
              level TEXT NOT NULL,
              content TEXT NOT NULL,
              summary TEXT NOT NULL,
              importance_score REAL NOT NULL DEFAULT 0,
              emotional_weight REAL NOT NULL DEFAULT 0,
              embedding_id TEXT,
              source_message_id TEXT REFERENCES messages(id) ON DELETE SET NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              last_accessed_at TEXT,
              decay_score REAL NOT NULL DEFAULT 0,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS emotion_states (
              id TEXT PRIMARY KEY,
              pleasure REAL NOT NULL,
              arousal REAL NOT NULL,
              dominance REAL NOT NULL,
              energy REAL NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS plugins (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL UNIQUE,
              version TEXT NOT NULL,
              type TEXT NOT NULL,
              enabled INTEGER NOT NULL DEFAULT 0,
              entrypoint TEXT NOT NULL,
              manifest_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
              id TEXT PRIMARY KEY,
              actor TEXT NOT NULL,
              action TEXT NOT NULL,
              target_type TEXT NOT NULL,
              target_id TEXT,
              created_at TEXT NOT NULL,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS runtime_events (
              id TEXT PRIMARY KEY,
              event_type TEXT NOT NULL,
              payload_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              handled_at TEXT,
              status TEXT NOT NULL DEFAULT 'new'
            );

            CREATE TABLE IF NOT EXISTS app_settings (
              key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at, description) VALUES (?, ?, ?)",
            ("001", utc_now(), "Initial MVP schema"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO emotion_states(id, pleasure, arousal, dominance, energy, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("default", 0.0, 0.0, 0.0, 100.0, utc_now()),
        )


def database_file() -> Path:
    return DATABASE_PATH

