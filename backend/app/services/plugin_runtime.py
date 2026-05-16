from __future__ import annotations

import json
from pathlib import Path

from ..config import PLUGIN_DIR
from ..database import connect, utc_now
from .event_bus import event_bus


class PluginRuntime:
    def scan(self) -> list[dict]:
        PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
        found = []
        for manifest_path in PLUGIN_DIR.glob("*/manifest.json"):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            now = utc_now()
            plugin_id = manifest["name"]
            with connect() as conn:
                conn.execute(
                    """
                    INSERT INTO plugins(id, name, version, type, enabled, entrypoint, manifest_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                      version = excluded.version,
                      type = excluded.type,
                      entrypoint = excluded.entrypoint,
                      manifest_json = excluded.manifest_json,
                      updated_at = excluded.updated_at
                    """,
                    (
                        plugin_id,
                        manifest["name"],
                        manifest["version"],
                        manifest["type"],
                        1 if manifest.get("enabled") else 0,
                        str(manifest_path.parent / manifest["entrypoint"]),
                        json.dumps(manifest, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
            found.append(manifest)
        return found

    def list_plugins(self) -> list[dict]:
        self.scan()
        with connect() as conn:
            rows = conn.execute("SELECT * FROM plugins ORDER BY name ASC").fetchall()
        return [dict(row) for row in rows]

    def set_enabled(self, name: str, enabled: bool) -> dict:
        with connect() as conn:
            conn.execute(
                "UPDATE plugins SET enabled = ?, updated_at = ? WHERE name = ?",
                (1 if enabled else 0, utc_now(), name),
            )
            row = conn.execute("SELECT * FROM plugins WHERE name = ?", (name,)).fetchone()
        event_bus.publish("plugin.enabled" if enabled else "plugin.disabled", {"name": name})
        return dict(row) if row else {}


plugin_runtime = PluginRuntime()

