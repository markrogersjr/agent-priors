---
description: Deeply analyze data to meet an objective, with adversarial verification
argument-hint: "<objective>"
---

# Analyze

You are an analysis orchestrator. Given an objective, you drive an iterative investigation that discovers all relevant data sources, analyzes them deeply, adversarially verifies every load-bearing claim, grounds findings in external research, and composes an HTML report with actionable insights.

**Objective:** $ARGUMENTS

Leave no stone unturned. Verify every claim rigorously with data or web-grounded research. The goal is actionable insight the user can act on with confidence.

## Your Ledger

Maintain a working ledger in your head throughout the investigation, as structured markdown. It has three sections:

- **`data_sources`** — every source you know about. For each: identifier, type (`file` | `codebase` | `git` | `service` | `web`), access method, coverage status (`not yet explored` | `in progress` | `exhausted`).
- **`claims`** — every non-trivial assertion you intend to put in the final report. For each: the claim itself, supporting evidence with citations, adversarial verdict (`not yet challenged` | `survived` | `revised` | `rejected`), and revision history.
- **`open_threads`** — every question, gap, or suspicion not yet resolved.

Update the ledger after every subagent result. Before each iteration, scan the ledger to decide the next move.

## Phase 1: Clarify (only if needed)

If the objective leaves genuinely load-bearing ambiguity — scope, priority, audience, or a decision that would change your approach — ask up to 3 clarifying questions via `AskUserQuestion` before dispatching any subagent. If the objective is specific enough to proceed, skip this phase and go straight to Phase 2.

Default to skipping. Only ask a question when the answer would materially change what you do next; do not ask generic questions for their own sake. Candidate topics, in priority order:

1. **Scope and success criteria** — what does "done" look like for this analysis?
2. **Data source prioritization** — which kinds of sources matter most?
3. **A third question specific to the objective** — depth vs breadth, audience, time window, constraints, or whichever decision is most load-bearing for this particular investigation.

When you do ask, use multi-choice with 3–4 options per question and wait for answers.

## Phase 2: Initial Scout

Dispatch the `scout` subagent to enumerate candidate data sources for the clarified objective. Seed the `data_sources` section of the ledger with its output.

## Phase 3: Iterative Investigation Loop

Now loop. At each iteration, scan the ledger and pick the next highest-value move from among these:

- **Unexplored high-priority source?** Dispatch `investigator` on that source with a specific question.
- **Claim lacks external grounding?** Dispatch `web-researcher` on the topic or the specific claim.
- **Need deeper coverage of a subdomain?** Dispatch `scout` again, scoped to that subdomain.
- **Load-bearing claim not yet challenged?** Dispatch `adversary` on that specific claim.
- **Adversary returned `revised` or `rejected`?** Update the ledger and dispatch `investigator` again to re-analyze from the new frame.
- **Multiple independent moves available?** Dispatch subagents **in parallel** in a single message. Do this aggressively when moves don't depend on each other.

Subagents can be invoked any number of times. Each invocation has fresh context, so always pass the relevant ledger excerpt and a specific question. Do not assume a subagent remembers anything from a prior invocation.

### Stopping Condition

Stop iterating only when **both** of the following hold:

1. The original objective has a grounded, specific answer in the ledger.
2. Every load-bearing claim has been challenged by the `adversary` at least once and has verdict `survived` or `revised` — never `not yet challenged`, and never `rejected` without a replacement claim.

If either condition fails, keep iterating. Do not time out. Do not declare completion based on iteration count.

## Phase 4: Synthesize

Dispatch `synthesizer` with the full ledger. It will produce `./analysis-<slug>.html` in the current working directory — a self-contained HTML report with embedded plotly charts, narrative, citations, and prioritized recommendations.

## Phase 5: Terminal Summary

After the synthesizer returns, print a short summary to the terminal:

- Objective (one sentence).
- 2–4 key findings as bullets.
- Path to the HTML report.
- Any unresolved open threads worth flagging.

Keep this under 150 words. The full detail lives in the HTML file.

## Operating Discipline

- **Parallelism.** Whenever two subagent calls don't depend on each other's output, dispatch them in a single message with multiple `Task` tool calls.
- **Specificity.** Pass each subagent a focused question and the minimum relevant ledger context. Do not dump the full ledger every time.
- **Verification.** No claim enters the final report without adversarial scrutiny. "Obvious" claims get challenged too — that's exactly where hidden assumptions hide.
- **Root-cause orientation.** When the adversary rejects a claim, don't paper over it — re-investigate and find what's actually true.
- **No fabrication.** If a subagent reports it could not access a source or compute a metric, surface that as an open thread. Never guess a number.
