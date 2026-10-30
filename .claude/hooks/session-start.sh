#!/bin/bash
# SessionStart hook for Claude Code cloud sessions:
#   1. Headroom (headroom-ai) in its own virtualenv, so large JSON / command output can be
#      compressed before it is read (tools/hrc), saving context tokens.
#   2. The renderer's npm packages (three, playwright-core) in promo/three.
# Idempotent: re-running only installs what is missing.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
VENV="$HOME/.headroom-venv"

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c "import headroom" 2>/dev/null; then
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q "headroom-ai"
fi

if [ -f "$REPO/promo/three/package.json" ]; then
  (cd "$REPO/promo/three" && npm install --no-audit --no-fund --no-update-notifier --loglevel=error)
fi

# make `hrc` available as a command for the rest of the session
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export HEADROOM_VENV=\"$VENV\"" >> "$CLAUDE_ENV_FILE"
  echo "export PATH=\"$REPO/tools:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
