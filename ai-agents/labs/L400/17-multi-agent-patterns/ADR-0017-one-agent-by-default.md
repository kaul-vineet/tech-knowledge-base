# ADR-0017: One agent with tools by default; supervisor/worker only when the context does not fit

## Status
Accepted (2026-10-28). Kept true by `test_fitness_patterns.py`.

## Context
The ops assistant answers ten kinds of request (metrics, logs, deploys, runbooks, invoices, tickets, and a conditional "check deploys if the error rate is high"). The model server has a 1,000-token context window. We measured five designs on the same fixed task set with `patterns.py`:

| Design | Passed | Model calls | Tokens | Failed |
|---|---|---|---|---|
| One agent + tools | 9/10 | 26 | 4,753 | t07 (three log reads overflow the context) |
| Router -> one specialist | 6/10 | 33 | 2,982 | t05, t06, t09 (cross-domain), t07 |
| Planner/executor | 9/10 | 20 | 1,937 | t09 (plans without seeing results) |
| Supervisor/worker | 9/10 | 52 | 3,977 | t09 (the split hides the metric from the deploys worker) |
| Hybrid (one agent; supervisor/worker if the estimate > 90 % of the window) | 10/10 | 30 | 4,821 | - |

Cemri et al. (2025) report that multi-agent systems often gain little over single agents and fail through system design, inter-agent misalignment and missing verification; our failures are the same kinds (lost context at a hand-off, no access to the right tool).

## Decision
We will run one ReAct-style agent with all tools. We will escalate a task to supervisor/worker only when the code estimate of the agent's peak prompt (tool schemas + task + expected tool output) exceeds 90 % of the context window. We will not use a router or a planner/executor for this workload, because both fail tasks that cross domains or depend on an observation.

## Consequences
- Every escalated task costs more model calls (t07: 8 calls instead of 4) - acceptable for rare, very large tasks.
- The estimate is a keyword heuristic; a new long-output tool must add its size to `OUTPUT_WORDS`, or the fitness test will show an overflow.
- A tool-result budget (build task: `trim_results.py`) lets the single agent pass all 10 tasks with 4,168 tokens; if it holds up on real models it may replace the escalation.
- Planner/executor is 2.5x cheaper in tokens; revisit it if the task mix loses its observation-dependent steps.
