# Current Status

## Implemented

- FastAPI backend
- SQLite schema and initialization
- macOS Application Support runtime data path
- conversation creation and message persistence
- mock chat response pipeline
- L1 context boundary
- L2 memory auto-write heuristic
- local vector-store abstraction
- memory query endpoint
- PAD emotion and energy state
- developer runtime endpoint
- audit logs
- runtime events
- manual REM endpoint
- plugin manifest scanning
- Flutter macOS project
- ChatScreen
- DeveloperDashboard
- Flutter API client
- backend tests
- Flutter analyze/test
- Flutter macOS debug `.app` build
- PyInstaller backend build script
- debug DMG creation script

## Verified

- Backend pytest passes.
- FastAPI actual `/health` endpoint works when launched with local port permission.
- Actual `/chat/message` request writes a conversation and memory candidate.
- Flutter `analyze` passes.
- Flutter widget test passes.
- `flutter build macos --debug` succeeds and produces `build/macos/Build/Products/Debug/flutter_app.app`.

## Next Work

- Add real model gateway instead of mock replies.
- Add richer memory viewer and manual memory editing.
- Add backend process launcher inside Flutter.
- Wire the existing Flutter `AppLauncher` into app startup.
- Bundle PyInstaller backend binary into Flutter app resources for release builds.
- Add WebSocket streaming UI.
- Add Chroma or LanceDB adapter behind `vector_store.py`.
- Add backup and restore endpoints.
- Add first packaging pass with PyInstaller + Flutter macOS build.
