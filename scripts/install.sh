#!/usr/bin/env bash
# Backward-compatible Claude default; native Codex support is explicit.
set -euo pipefail
exec python3 "$(dirname "${BASH_SOURCE[0]}")/install.py" "$@"
