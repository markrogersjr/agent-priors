---
name: remote
description: This skill should be used whenever a command should run on the configured
  remote server rather than locally — e.g. "run on the remote", "kick off training on
  dgx", "tail the log on the box", "ssh in and ...", or any GPU/long-running job that
  belongs on the remote. Provides the exact Bash invocation needed to sync code and
  execute the command, with output visible in the transcript.
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/remote:*)"]
---

# Remote

Sync the local repo to the configured remote server and execute a command there. The
`remote` script auto-commits any uncommitted changes, force-pushes the current branch,
syncs the remote checkout, and then runs the command over SSH.

## How to invoke

Issue a single **Bash** tool call:

    ${CLAUDE_PLUGIN_ROOT}/scripts/remote <command>

Do NOT:

- Pass the command as the Skill tool's `args` parameter. The `args` are silently
  discarded — nothing runs, and the user sees only "Skill(remote:remote)" with no
  visible command. Always route through the Bash tool so the full argv renders in the
  transcript.
- Invoke the slash command form `/remote <command>`. Slash commands are user-typed;
  routing through them obscures the argv from the user.

The Bash tool path is the only one that produces a visible, auditable command in the
user's transcript.

## Modes

Foreground (default) — output streams back. Use for short jobs and inspections.

    ${CLAUDE_PLUGIN_ROOT}/scripts/remote nvidia-smi

Detached (`-t`) — runs in a `tmux` session on the remote, logs to
`<remote_dir>/logs/remote-<pid>.log`, returns immediately. Use for training runs and
anything longer than a couple minutes.

    ${CLAUDE_PLUGIN_ROOT}/scripts/remote -t uv run train.py

Sync only — pass no command to push code without executing anything.

    ${CLAUDE_PLUGIN_ROOT}/scripts/remote

## Per-call overrides

Flags must come before the command (and before `-t`). Any unspecified flag falls back
to the value in `~/.claude/settings.json`.

    ${CLAUDE_PLUGIN_ROOT}/scripts/remote --alias=lightning <command>
    ${CLAUDE_PLUGIN_ROOT}/scripts/remote --directory=/other/path <command>
    ${CLAUDE_PLUGIN_ROOT}/scripts/remote --alias=lightning --author="Name <email>" -t <command>

## Configuration

Configured via the `/plugin` slash command, or by editing `~/.claude/settings.json`
under `pluginConfigs["remote@agent-priors"].options`: `alias`, `author`, `directory`.
The script reads these at runtime.

## Checking detached job status

`-t` mode pipes all output to a per-session log file. Tail it via:

    ssh <REMOTE_ALIAS> "tail -200 <REMOTE_DIR>/logs/remote-<pid>.log"
