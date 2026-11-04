**Concept: multi-agent patterns – planner/executor, supervisor/worker, router – and when one agent with tools is better**

## Why it matters
"Add more agents" is the usual next move after a first agent works. Each extra agent adds model calls, tokens and hand-offs where context gets lost. Sometimes that buys something real: room in an overflowing context, separate permissions, parallel work. Often it buys nothing. Cemri et al. (2025) analysed over 1,600 traces from seven multi-agent frameworks and found that the gains over a single agent were often small. Most failures were system design, misalignment between agents and missing checks. You can only decide which case you are in by measuring on your own tasks.

## Mental model
Every design is the same loop (lesson 6) cut into different pieces. The question is where the cuts go and what crosses each cut.

```
one agent:    task ─► [LLM ⇄ tools]* ─► answer                         (all context in one place)
router:       task ─► LLM:pick ─► specialist [LLM ⇄ its tools]* ─► answer
planner/exec: task ─► LLM:plan(JSON) ─► code runs tools ─► LLM:write ─► answer   (plans blind)
supervisor:   task ─► LLM:split ─► worker₁..ₙ [LLM ⇄ tools]* ─► LLM:combine ─► answer
```
Only task text and short answers cross a cut; tool results and schemas stay on one side. That is the benefit (isolation) and the cost (whatever was not handed over is gone).

## Design space
- **One agent + tools (ReAct).** Interleaves reasoning and acting, so later steps can depend on earlier observations (Yao et al.). Every step re-sends every tool schema and every result. Tokens grow with steps × tools, and long results can overflow the context window.
- **Router.** One cheap classification call, then a specialist that sees only its own tools: fewer schema tokens per call. It fails when a task spans domains, because the specialist simply does not have the other tool.
- **Planner/executor (ReWOO-style).** One planning call, code executes the plan, one call writes the answer. ReWOO reports about 5× fewer tokens on HotpotQA. The plan is written before any result exists, so it cannot react to what the tools return.
- **Supervisor/worker** (AutoGen, HuggingGPT controllers). Each sub-task gets a fresh context, which is real isolation for long outputs or different credentials. It costs the most calls, and information that the split did not foresee is lost.

## How to decide
Use a fixed task set and three numbers per design: success, model calls, tokens. Rank success first, then prefer the simplest design that reaches it.

Worked example (lab, context window 1,000 tokens, 10 tasks → see lab step 2):

| design | passed | calls | tokens | failed |
|---|---|---|---|---|
| one agent | 9 | 26 | 4,753 | t07: three log reads, 1,137 tokens > 1,000 |
| router | 6 | 33 | 2,982 | cross-domain t05, t06, t09 + t07 |
| planner/executor | 9 | 20 | 1,937 | t09 "check deploys *if* error_rate > 2 %" |
| supervisor/worker | 9 | 52 | 3,977 | t09: the deploys worker never saw the metric |
| hybrid | 10 | 30 | 4,821 | – |

The hybrid keeps one agent and escalates only when a code estimate of the peak prompt (schemas + task + expected results) exceeds 90 % of the window. For t07 the estimate is 1,178 against a budget of 900, so t07 goes to supervisor/worker. For t01 it is 143, so t01 stays on one agent. On every task that stays on one agent, the hybrid spends exactly the single agent's tokens; the fitness test checks this. A tool-result budget (build task) gets one agent to 10/10 with 4,168 tokens. Context engineering often beats adding agents.

## Failure modes at scale
- **Schema tax:** with 18 tools instead of 6, the same 26 calls cost 10,293 tokens instead of 5,925 (try it 2). Watch tokens per call grow as tools are added.
- **Hand-off loss:** workers answer the question they were given, not the one you meant. Watch for answers that are correct per sub-task but wrong as a whole.
- **Silent context truncation:** Ollama cuts the prompt to `num_ctx` instead of returning HTTP 400. Watch `prompt_tokens` near the window.

## Common mistakes
- Choosing a multi-agent framework before having a task set and a single-agent baseline.
- Comparing designs on success alone and ignoring calls and tokens (or the reverse).
- Splitting work by team boundaries instead of by context, permission or parallelism needs.
