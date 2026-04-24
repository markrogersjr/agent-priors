#!/usr/bin/env python3
"""
Compose the proposed markdown content for a PreToolUse hook.

Reads the hook payload from stdin and produces the content that the tool, if accepted, would
leave on disk. For `Write`, that is `tool_input.content` verbatim. For `Edit`, it is the current
file contents with `old_string` replaced by `new_string` (first occurrence, or all occurrences
when `replace_all` is true). When no tool context is provided -- e.g. the `render-active-plan`
hook passes only `file_path` -- the current file is rendered as-is.

The composed content is written to `/tmp/markdown-preview/<basename>.md` and that path is
printed on stdout so the caller can hand it to pandoc. The dedicated `markdown-preview/` subdir
avoids clobbering any original `.md` files the user may have sitting directly in `/tmp/`. Exits
silently with no output if the target is not a `.md` file or the source file is missing.
"""
import json
import sys
from pathlib import Path

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
tool_input = data.get('tool_input', {})
file_path = tool_input.get('file_path', '')

if not file_path.endswith('.md'):
    sys.exit(0)

match tool_name:
    case 'Write':
        content = tool_input.get('content', '')
    case 'Edit':
        try:
            current = Path(file_path).read_text()
        except FileNotFoundError:
            sys.exit(0)
        old_string = tool_input.get('old_string', '')
        new_string = tool_input.get('new_string', '')
        replace_all = tool_input.get('replace_all', False)
        content = (
            current.replace(old_string, new_string)
            if replace_all
            else current.replace(old_string, new_string, 1)
        )
    case _:
        try:
            content = Path(file_path).read_text()
        except FileNotFoundError:
            sys.exit(0)

preview_dir = Path('/tmp/markdown-preview')
preview_dir.mkdir(exist_ok=True)
temp_md = preview_dir / Path(file_path).name
temp_md.write_text(content)
print(temp_md)
