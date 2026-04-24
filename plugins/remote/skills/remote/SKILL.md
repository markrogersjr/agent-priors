---
name: remote
description: Run commands on a remote server via SSH with automatic code sync
---

# Remote

Run commands on a remote server. The `remote` script auto-commits local changes, force-pushes to the current branch, and syncs the remote checkout before executing.

## Usage

```bash
# sync code and stream command output
/remote <command>

# sync code and run in detached tmux session (returns immediately)
/remote -t <command>

# just sync code, no command
/remote

# override any configured option for a single invocation
/remote --alias=lightning <command>
/remote --directory=/other/path <command>
/remote --alias=lightning --author="Name <email>" -t <command>
```

Flags (`--alias=...`, `--author=...`, `--directory=...`) must come before the command and before `-t`. Any unspecified flag falls back to the value in `~/.claude/settings.json`.

## Configuration

Configure via the `/plugin` slash command in Claude Code, or edit `~/.claude/settings.json` directly:

```json
{
  "pluginConfigs": {
    "remote@agent-priors": {
      "options": {
        "alias": "<ssh host alias>",
        "author": "<git author, e.g. Name <email>>",
        "directory": "<remote working directory>"
      }
    }
  }
}
```

The script reads these fields from `settings.json` at runtime.

## Checking Job Status

The `-t` mode pipes all output to `logs/remote-<pid>.log` on the remote via `tmux pipe-pane`. To check:

```bash
ssh <REMOTE_ALIAS> "tail -200 <REMOTE_DIR>/logs/<session>.log"
```
