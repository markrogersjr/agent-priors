#!/usr/bin/env bash
set -euo pipefail

cat > /dev/null

[ -n "${POLL_DIR:-}" ] || exit 0
[ -n "${POLL_INSTRUCTIONS:-}" ] || exit 0
[ -f "$POLL_INSTRUCTIONS" ] || exit 0

watcher=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/watch

header=$(cat <<EOF
# Poller protocol

You watch \`$POLL_DIR\` for event files. Each file is one event.

## Setup (at session start)

1. Load \`Monitor\` if not yet available: call \`ToolSearch\` with \`select:Monitor\`.
2. Invoke \`Monitor\` with:
   - \`description\`: "watching $POLL_DIR for events"
   - \`command\`: \`$watcher $POLL_DIR\`
   - \`persistent\`: true

## Handling each event

Each notification from \`Monitor\` is the absolute path of a new event file.

1. Read the file with the \`Read\` tool.
2. Process it according to the instructions below.
3. Delete the file via \`Bash\`: \`rm <path>\`.
4. Respond with exactly one line: \`DONE: <basename>\`.

If you cannot handle the event, respond \`ERROR: unknown <basename>\`
and leave the file in place.

## Hard rules

- Never silently drop an event. Always respond \`DONE:\` or \`ERROR:\`.
- No free-form text outside \`DONE:\` / \`ERROR:\` lines.
- Never modify the instructions file unless explicitly asked.

## Instructions

EOF
)

protocol="$header

$(cat "$POLL_INSTRUCTIONS")"

jq -n --arg ctx "$protocol" \
    '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$ctx}}'
