#!/usr/bin/env bash
set -euo pipefail
CATPAW_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$CATPAW_SCRIPT_DIR/install.py" "$@"
