# macOS Packaging Plan

MVP packaging target:

1. Build Flutter as a macOS `.app`.
2. Package FastAPI backend with PyInstaller.
3. Bundle the backend executable inside the Flutter app resources.
4. Launch the backend as a local child process.
5. Connect to `127.0.0.1:<port>` via HTTP/WebSocket.
6. Store data under `~/Library/Application Support/Aether Dev/`.

The Flutter project already contains `AppLauncher` and `StoragePaths` service stubs for this.

## Current Scripts

Build backend binary:

```bash
cd /Users/lixie/Desktop/Aether_Dev
bash scripts/build_backend_binary.sh
```

Build Flutter macOS debug app:

```bash
bash scripts/build_macos_debug_app.sh
```

Create a debug DMG from the built app:

```bash
bash scripts/create_dmg_from_debug_app.sh
```

The current DMG is a development artifact. Release packaging still needs:

- bundle `backend/dist/aether_backend` into app resources
- launch bundled backend instead of dev script
- Developer ID signing
- notarization
- Sparkle feed generation

## Later Release Requirements

- Developer ID signing
- notarization
- `.dmg` generation
- Sparkle update feed
- migration-before-launch
- backup-before-upgrade
- rollback if migration fails
