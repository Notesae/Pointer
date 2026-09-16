#!/usr/bin/env bash
set -euo pipefail
ICEGEM_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ICEGEM_SCRIPT_DIR/install.py" "$@"
