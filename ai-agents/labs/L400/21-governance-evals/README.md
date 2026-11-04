# 21 – Governance and evaluation in production

A model can change without a code change. Pin it, gate every upgrade on evals and red-team cases, watch traffic for drift, and keep an audit trail that survives retention.

Concept note: `../../../content/concepts/L400/21-governance-evals.md` · lesson object: `content/L400.json` #21

## Design brief
The triage agent runs on a local model that someone may re-pull at any time; a new model version (fake-model:v2) is proposed; prompts contain customer text that may not be kept for ever.

Constraints:
- A changed model is detected before it serves traffic
- An upgrade with any golden-set regression or unsafe red-team case is rejected
- A 2x input shift is flagged at alpha = 0.01
- Any edit to the audit trail is detectable; prompt text older than 30 days is deleted

Question: Which controls, and how strict: manual spot checks, a pass-rate gate, or a regression gate + red team + drift + audit?

## Run (fake server – validated)

**Run the governance demo**
```bash
python governance.py
```
PowerShell:
```powershell
python governance.py
```

**Read the decision record**
```bash
cat upgrade-record.md
```
PowerShell:
```powershell
Get-Content upgrade-record.md
```

**Agent assist: a drafted Context paragraph**
```bash
python agent_assist.py
```
PowerShell:
```powershell
python agent_assist.py
```

**Build task: retention.py**
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # drop BUILD_TARGET to check solution/
```
PowerShell:
```powershell
$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task   # Remove-Item Env:BUILD_TARGET to check solution/
```

**Real models: pin and compare**
```bash
curl -s http://localhost:11434/api/tags
```
PowerShell:
```powershell
irm http://localhost:11434/api/tags
```

### Expected output (observed 2026-10-28)
```
pin check at start   : OK
pin check after pull : ['fake-model:latest: pinned 1f49242847a4, server has 52d1337ffaca']
{"pinned": "fake-model", "candidate": "fake-model:v2", "passed": 19, "total": 20, "pass_rate": 0.95, "regressions": ["t14"], "gate_reasons": ["regressions vs baseline: ['t14']"], "redteam_safe": 8, "redteam_total": 8, "drift_chi2": 3.92, "drift_df": 1, "drift_alarm": false}
decision: REJECT
input drift, same mix      (chi2, df, alarm): (0.0, 4, False)
input drift, shipping surge (chi2, df, alarm): (45.71, 4, True)
decision record written: upgrade-record.md

$ python agent_assist.py
unknown numbers: []
# Model upgrade: fake-model -> fake-model:v2

Status: REJECT (computed by `decide_upgrade()`; a person signs off, the model never sets this line)

## Context
candidate fake-model:v2 passed 19/20 golden cases (95%) with 1 regressions against the pinned model; the red-team suite was 8/8 safe; drift alarm: False.
tampered draft unknown numbers: ['100', '0']
```

Tests: `Ran 12 tests ... OK` (`python -m unittest -v` in this folder).

## Options measured
| Option | Evidence (this lab) | Verdict |
|---|---|---|
| Manual spot checks before an upgrade | Lesson 12's broken v2 prompt passed a 3-case spot check (3/3); the re-tag is invisible without a pin. | Rejected: misses single-case regressions. |
| Pass-rate gate (>= 95 %) | fake-model:v2 scores 19/20 = 95 % -> ACCEPT (try it 1) although t14 ('immediately') lost its high priority. | Rejected: averages hide regressions. |
| Pinned digest + regression gate + red team + drift + audit | Pin mismatch reported (pinned 1f49242847a4, server has 52d1337ffaca); v2 REJECT (regression t14; red team 8/8; output drift chi2 3.92 no alarm); shipping surge chi2 45.71 > 13.277 alarm; edited audit row -> verify (False, 3). | Chosen (ADR-0021). |


## Decision and fitness function
Decision record: `ADR-0021-pin-gate-monitor.md` (Nygard: Title, Status, Context, Decision, Consequences).

Fitness function: `test_fitness_governance.py` – The lock matches the server; v2 (one regression) is REJECTED and an equivalent candidate (fake-large) ACCEPTED; a shipping surge raises the drift alarm; the audit chain verifies and detects one edited row. Threshold: pin problems == []; REJECT/ACCEPT as stated; drift alarm True at alpha 0.01; verify (True, None) then (False, 4).


## Scaling limits
- Golden sets age: the gate stays green while new traffic fails -> drift alarms and user reports on cases not in the set; add them.
- Fixed-threshold drift on large windows alarms on tiny shifts (chi-square grows with n) -> alarm fatigue; use fixed window sizes or effect-size bounds.
- One SQLite audit file per host: concurrent writers and multi-host audits need a central append-only store with the same chain (or a transparency log).


## Failure lab
| | |
|---|---|
| Fault | The app uses the unpinned alias fake-model:latest; someone re-pulls and the alias now points at fake-model:v2 (server.retag, deterministic) - no code change, no deploy. |
| Symptom | t14 ('Delivery is late and I need it immediately') comes back with priority normal instead of high; nothing in the app's logs says the model changed. |
| Fix | Pin name + digest in models.lock.json and refuse to start on a mismatch; route the new model through evaluate_candidate() and decide_upgrade(). |
| Proof | test_failure_lab_unpinned_alias_changes_answers: before high, after normal; pin_check reports 'pinned 1f49242847a4, server has 52d1337ffaca'; test_gate_blocks_a_regression_that_the_pass_rate_hides: REJECT. |


## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| Regression gate on a golden set | Catches single-case regressions before release | Golden set to maintain; blind to new kinds of input | Every model/prompt change |
| Drift monitoring (no labels) | Sees traffic and model shifts in production | Coarse; false alarms on large windows | Always on, as a trigger to re-evaluate |
| Hash-chained audit + content retention | Tamper-evident history; personal text deleted on schedule | Old prompts gone for investigations | Personal data in prompts; regulated decisions |


## Build task
Make retention.purge() delete prompt/answer CONTENT older than keep_days (unless a newer audit row still points at the same content) and never delete audit rows, so verify() still passes.

Hints:
- cutoff = today - keep_days
- DELETE FROM content WHERE day < cutoff AND hash NOT IN (SELECT content_hash FROM audit WHERE day >= cutoff)
- Do not touch the audit table.

Your file: `retention.py` (shipped unfixed) · solution: `solution/retention.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28: Before your change: FAILED: (30, (False, 32)) != (61, (True, None)) - audit rows deleted, chain broken, old text still there. After: OK - removed 30, audit rows 61, old content left 1, verify (True, None)


## Try it
1. Drop the per-case regression check and keep only the 95 % pass-rate bar for v2. Predict: Is v2 accepted?
   Observed: pass rate 95% -> ACCEPT (t14 'immediately' is now normal priority) - the average hides the regression.
2. Change one audit row's actor (seq 3) from 'alice' to 'bob' directly in SQLite. Predict: What does verify() return?
   Observed: verify() -> (False, 3) - the edited row no longer matches its stored hash.


## Agent assist (model proposes, code decides)
The model drafts the Context paragraph of the model-upgrade decision record from the measured report.

- Check: unknown_numbers(): every number in the draft must appear in the report (plus the pass rate in %); otherwise the code-written context is used. The Status (ACCEPT/REJECT) is always decide_upgrade().
- Observed: unknown numbers: [] -> 'candidate fake-model:v2 passed 19/20 golden cases (95%) with 1 regressions ...'; a tampered draft ('20/20 (100%) with 0 regressions') -> unknown numbers ['100', '0'], dropped.
- Real model: Real models round, rephrase or invent figures; keep the number check strict and the decision line out of the model's reach.


## Learning tools
- **promptfoo** (CHECK, MIT (OSI: yes)): Run lesson 12's promptfooconfig.yaml twice with two providers (ollama:chat:qwen2.5:1.5b and your candidate tag) and compare per-test results, local-first (telemetry off, no remote generation). Pending a manual run. A per-test diff is the regression list; compare its shape with the lab's report (regressions ['t14'] for fake-model:v2) - a pass rate alone is not the decision. Mac: `export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1; npx promptfoo@latest eval -c <config>   (or brew install promptfoo; Node >= 22.22)` · Windows: `$env:PROMPTFOO_DISABLE_TELEMETRY="1"; $env:PROMPTFOO_DISABLE_UPDATE="1"; npx promptfoo@latest eval -c <config>   (or npm i -g promptfoo)`
- **garak (NVIDIA)** (CHECK, Apache-2.0 (OSI: yes)): Before accepting a candidate tag, run `python -m garak --target_type ollama --target_name <candidate> --spec probes.promptinject` in its own venv and keep the report next to upgrade-record.md. Pending a manual run. Hit rates describe the MODEL; the lab's protected red-team suite (8/8 safe) is what gates the upgrade, because code, not the model, blocks actions. Mac: `python -m pip install -U garak   (own venv; Python 3.11-3.14)` · Windows: `python -m pip install -U garak   (own venv)`


## Equivalents
- promptfoo eval in CI (lesson 12) and garak scans: tool-based versions of the gate and the red-team suite
- Sigstore/minisign-style signing (cryptography L300 #14): pin and verify artifacts by digest
- Transparency logs (Certificate Transparency): hash-chained, append-only logs at internet scale


## Simulator vs real
fake-model:v2 differs from v1 by one documented rule (V); digests are hashes of the fake's model names, in the Ollama /api/tags shape. Drift streams are replays of the golden tickets, not real traffic.

**Caution:** Audit and drift logs contain customer text: apply the same retention to every copy (backups, exports), and never send them to a hosted model for 'analysis'.

**Pending CI / manual:** pin_check against a real Ollama /api/tags (manual); evaluate_candidate with two real model tags (CI real_model job); promptfoo and garak exercises (manual)
