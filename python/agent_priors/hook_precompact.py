import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    """
    PreCompact hook entry point. Forks a detached summarizer subprocess and exits immediately so compaction
    proceeds without delay.
    """
    input_data = json.load(sys.stdin)
    session_id = input_data.get('session_id', '')
    transcript_path = input_data.get('transcript_path', '')
    if not session_id or not transcript_path:
        return
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    # kill existing summarizer if re-compacting
    if (pid_path := PERSIST_DIR / f'{session_id}.pid').exists():
        try:
            os.kill(int(pid_path.read_text()), 9)
        except (ProcessLookupError, ValueError):
            pass
    (PERSIST_DIR / f'{session_id}.md').unlink(missing_ok=True)
    pid_path.write_text(
        str(
            subprocess.Popen(
                ['agent-priors-persist-summarize', session_id, transcript_path],
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            .pid
        )
    )


def summarize():
    """
    Detached summarizer entry point. Reads the transcript, extracts recent user/assistant messages, pipes them
    to ``claude -p`` for summarization, writes the result to ``{session_id}.md``, and removes the PID file.
    """
    session_id = sys.argv[1]
    try:
        result = subprocess.run(
            [
                'claude', '-p', '--bare', '--model',
                os.environ.get('CLAUDE_PLUGIN_OPTION_model', 'sonnet'),
                SUMMARIZE_PROMPT
            ],
            input='\n\n'.join(
                [
                    f'{message["role"]}: {message["content"][:2000]}'
                    for message in reversed(
                        [json.loads(line) for line in open(sys.argv[2])]
                    )
                    if isinstance(message.get('content', ''), str)
                    and message.get('role') in ('user', 'assistant')
                ][:50][::-1]
            ),
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            (PERSIST_DIR / f'{session_id}.md').write_text(
                result.stdout.strip()
            )
    finally:
        (PERSIST_DIR / f'{session_id}.pid').unlink(missing_ok=True)


PERSIST_DIR = Path.home() / '.agent-priors' / 'persist'
SUMMARIZE_PROMPT = '''\
You are summarizing a Claude Code conversation that is about to be compacted \
(context window is full). Your summary will be injected into every subsequent \
prompt so the agent retains critical context.

Focus on:
1. PLAN PROGRESS: What was the overall goal? Which steps are done, which remain?
2. CURRENT TASK: What was the agent working on right before compaction? \
What files were being edited? What was the last tool call or decision?
3. KEY DECISIONS: Any architectural choices, rejected approaches, or constraints discovered.
4. BLOCKERS / OPEN QUESTIONS: Anything unresolved that the agent needs to remember.

Be concise. Use bullet points. Do NOT include code unless a specific line number \
or snippet is critical context. Target 300-500 words.'''
