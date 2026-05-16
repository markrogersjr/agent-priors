#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0"]
# ///

"""
MCP server exposing the poll plugin's bash CLI as callable tools.

Tools mirror `scripts/poll` subcommands: start, list, logs, stop. Each tool
delegates to the bash script and returns its stdout, stderr, and exit code.
"""

import os
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

plugin_root = Path(os.environ['CLAUDE_PLUGIN_ROOT'])
poll = plugin_root / 'scripts' / 'poll'
server = FastMCP('poll')

def run(*arguments: str) -> str:
    result = subprocess.run([str(poll), *arguments], capture_output=True, text=True, timeout=30)
    sections = []
    if result.stdout:
        sections.append(result.stdout.rstrip())
    if result.stderr:
        sections.append(f'[stderr]\n{result.stderr.rstrip()}')
    sections.append(f'[exit code: {result.returncode}]')
    return '\n'.join(sections)

@server.tool()
def poll_start(directory: str, instructions: str) -> str:
    """
    Start a poller watching `directory` for event files. Each new file is
    processed per `instructions`, a path to a markdown file whose contents
    are injected into the spawned session at every SessionStart (so they
    survive compaction).

    The poller runs as a fresh Claude Code session inside the `poll` tmux
    socket. Session name equals `basename(directory)`. The session's cwd is
    set to an ephemeral empty directory so no project `CLAUDE.md` is
    auto-discovered; only `instructions` shapes the session's behavior.

    Parameters
    ----------
    directory: directory whose new files become events
    instructions: path to a markdown file describing how to process events
    """
    return run('start', directory, instructions)

@server.tool()
def poll_list() -> str:
    """List running pollers with their watched directories and instructions paths."""
    return run('list')

@server.tool()
def poll_logs(name: str) -> str:
    """Capture recent output from a poller's tmux pane."""
    return run('logs', name)

@server.tool()
def poll_stop(name: str) -> str:
    """Stop a poller."""
    return run('stop', name)

if __name__ == '__main__':
    server.run()
