#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0"]
# ///

"""
MCP server exposing the remote plugin's bash script as a callable tool.

The single `remote_run` tool synchronizes the local repository to the configured remote
server and executes a command there. The underlying bash script auto-commits any
uncommitted changes, force-pushes the current branch, syncs the remote checkout, then
runs the command over SSH (optionally in a detached `tmux` session for long jobs).
"""

import os
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

plugin_root = Path(os.environ['CLAUDE_PLUGIN_ROOT'])
script_path = plugin_root / 'scripts' / 'remote'

server = FastMCP('remote')

@server.tool()
def remote_run(
    command: str,
    detached: bool | None = False,
    cwd: str | None = None,
    alias: str | None = None,
    author: str | None = None,
    directory: str | None = None,
) -> str:
    """
    BEFORE calling this tool, emit a single inline message in your response — as
    plain assistant text, NOT a tool call — in this exact format, listing only
    the arguments you are actually passing:

        remote(
            command="<command>",
            alias="<alias>",
        )

    The user cannot see MCP tool call arguments in the Claude Code UI without
    manually expanding the call (ctrl+o), and hook output renders only after the
    tool returns. Announcing inline first makes the command visible in real time
    while the (often long-running) sync + remote execution proceeds.

    Run a command on the configured remote server after syncing the local repository.

    The bash script auto-commits any uncommitted local changes, force-pushes the current
    branch, syncs the remote checkout, then executes the command over SSH. Output is
    captured and returned in full for foreground runs; detached runs return immediately
    after launching the remote `tmux` session.

    Parameters
    ----------
    command: str
        Shell command to execute on the remote. Pass an empty string to sync only.
    detached: bool | None = False
        If `True`, runs in a detached `tmux` session on the remote and returns
        immediately. Output is logged to `<remote_dir>/logs/remote-<pid>.log`. Use for
        jobs longer than a couple minutes (training runs, long evals).
    cwd: str | None = None
        Local working directory for the sync — git operations run from here. Defaults
        to the MCP server's startup directory, which is usually the user's project
        root.
    alias: str | None = None
        Override the configured SSH alias for this call.
    author: str | None = None
        Override the configured git author for this call.
    directory: str | None = None
        Override the configured remote working directory for this call.
    """
    arguments = [str(script_path)]
    if alias:
        arguments.append(f'--alias={alias}')
    if author:
        arguments.append(f'--author={author}')
    if directory:
        arguments.append(f'--directory={directory}')
    if detached:
        arguments.append('-t')
    if command:
        arguments.append(command)
    result = subprocess.run(arguments, capture_output=True, text=True, cwd=cwd)
    sections = []
    if result.stdout:
        sections.append(result.stdout.rstrip())
    if result.stderr:
        sections.append(f'[stderr]\n{result.stderr.rstrip()}')
    sections.append(f'[exit code: {result.returncode}]')
    return '\n'.join(sections)

if __name__ == '__main__':
    server.run()
