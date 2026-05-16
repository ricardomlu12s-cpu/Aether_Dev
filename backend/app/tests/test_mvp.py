from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import ADMIN_TOKEN
from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_persists_and_creates_messages() -> None:
    conversation = client.post("/conversations", json={"title": "Test"}).json()
    response = client.post(
        "/chat/message",
        json={"conversation_id": conversation["id"], "content": "记住这个项目必须先完成 MVP 闭环"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == conversation["id"]
    messages = client.get(f"/conversations/{conversation['id']}/messages").json()
    assert len(messages) == 2


def test_admin_runtime_requires_token() -> None:
    assert client.get("/developer/runtime").status_code == 401
    response = client.get("/developer/runtime", headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    assert response.status_code == 200

