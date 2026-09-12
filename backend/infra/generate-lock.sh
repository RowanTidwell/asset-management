#!/usr/bin/env bash
set -euo pipefail

# Infra copy of generate-lock for discoverability under backend/infra
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
else
  for p in python3.14 python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
      PYTHON="$p"
      break
    fi
  done
fi

if [ -z "${PYTHON:-}" ]; then
  echo "Error: no suitable python executable found"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON" -m venv "$VENV_DIR"
fi

if [ -x "$VENV_DIR/bin/python" ]; then
  PYTHON="$VENV_DIR/bin/python"
elif [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  PYTHON="$VENV_DIR/Scripts/python.exe"
fi

"$PYTHON" -m pip install --upgrade pip setuptools wheel
"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" -m pip freeze > requirements-lock.txt
echo "Wrote $ROOT_DIR/requirements-lock.txt"
