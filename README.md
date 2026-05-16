# Aether Dev

<div align="center">

**macOS Digital Life System — Long Memory, Real Emotion, Agent-Native**

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Flutter-macOS-blue.svg)](https://flutter.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-3%2F3%20passed-brightgreen.svg)](#)

</div>

Aether Dev is a macOS developer-side foundation for a long-memory digital life system — not a passive chatbot, but a persistent digital entity with structured memory architecture, emotion modeling, and autonomous reflection cycles.

## Architecture

```
┌────────────────────────────────────────────┐
│  Flutter macOS App (Dart)                  │
│  ChatScreen · DeveloperDashboard · Memory │
├────────────────────────────────────────────┤
│  FastAPI Backend (Python 3.13)            │
│  ┌──────────┬──────────┬────────────────┐ │
│  │ Routers  │ Services │ Plugins        │ │
│  │ health   │ chat     │ example_memory │ │
│  │ convos   │ memory   │ (extensible)   │ │
│  │ chat     │ emotion  │                │ │
│  │ memory   │ audit    │                │ │
│  │ emotion  │ event    │                │ │
│  │ dev      │ embed    │                │ │
│  │ plugins  │ vector   │                │ │
│  │ WebSocket│ model    │                │ │
│  └──────────┴──────────┴────────────────┘ │
├────────────────────────────────────────────┤
│  SQLite + Vector Store + Plugin Runtime   │
│  macOS Application Support sandbox        │
└────────────────────────────────────────────┘
```

## Key Features

### L1 / L2 / L3 Memory System
- **L1** — Conversation context window with configurable message limit
- **L2** — Auto-extracted long-term memories surfaced during conversation
- **L3** — Persistent vector-store entries with embedding support (mock, OpenAI, Chroma, LanceDB)

### PAD Emotion Engine
- Pleasure-Arousal-Dominance emotional state model
- Energy level tracking independent of emotion
- State update API with event-bus notification

### Autonomous REM Cycle
- Manual trigger endpoint (`POST /developer/rem/run`)
- Memory consolidation via service pipeline
- Runtime event logging per REM pass

### Plugin System
- Manifest-based plugin discovery from `plugins/` directory
- Enable / disable at runtime via API
- Example memory plugin shipped

### Developer Dashboard
- Runtime status viewer (pid, uptime, memory count, emotion state)
- Audit log browser
- Structured log viewer
- Flutter macOS native window

## Quick Start

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Health check
curl http://127.0.0.1:8000/health

# Send a message
curl -X POST http://127.0.0.1:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello"}'

curl -X POST http://127.0.0.1:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{"content":"What can you remember about me?"}'

# Flutter frontend
cd frontend/flutter_app
flutter run -d macos
```

## API Endpoints (21 routes)

| Category | Method | Path |
|----------|--------|------|
| Health | `GET` | `/health` |
| Conversations | `POST` `/GET` | `/conversations` |
| Conversations | `GET` | `/conversations/{id}/messages` |
| Chat | `POST` | `/chat/message` |
| Chat | `WS` | `/ws/chat/{id}` |
| Memory | `POST` | `/memory/write` |
| Memory | `GET` | `/memory/query` |
| Memory | `GET` | `/memory/recent` |
| Memory | `DELETE` | `/memory/{id}` |
| Memory | `POST` | `/memory/{id}/level/{level}` |
| Emotion | `GET` | `/emotion/status` |
| Emotion | `POST` | `/emotion/update` |
| Developer | `GET` | `/developer/runtime` |
| Developer | `GET` | `/developer/logs` |
| Developer | `GET` | `/developer/audit` |
| Developer | `POST` | `/developer/rem/run` |
| Plugins | `GET` | `/plugins` |
| Plugins | `POST` | `/plugins/{name}/enable` |
| Plugins | `POST` | `/plugins/{name}/disable` |

## Test Results

```
backend:  3/3 passed  (FastAPI endpoint tests)
flutter:  1/1 passed  (widget tests)
analyze:  No issues found
```

## Project Structure

```
Aether_Dev/
├── backend/           FastAPI backend (Python)
│   ├── app/
│   │   ├── routers/    21 API route handlers
│   │   ├── services/   8 service modules
│   │   └── tests/      MVP test suite
│   └── scripts/        Build & start scripts
├── frontend/          Flutter macOS app (Dart)
│   └── flutter_app/
│       ├── lib/        Screens, models, services
│       └── macos/      Native macOS runner
├── plugins/           Plugin manifests & implementations
├── docs/              Architecture, API, roadmap docs
└── scripts/           CI scripts (test, build, package)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.115, Uvicorn, Python 3.13 |
| Database | SQLite (via aiosqlite) |
| Vector Store | Local JSON + Chroma / LanceDB adapters |
| Frontend | Flutter 3.x, Dart, macOS native |
| Packaging | PyInstaller + macOS .dmg |
| Testing | Pytest, Flutter test |

## Roadmap

More details in [docs/evolution_roadmap.md](docs/evolution_roadmap.md). The MVP is the stable base — real model gateway, WebSocket streaming UI, Chroma/LanceDB backends, and release packaging are the next increment.

## License

MIT — see [LICENSE](LICENSE).
