# Agent Priors

## Plugins

### analyze

Deeply analyzes data to meet an objective. The `/analyze` command orchestrates an iterative investigation: a `scout` subagent identifies every relevant data source (local files, codebase, git history, remote hosts, databases, APIs, collaboration tools, observability, object storage, notebooks, web) along with the specific tables, columns, endpoints, commits, and files that bear on the objective. An `investigator` then analyzes each source with evidence-backed claims. A `web-researcher` grounds findings in external sources. An `adversary` adversarially challenges every load-bearing claim. The orchestrator loops, dispatching any subagent any number of times, until the objective is answered and every claim has survived or been revised. A `synthesizer` produces a self-contained HTML report at `./analysis-<slug>.html` with embedded plotly charts, evidence citations, and prioritized recommendations. All subagents are registered at plugin level so Claude can invoke them directly via `Task` outside the orchestrator.

### markdown

Renders markdown files in the browser. A PostToolUse hook fires after every Write tool call. If the written file has a `.md` extension, the hook converts it to HTML via pandoc with GitHub dark styling and MathJax support, then opens the result.

### persist

Preserves conversation context across compaction events. When Claude Code's context window fills up and triggers compaction, the PreCompact hook forks a detached subprocess that summarizes recent conversation history via `claude -p`. On the next prompt, the plugin injects that summary as additional context. The summarizer targets plan progress, current task state, key decisions, and open blockers.

### reinforce

Injects a file into every prompt. The UserPromptSubmit hook reads a user-configured file path and returns its contents as hook output, so the instructions appear in every turn regardless of compaction. Useful for project-specific rules that must not be lost.

### remote

Runs commands on a remote server with automatic code sync. The script auto-commits local changes, force-pushes the current branch, and pulls on the remote before executing. Two modes: foreground (streams output back) and detached tmux (returns immediately with a session name and log path). Configured via SSH alias, git author, and remote working directory.

### review

Previews diffs in neovim before accepting. A PreToolUse hook intercepts Edit and Write tool calls, computes a word-level diff against the current file, and sends a syntax-highlighted conflict view to a running neovim instance via RPC. The hook polls the Claude Code permission prompt in tmux — when the user accepts or rejects, the diff buffer closes automatically and, on accept, opens the modified file at the first changed line.

### tighten

A skill that teaches declarative style and locality of reference, drawn from *Code Complete*'s span and live time metrics. It covers function signatures, variable creation, inline composition, indentation, chaining, parenthesis nesting, DRY, and pandas idioms. No hooks — invoked on demand before writing code.
