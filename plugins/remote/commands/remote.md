---
description: "Sync code to remote and run a command via SSH"
argument-hint: "[-t] <command>"
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/remote:*)"]
---

```!
"${CLAUDE_PLUGIN_ROOT}/scripts/remote" $ARGUMENTS
```
