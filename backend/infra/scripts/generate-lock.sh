#!/usr/bin/env bash
set -euo pipefail

# Generate a pinned requirements file at the repository root using the
# backend virtualenv if available, otherwise fall back to `python` on PATH.
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
LOCK_PATH="$BACKEND_DIR/../requirements-lock.txt"

VENV_PY="$BACKEND_DIR/.venv/Scripts/python.exe"
if [ -x "$VENV_PY" ]; then
  "$VENV_PY" -m pip freeze > "$LOCK_PATH"
else
  python -m pip freeze > "$LOCK_PATH"
fi
echo "Wrote $LOCK_PATH"
#!/usr/bin/env bash
set -euo pipefail

# Generates backend/requirements-lock.txt by installing the top-level
# requirements into a local .venv and freezing installed package versions.
# Works on Linux/macOS/WSL. On Windows, run the equivalent commands in PowerShell.


ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
# Prefer an active venv's python, fall back to available system python
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
else
  # try common python executables
  for p in python3.14 python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
      PYTHON="$p"
      break
    fi
  done
fi

if [ -z "${PYTHON:-}" ]; then
  echo "Error: no suitable python executable found (tried python3.14, python3, python)."
  exit 1
fi

# ensure venv exists, create if missing (use chosen python)
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv in $VENV_DIR with $PYTHON"
  "$PYTHON" -m venv "$VENV_DIR"
fi

# prefer venv python executables (cross-platform)
if [ -x "$VENV_DIR/bin/python" ]; then
  PYTHON="$VENV_DIR/bin/python"
elif [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  PYTHON="$VENV_DIR/Scripts/python.exe"
fi

echo "Using python: $PYTHON"

# Upgrade pip and install current requirements
"$PYTHON" -m pip install --upgrade pip setuptools wheel
"$PYTHON" -m pip install -r requirements.txt

# Freeze to lockfile
"$PYTHON" -m pip freeze > requirements-lock.txt

echo "Wrote $ROOT_DIR/requirements-lock.txt"
