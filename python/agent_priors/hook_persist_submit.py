import json
import os
import sys
import time
from pathlib import Path


def main():
    """
    UserPromptSubmit hook entry point for the persist plugin. Injects the compaction summary as additionalContext
    if available, waiting for a running summarizer if necessary.
    """
    session_id = json.load(sys.stdin).get('session_id', '')
    if not session_id:
        return
    summary_path = PERSIST_DIR / f'{session_id}.md'
    pid_path = PERSIST_DIR / f'{session_id}.pid'
    # wait for running summarizer
    if not summary_path.exists() and pid_path.exists():
        try:
            pid = int(pid_path.read_text())
        except ValueError:
            pid_path.unlink(missing_ok=True)
            return
        for _ in range(180):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                pid_path.unlink(missing_ok=True)
                break
            time.sleep(0.5)
    if summary_path.exists():
        json.dump(
            {'additionalContext': f'[Compaction Summary]\n{summary_path.read_text()}'},
            sys.stdout
        )


PERSIST_DIR = Path.home() / '.agent-priors' / 'persist'
