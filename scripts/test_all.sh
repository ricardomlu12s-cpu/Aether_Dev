#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT/backend"
pytest

cd "$ROOT/frontend/flutter_app"
flutter analyze
flutter test

