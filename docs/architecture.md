# Architecture

The MVP uses a local-first architecture:

```text
Flutter macOS app
  -> HTTP/WebSocket
FastAPI local backend
  -> SQLite
  -> local vector store abstraction
  -> plugin runtime
```

The backend is the system authority for conversations, memories, emotion state, plugin manifests, audit logs, and runtime events.

## MVP Boundary

The MVP must prove this loop:

```text
chat -> persist messages -> restart -> restore history -> write memory -> retrieve memory -> inspect in developer console
```

Advanced systems remain planned:

- Rust emotion engine
- Chroma/LanceDB/Weaviate adapter
- full Flutter developer dashboard
- macOS app packaging
- model adapters
- REM automation
- multi-agent social layer
- voice, avatar, action, and perception plugins

