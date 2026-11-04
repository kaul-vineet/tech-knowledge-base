# Team roles for the capstone and pair-programming protocol for L200

## 1. Capstone teams (3–4 students, weeks 10–14)
Every team builds the incident-triage agent of L400 #22 and its ADRs. Roles rotate once, at the start of week 12, so that each student holds at least two roles; the oral defence still examines everyone on the whole system.

| Role | Owns | Typical artefacts | Hand-off duty |
|---|---|---|---|
| **Boundary owner** | `policy.py`, allow-lists, approval rules; the "code decides" invariant (ADR-001) | Policy tests, fitness test, capability list | Explains every action the agent can take and who approves it |
| **Reliability owner** | Durable workflow, idempotency, budgets, retries (ADR-003) | Crash-sweep test, budget justification (lesson 25 T1) | Shows the worst-case cost and duplicate-free recovery |
| **Evaluation owner** | Golden incidents, scorecard, CI gate, statistics | `eval_capstone.py` baseline, Wilson intervals, power statement, McNemar comparison between versions | States what the suite can and cannot detect |
| **Integration and responsibility owner** (teams of 4; otherwise shared) | MCP tools, retrieval, traces; data handling and disclosure | Trace samples, retention settings, Art. 50 disclosure text, risk register | Leads the ethics part of the defence (lesson 26) |

**Team rules**
- One shared repository; every change through a pull request reviewed by someone in another role.
- Every ADR names its author(s) and is peer-reviewed by another team (`peer-review-adr.md`).
- A weekly 15-minute stand-up note (done / next / blocked) in the repository; it is the evidence used if contribution is disputed.
- Contribution statement at submission, signed by all members; marks can be moderated individually on the basis of the defence and the repository history.

## 2. Conflict and contribution
If a member is not contributing, the team records it in the stand-up notes and tells the course team by the end of week 12. Teams may not exclude a member without the course team's agreement.

## 3. Pair-programming protocol for the L200 labs (weeks 4–5)
L200 labs ("build it") are done in pairs: one feature per lab, with a test.

1. **Roles.** *Driver* types; *navigator* reads the lesson, watches for errors, and keeps the test in view. Swap every 20 minutes (set a timer) or at each green test, whichever is first.
2. **Start from the test.** Read the build task and its `test_build_task.py`; run it and watch it fail before writing code.
3. **Small steps.** The driver says what they are about to type; the navigator says "stop" for anything that contradicts the lesson's boundary rules (no secrets in prompts, deterministic checks in code, validation before use).
4. **Agent assist.** A local model may be used as a third voice for explanations or drafts. The navigator reads every suggestion aloud before it is typed; nothing generated is committed without both partners understanding it and a passing test.
5. **Commit together.** Both names in the commit message (`Co-authored-by:`). Each partner writes a two-sentence reflection in the lab README: what they drove, one thing they learned from the other.
6. **Remote pairs.** Use screen sharing with the same 20-minute swaps; the driver shares, the navigator keeps the lesson open.
7. **Assessment.** Lab marks are shared; the reflections and swap log are checked. Pairs change each week so everyone pairs with at least two classmates.
