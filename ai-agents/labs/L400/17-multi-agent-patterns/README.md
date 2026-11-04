# 17 – Multi-agent patterns: when one agent with tools is enough

More agents means more calls, more tokens and more hand-offs. Measure first: one agent with tools is the baseline every other design has to beat on your tasks.

Concept note: `../../../content/concepts/L400/17-multi-agent-patterns.md` · lesson object: `content/L400.json` #17

## Design brief
An internal ops assistant answers ten request types against six tools (metrics, logs, deploys, runbooks, invoices, tickets) on a small local model with a 1,000-token context window.

Constraints:
- Success on all 10 fixed tasks (graded by code: every expected call made, no extra call, every fact stated)
- At most 8 model calls per task
- Tokens per task no higher than one agent's on tasks one agent can do
- Never exceed the 1,000-token context window

Question: One agent with all tools, a router to specialists, planner/executor, supervisor/worker - or a mix?

## Run (fake server – validated)

**Start the L400 fake server with a 1,000-token window**
```bash
python ../fake_server_l400.py --port 8765 --context-limit 1000
```
PowerShell:
```powershell
python ..\fake_server_l400.py --port 8765 --context-limit 1000
```

**Measure the five designs**
```bash
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model; python patterns.py
```
PowerShell:
```powershell
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python patterns.py
```

**Read the failures in patterns.jsonl**
```bash
python -c "import json; [print(r) for r in map(json.loads, open('patterns.jsonl', encoding='utf-8')) if not r['pass']]"
```
PowerShell:
```powershell
python -c "import json; [print(r) for r in map(json.loads, open('patterns.jsonl', encoding='utf-8')) if not r['pass']]"
```

**Build task: trim_results.py**
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # drop BUILD_TARGET to check solution/
```
PowerShell:
```powershell
$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task   # Remove-Item Env:BUILD_TARGET to check solution/
```

### Expected output (observed 2026-10-28)
```
single     9/10 passed  model calls  26  tokens   4753  failed ['t07']
router     6/10 passed  model calls  33  tokens   2982  failed ['t05', 't06', 't07', 't09']
planner    9/10 passed  model calls  20  tokens   1937  failed ['t09']
supervisor 9/10 passed  model calls  52  tokens   3977  failed ['t09']
hybrid     10/10 passed  model calls  30  tokens   4821  failed []
per-task rows: patterns.jsonl
```

Tests: `Ran 12 tests ... OK` (`python -m unittest -v` in this folder).

## Options measured
| Option | Evidence (this lab) | Verdict |
|---|---|---|
| One agent + tools (ReAct loop) | 9/10, 26 model calls, 4,753 tokens; fails t07: three log reads reach 1,137 prompt tokens > 1,000 (HTTP 400 context_length_exceeded). | Best default: handles observation-dependent steps (t09); needs a guard for very long results. |
| Router -> one specialist | 6/10, 33 calls, 2,982 tokens; fails cross-domain t05, t06, t09 (the specialist lacks the other tool) and t07. | Rejected for this mix: cheap per call but blind to tasks that span domains. |
| Hierarchies: planner/executor or supervisor/worker | Planner 9/10, 20 calls, 1,937 tokens (fails t09: plans before seeing the metric). Supervisor 9/10, 52 calls, 3,977 tokens (fails t09: the split hides the metric). Hybrid 10/10, 30 calls, 4,821 tokens; t07 escalated (estimate 1,178 > 900). | Chosen: the hybrid - one agent by default, supervisor/worker only for context overflow. Planner/executor is the cheapest if tasks never depend on observations. |


## Decision and fitness function
Decision record: `ADR-0017-one-agent-by-default.md` (Nygard: Title, Status, Context, Decision, Consequences).

Fitness function: `test_fitness_patterns.py` – The hybrid passes 10/10; on every task the estimate keeps on one agent it spends exactly the single agent's tokens; no task uses more than 8 model calls. Threshold: 10/10 passed; tokens(hybrid) == tokens(single) on non-escalated tasks; model calls <= 8 per task.


## Scaling limits
- Many long-output tools: the keyword estimate misses new tools -> context_length_exceeded (or, on Ollama, silently truncated prompts) in the logs.
- Dozens of tools: schema tokens dominate every call (6 -> 18 tools: 5,925 -> 10,293 tokens for the same calls) -> route or filter tools per request.
- Independent long sub-tasks at volume: one agent is sequential -> supervisor/worker in parallel becomes worth its extra calls when latency, not tokens, is the constraint.


## Failure lab
| | |
|---|---|
| Fault | Task t07 reads three service logs (~330 words each) on a model with a 1,000-token window (fake server --context-limit 1000, deterministic). |
| Symptom | The single agent's fourth call is rejected: context_length_exceeded: 1137 prompt tokens > context 1000 - t07 fails; the router fails the same way. |
| Fix | Estimate the peak prompt in code and escalate only those tasks to supervisor/worker (hybrid); the build task shows the alternative fix - a tool-result budget. |
| Proof | test_failure_lab_single_overflows (fails with context_length_exceeded) vs test_failure_lab_hybrid_escalates (estimate 1178 > 900, pass in 8 calls). |


## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| One agent + tools | Adapts to results; fewest moving parts | All schemas and results on every call; overflow on long results | Default; tasks under the context budget |
| Router | Fewer schemas per call | Cross-domain tasks fail silently | Domains never mix and tool counts are large |
| Planner/executor or supervisor/worker | Fewest calls (planner) or context isolation (supervisor) | Blind to observations; hand-off loss; most calls (supervisor) | Fixed-shape tasks (planner); long or separately-permissioned sub-tasks (supervisor) |


## Build task
Give the single agent a tool-result budget: make trim_results.trim(result) keep the first line (the fact) plus at most 60 words and say what was cut, so t07 fits in one agent's 1,000-token window.

Hints:
- The first line of every tool result carries the fact the grader checks.
- Split on lines, keep line 0, count the remaining words.
- Tell the model what was cut ('ask for a narrower query') instead of silently dropping it.

Your file: `trim_results.py` (shipped unfixed) · solution: `solution/trim_results.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28: Before your change: FAILED (failures=2): 9 != 10 (t07 still overflows) and 202 not less than or equal to 75. After: OK - single+trim: 10/10, model calls 26, tokens 4168


## Try it
1. Start the fake server with --context-limit 2000 (a larger num_ctx) and run the single agent again. Predict: Does one agent now solve everything? At what token cost?
   Observed: context 2000 -> single 10/10, tokens 5925, failed [] - the overflow, not the topology, was the problem.
2. Offer the single agent 12 extra unused tools (single(run, task, extra_tools=12)). Predict: Do the answers change? Do the tokens?
   Observed: 6 tools -> 5925 tokens; 18 tools -> 10293 tokens (+4368) for the same 26 model calls - the schema tax that routers avoid.


## Learning tools
- **Langflow** (BUILD WITHOUT CODE, MIT (OSI: yes)): Build two flows on Ollama: one Agent with all six tools, and a router prompt in front of two agents with two tools each; send t05 ('Check metrics for payments and deploys for payments') to both and compare the tool calls in the trace. Pending a manual run. Should match the lab: the single agent calls get_metrics and list_deploys; the routed flow calls only one of them (router t05 fails in patterns.jsonl). Mac: `uv pip install langflow && uv run langflow run   (Python 3.10-3.14; set LANGFLOW_SUPERUSER_PASSWORD since 1.13)` · Windows: `uv pip install langflow; uv run langflow run   (same pip/uv route; Desktop .msi may need MS C++ Build Tools)`


## Equivalents
- AutoGen / multi-agent conversation frameworks: supervisor/worker and group-chat topologies (the measurement method is the same)
- HuggingGPT: an LLM controller that plans, routes to models and summarises (planner + router)
- Langflow agent components: build the router and the single-agent flow without code and compare their tool-call traces


## Simulator vs real
fake_server_l400.py follows fixed rules (header) and counts words as tokens: it proves the plumbing, the grading and the cost accounting, not model quality. A real model may pick wrong tools, plan differently and, on Ollama, truncate instead of failing.

**Caution:** Workers inherit the tools you give them: never pass side-effecting tools to a worker just because the supervisor had them; keep approval gates (lesson 15) at the tool, not in the topology.

**Pending CI / manual:** patterns.py against a real model (CI real_model job; Ollama truncates instead of HTTP 400); Langflow exercise (manual)
