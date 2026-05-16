# Aether Dev

Aether Dev is a macOS developer-side foundation for a long-memory digital life system.

Current MVP focus:

- FastAPI local backend
- SQLite conversation persistence
- L1/L2/L3 memory boundaries
- Local vector-store abstraction
- PAD emotion and energy state
- Developer runtime endpoints
- Plugin manifest scanning
- Audit logs and runtime events

Future phases are not removed. They are documented as staged upgrades so the first version can run before advanced systems are added.

## Location

Project source:

```text
/Users/lixie/Desktop/Aether_Dev
```

Runtime data:

```text
~/Library/Application Support/Aether Dev/
  aether.sqlite3
  vector_store/
  logs/
  plugins/
  backups/
```

## Backend Quick Start

```bash
cd /Users/lixie/Desktop/Aether_Dev/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Create a conversation and send a message:

```bash
curl -X POST http://127.0.0.1:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"MVP Test"}'

curl -X POST http://127.0.0.1:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"content":"记住：这个项目最终所有功能都要实现，MVP 只是底座。"}'
```

Developer endpoints require:

```text
Authorization: Bearer dev-admin-token
```

## Tests

```bash
cd /Users/lixie/Desktop/Aether_Dev/backend
pytest
```

Run all current checks:

```bash
cd /Users/lixie/Desktop/Aether_Dev
bash scripts/test_all.sh
```

Start backend from the project root:

```bash
cd /Users/lixie/Desktop/Aether_Dev
bash scripts/start_backend.sh
```

Start Flutter frontend:

```bash
cd /Users/lixie/Desktop/Aether_Dev/frontend/flutter_app
flutter run -d macos
```

Start Flutter and let it launch the development backend:

```bash
cd /Users/lixie/Desktop/Aether_Dev/frontend/flutter_app
AETHER_PROJECT_ROOT=/Users/lixie/Desktop/Aether_Dev flutter run -d macos
```

## Current API

- `GET /health`
- `POST /conversations`
- `GET /conversations`
- `GET /conversations/{id}/messages`
- `POST /chat/message`
- `GET /memory/query`
- `POST /memory/write`
- `GET /emotion/status`
- `POST /emotion/update`
- `GET /developer/runtime`
- `GET /developer/logs`
- `GET /developer/audit`
- `POST /developer/rem/run`
- `GET /plugins`
- `POST /plugins/{name}/enable`
- `POST /plugins/{name}/disable`
- `WS /ws/chat/{conversation_id}`

## Full Scope

The MVP is not the final feature set. The full feature roadmap is kept in:

```text
docs/evolution_roadmap.md
```

Current implementation status is tracked in:

```text
docs/current_status.md
```
