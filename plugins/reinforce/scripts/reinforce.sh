#!/usr/bin/env bash
set -euo pipefail
if [ -n "${CLAUDE_PLUGIN_OPTION_path:-}" ]; then
    cat "$CLAUDE_PLUGIN_OPTION_path"
fi
