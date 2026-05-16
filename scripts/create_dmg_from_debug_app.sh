#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/frontend/flutter_app/build/macos/Build/Products/Debug/flutter_app.app"
OUT="$ROOT/Aether_Dev_Debug.dmg"

if [ ! -d "$APP" ]; then
  echo "Missing app. Run scripts/build_macos_debug_app.sh first." >&2
  exit 1
fi

rm -f "$OUT"
hdiutil create -volname "Aether Dev Debug" -srcfolder "$APP" -ov -format UDZO "$OUT"

echo "DMG: $OUT"

