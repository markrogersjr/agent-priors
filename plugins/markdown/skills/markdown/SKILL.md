---
name: markdown
description: Describes the markdown plugin's auto-render hooks. Loaded when Claude is about to create or edit a `.md` file, or call `ExitPlanMode` — informs Claude that the user sees the proposed file as rendered HTML in the browser before the approval prompt, in addition to any inline view, so no extra rendering step is needed.
---

# Markdown auto-render

The plugin adds two hooks:
- `PreToolUse(Edit|Write)` on any `.md` file → renders the *proposed* content (from `tool_input.content` for Write, or by applying `old_string`→`new_string` to the current file for Edit) and opens it in the browser before the approval prompt.
- `PreToolUse(ExitPlanMode)` → re-renders the newest file in `~/.claude/plans/` right before the ExitPlanMode approval, so the user reads the exact version being submitted.

This is purely additive. Whatever Claude outputs inline is unchanged. The browser render is a supplement that makes long markdown readable while deciding whether to accept.
