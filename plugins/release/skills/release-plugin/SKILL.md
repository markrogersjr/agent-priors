---
name: release-plugin
description: Bump a plugin's version, commit pending changes, push, and prompt for marketplace reload — for an agent-priors plugin source repo
---

# /release-plugin

Releases a Claude Code plugin from its source repo. Bumps the patch version, commits pending changes alongside the bump, pushes to origin, and prints the follow-up commands the user has to type (`/plugin` to refresh the marketplace, `/reload-plugins` to rebuild the version-pinned cache).

## When to use

After editing a plugin under `~/workspace/<repo>/plugins/<name>/`. Never run against the marketplace cache at `~/.claude/plugins/marketplaces/<name>/` — that's a read-only-by-convention installed copy.

## Steps

1. **Identify the plugin.** Use `$ARGUMENTS` as the plugin name if given (`/release-plugin remote`); otherwise infer from cwd (look for a `plugins/<name>/` ancestor). Ask if neither resolves.

2. **Confirm source repo, not cache.** `git rev-parse --show-toplevel` must land under `~/workspace/`. If it's under `~/.claude/plugins/`, abort and tell the user to `cd` to the source.

3. **Inspect what changed.** `git status --short` plus `git diff plugins/<name>` to understand what's about to ship. If there are uncommitted changes outside the plugin's directory, ask the user whether to include them (default: no).

4. **Bump the version.** Read `plugins/<name>/.claude-plugin/plugin.json`, increment the patch component of `version` (e.g. `0.3.9` → `0.3.10`). If the user passed `--minor` or `--major`, bump that segment and zero the lower ones.

5. **Stage and commit.** Stage only paths under `plugins/<name>/`. Commit subject: `<name> <new-version>: <one-line summary>`. Body: short bullets if the change has multiple notable parts.

6. **Push.** `git push origin "$(git rev-parse --abbrev-ref HEAD)"`. Don't force-push on rejection — surface the error.

7. **Print follow-up.** Tell the user to run `/plugin` (Update marketplace → agent-priors) then `/reload-plugins`. These are built-in slash commands; you cannot trigger them yourself.
