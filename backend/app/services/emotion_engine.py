from __future__ import annotations

import math
from datetime import datetime, timezone

from ..database import connect, utc_now
from .event_bus import event_bus


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class EmotionEngine:
    def status(self) -> dict:
        with connect() as conn:
            row = conn.execute("SELECT * FROM emotion_states WHERE id = 'default'").fetchone()
        return dict(row)

    def decay(self) -> dict:
        state = self.status()
        updated_at = datetime.fromisoformat(state["updated_at"])
        now = datetime.now(timezone.utc)
        hours = max((now - updated_at).total_seconds() / 3600, 0.0)
        factor = math.exp(-0.08 * hours)
        return self.update(
            pleasure=(state["pleasure"] * factor) - state["pleasure"],
            arousal=(state["arousal"] * factor) - state["arousal"],
            dominance=(state["dominance"] * factor) - state["dominance"],
            energy=max(state["energy"] - hours * 0.8, 0) - state["energy"],
        )

    def update(self, pleasure: float = 0.0, arousal: float = 0.0, dominance: float = 0.0, energy: float = 0.0) -> dict:
        state = self.status()
        next_state = {
            "id": "default",
            "pleasure": clamp(state["pleasure"] + pleasure, -1.0, 1.0),
            "arousal": clamp(state["arousal"] + arousal, -1.0, 1.0),
            "dominance": clamp(state["dominance"] + dominance, -1.0, 1.0),
            "energy": clamp(state["energy"] + energy, 0.0, 100.0),
            "updated_at": utc_now(),
        }
        with connect() as conn:
            conn.execute(
                """
                UPDATE emotion_states
                SET pleasure = ?, arousal = ?, dominance = ?, energy = ?, updated_at = ?
                WHERE id = 'default'
                """,
                (
                    next_state["pleasure"],
                    next_state["arousal"],
                    next_state["dominance"],
                    next_state["energy"],
                    next_state["updated_at"],
                ),
            )
        event_bus.publish("emotion.updated", next_state)
        return next_state

    def apply_text_event(self, text: str) -> dict:
        positive = ["好", "喜欢", "成功", "谢谢", "棒", "优秀", "happy", "great"]
        negative = ["坏", "失败", "讨厌", "错误", "崩", "难受", "angry", "bad"]
        p_delta = 0.04 if any(word in text.lower() for word in positive) else 0.0
        p_delta -= 0.05 if any(word in text.lower() for word in negative) else 0.0
        arousal = min(len(text) / 800, 0.06)
        return self.update(pleasure=p_delta, arousal=arousal, dominance=0.01, energy=-0.2)


emotion_engine = EmotionEngine()

