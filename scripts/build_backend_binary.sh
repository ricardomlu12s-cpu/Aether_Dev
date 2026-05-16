#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
pyinstaller --clean --onefile --name aether_backend run_backend.py

echo "Backend binary: $ROOT/backend/dist/aether_backend"

