# 18 – Durable agent workflows: checkpoints, resume and exactly-once effects

A process will die mid-workflow. Record each step's result before moving on, derive effect keys from the workflow and step, and treat waiting for a human as data, not a sleeping thread.

Concept note: `../../../content/concepts/L400/18-durable-workflows.md` · lesson object: `content/L400.json` #18

## Design brief
A support agent proposes a refund with a model, a manager approves it (minutes to days later), the payments API moves the money and the customer is notified.

Constraints:
- A crash at any of 12 points (before/after each of 5 steps, after the model answered, after the payment answered) must end with exactly 1 refund and 1 notification
- No thread or HTTP request held open while a human decides
- Approvals expire after 48 h; a late click must not move money
- Runs on one Mac mini or Windows PC without extra servers

Question: In-memory loop with retries, an SQLite checkpoint journal, or a workflow engine (Temporal)?

## Run (fake server – validated)

**Start the L400 fake server**
```bash
python ../fake_server_l400.py --port 8765
```
PowerShell:
```powershell
python ..\fake_server_l400.py --port 8765
```

**Run the demo: naive vs durable, same crash**
```bash
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model; python durable.py
```
PowerShell:
```powershell
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python durable.py
```

**Build task: approval_policy.py**
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # drop BUILD_TARGET to check solution/
```
PowerShell:
```powershell
$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task   # Remove-Item Env:BUILD_TARGET to check solution/
```

**Optional: Temporal equivalent**
```bash
python -m pip install temporalio==1.34.0 && RUN_TEMPORAL=1 python -m unittest -v test_temporal_equivalent
```
PowerShell:
```powershell
python -m pip install temporalio==1.34.0; $env:RUN_TEMPORAL="1"; python -m unittest -v test_temporal_equivalent
```

### Expected output (observed 2026-10-28)
```
naive, crash after the refund : 2 -> 2 refunds
durable, same crash          : done ['after_effect:refund'] -> 1 refund
{"step": "lookup", "event": "completed", "order_id": "A-1001", "paid": 25.0, "status": "delivered"}
{"step": "propose", "event": "completed", "amount": 25.0}
{"step": "approval", "event": "signal:approve", "by": "alice"}
{"step": "approval", "event": "completed", "by": "alice"}
{"step": "refund", "event": "completed", "refund_id": 1, "replayed": true}
{"step": "notify", "event": "completed", "order_id": "A-1001", "amount": 25.0}
outbox: [('refund_done',)]
```

Tests: `Ran 12 tests ... OK (skipped=1)` (`python -m unittest -v` in this folder).

## Options measured
| Option | Evidence (this lab) | Verdict |
|---|---|---|
| In-memory loop + retries | Crash sweep: duplicate refund at 4 of 12 points; the model re-asked at 9 of 12. | Rejected: fine for read-only agents only. |
| SQLite event history + idempotency keys + outbox | Without keys: 1 duplicate (after the payment answered, before the checkpoint). With keys: 0 of 12; the only repeat is one model call (crash after its answer). | Chosen while one process owns the workflows. |
| Temporal (workflow engine) | Pending CI (temporalio 1.34.0, local dev server): expected 'done' with 1 refund after an activity that dies after the payment is retried. | Next step for several workers, cross-host timers and history browsing; keys are still needed. |


## Decision and fitness function
Decision record: `ADR-0018-sqlite-event-history.md` (Nygard: Title, Status, Context, Decision, Consequences).

Fitness function: `test_fitness_crash_sweep.py` – Kill the workflow once at each of the 12 crash points, restart from the SQLite file, drive it to the end. Threshold: status done, refunds == 1, refund_done outbox rows == 1 at every point; model calls <= 1 (2 only for after_model:propose).


## Scaling limits
- One SQLite writer: many concurrent workflows queue on the write lock -> 'database is locked' errors and growing step latency; move to Temporal or a server database.
- Unbounded histories: long-lived workflows with many signals slow replay -> watch rows per workflow; Temporal's continue-as-new is the equivalent fix.
- APIs without Idempotency-Key: the 'after the effect, before the checkpoint' gap cannot be closed -> reconcile by querying the API before retrying.


## Failure lab
| | |
|---|---|
| Fault | The process is killed right after the payments API committed the refund and answered, before the step's checkpoint is written (crash point after_effect:refund, deterministic). |
| Symptom | Naive restart: 2 refunds. Checkpoints without a key: still 2 refunds - the restart re-sends because the checkpoint never happened. |
| Fix | Derive the Idempotency-Key from workflow id + step ('wf-1:refund') and send it on every attempt; write local effects (notification) in the checkpoint transaction. |
| Proof | test_failure_lab_naive_refunds_twice and test_failure_lab_checkpoint_without_key_refunds_twice (2 refunds) vs test_failure_lab_durable_refunds_once (1 refund, replayed true). |


## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| In-memory loop | Simplest | Duplicates and re-asks after any crash | Read-only agents |
| SQLite history + keys + outbox | Exactly-once on one machine, no extra server | One writer; you own the engine code | One process, local-first deployments |
| Temporal | Durable timers, retries, history UI, many workers | A server to run; deterministic-workflow rules | Several workers or hosts, many long waits |


## Build task
Give approvals a deadline: make approval_policy.state() return 'timed_out' when no decision arrived within timeout_h (the workflow escalates, no refund) and ignore approve/reject signals stamped after the deadline.

Hints:
- deadline = since + timeout_h
- Only signals with ts <= deadline count.
- 'timed_out' only when now > deadline; otherwise 'waiting'.

Your file: `approval_policy.py` (shipped unfixed) · solution: `solution/approval_policy.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28: Before your change: FAILED: (['waiting', 'waiting', 'waiting', 'done'], 1, ['refund_done']) != (['waiting', 'waiting', 'escalated', 'escalated'], 0, ['approval_timeout']). After: OK


## Try it
1. Crash between the model's answer and its checkpoint (crash_at={'after_model:propose'}). Predict: How many model calls and refunds after recovery?
   Observed: done, crashes ['after_model:propose'], model calls 2, refunds 1 - the model is asked twice (tokens), money moves once.
2. Send the approval signal twice (a double click) before running on. Predict: How many signals are stored, how many refunds?
   Observed: done, approve signals stored 1, refunds 1 - UNIQUE (wf_id, step, event) de-duplicates the signal.


## Learning tools
- **Temporal CLI dev server + Web UI** (SEE, MIT (OSI: yes)): Start `temporal server start-dev`, change run_demo in temporal_equivalent.py to Client.connect('localhost:7233'), run it, then open wf-temporal-1 in the Web UI (http://localhost:8233). Pending a manual run. The event history should show propose_refund completed, the approve signal, send_refund failed once (worker died after the refund) and completed on retry - and the payments stand-in still lists 1 refund, as the lab's durable run does. Mac: `brew install temporal; temporal server start-dev   (UI http://localhost:8233)` · Windows: `Windows amd64 archive from the CLI README; temporal.exe server start-dev`
- **Toxiproxy** (BUILD WITHOUT CODE / INSPECT, MIT (OSI: yes)): Put a proxy in front of the payments stand-in, add a 'reset_peer' toxic (toxicity 1.0) for the first POST only, and point Engine(payments_url=...) at the proxy. Pending a manual run. The engine sees a connection error after the payment committed - the same gap as the failure lab; with keys the next run gets Idempotent-Replayed true and the stand-in lists 1 refund. Mac: `brew tap shopify/shopify && brew install toxiproxy   (or ghcr.io/shopify/toxiproxy)` · Windows: `toxiproxy-server/cli-windows-amd64.exe from the GitHub releases`


## Equivalents
- Temporal (MIT; CLI dev server + Web UI in the learning-tools catalogue): event history, activities, signals, durable timers
- IETF draft-ietf-httpapi-idempotency-key-header: the API side of the exactly-once effect
- Transactional outbox (application-architecture L200 #9): local effects committed with the state change


## Simulator vs real
The payments API is the stdlib stand-in from lesson 15; crashes are injected exceptions (Crash) at named points, not real kills - the SQLite file and the API state are real. Timing uses a fake clock in hours.

**Caution:** Never let the model choose the idempotency key, the approval state or the deadline; keep approval signals authenticated in a real system (who clicked matters for the audit trail).

**Pending CI / manual:** temporal_equivalent.py + test_temporal_equivalent.py (temporalio 1.34.0, RUN_TEMPORAL=1; CI temporal job); durable.py against a real model (CI real_model job); Temporal Web UI and Toxiproxy exercises (manual)
