#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/frontend/flutter_app"
flutter build macos --debug

echo "Debug app: $ROOT/frontend/flutter_app/build/macos/Build/Products/Debug/flutter_app.app"

