#!/usr/bin/env bash
set -euo pipefail

# Export a requirements.txt for environments that need pip installs
# Usage: run this from the repository root where pyproject.toml lives

if ! command -v poetry >/dev/null 2>&1; then
  echo "poetry is required to export requirements. Install poetry first." >&2
  exit 2
fi

poetry export -f requirements.txt --output backend/requirements.txt --without-hashes
echo "Exported backend/requirements.txt"
