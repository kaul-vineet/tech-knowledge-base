# 15 – Safe tool execution

A timeout does not mean 'nothing happened'. Side-effecting tools need a key that makes retries harmless, a human yes before they run, and a record of who did what.

Concept note: `../../../content/concepts/L300/15-safe-tool-execution.md` · lesson object: `content/L300.json` #15

## Run (fake server – validated)
```bash
python ../fake_server_l300.py --port 8765   # terminal 1
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model   # terminal 2
python safe_tools.py
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\fake_server_l300.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"   # terminal 2
python safe_tools.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
naive, 1 slow response : [{'id': 1, 'order_id': 'A-1001', 'amount': 25.0}, {'id': 2, 'order_id': 'A-1001', 'amount': 25.0}]
agent   : Final answer: send_refund(order_id=A-1001, amount=25.0) = queued for human approval as #1; nothing has been sent yet
refunds before approval: []
executed: [{'refund_id': 1, 'order_id': 'A-1001', 'amount': 25.0, 'replayed': True}]
refunds after approval : [{'id': 1, 'order_id': 'A-1001', 'amount': 25.0}]
{"actor": "agent", "event": "queued", "approval": 1, "args": {"amount": 25.0, "order_id": "A-1001"}, "key": "2f848eae73459b0ec30c1d92159fda06", "tool": "send_refund"}
{"actor": "alice", "event": "approved", "approval": 1}
{"actor": "executor", "event": "timeout_retry", "attempt": 0, "key": "2f848eae73459b0ec30c1d92159fda06"}
{"actor": "executor", "event": "executed", "approval": 1, "key": "2f848eae73459b0ec30c1d92159fda06", "result": {"amount": 25.0, "order_id": "A-1001", "refund_id": 1, "replayed": true}, "tool": "send_refund"}
```
`approvals.db` afterwards:
```
[(1, 'send_refund', 'done', 'alice')]
[('agent', 'queued'), ('alice', 'approved'), ('executor', 'timeout_retry'), ('executor', 'executed')]
```

Tests: `Ran 11 tests ... OK`.

## Failure lab
| | |
|---|---|
| Fault (seeded) | payments_service.py commits the first refund and then answers 0.6 s late (slow_first=True); the client timeout is 0.3 s - deterministic. |
| Symptom | The naive tool sees a timeout, retries, and the customer is refunded twice: 2 rows of 25.00 for A-1001. |
| Fix | Queue side-effecting calls for human approval (SQLite), send an Idempotency-Key derived from run + call id, retry only with the same key, audit every step. |
| Proof | test_failure_lab_naive_retry_refunds_twice (2 refunds) vs test_failure_lab_key_and_approval_refund_once (0 before approval, 1 after, replayed True). |

## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| Approve every side effect | No action without a human; clear accountability | Latency, reviewer fatigue ('approve all') | Money, deletes, external messages, early in a rollout |
| Auto-approve under a policy (e.g. refunds <= 20.00) | Fast for routine cases | The policy is now the control; needs its own tests and limits | High volume, low value, after the golden set and audit data justify it |
| Dry-run first | Safe preview, good for reviews and new tools | The real call can still fail differently | New tools, migrations, bulk operations |

## Build task
Start from the shipped resumable_gate.py (unfixed: resume() re-sends stuck rows with a NEW key). Make execution resumable: after a crash between 'refund sent' and 'status done', a restarted process finishes every 'executing' row with its stored key - exactly one refund.

Hints:
- Select rows WHERE status = 'executing'.
- Call _send() with the key from the row.
- Write 'done' and an audit row 'resumed'.

Your file: `resumable_gate.py` (shipped unfixed) · solution: `solution/resumable_gate.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28 – shipped file (fail-before) vs solution (pass-after):
```
BUILD_TARGET=mine  -> AssertionError: Tuples differ: (2, False, 'done') != (1, True, 'done')
                      FAILED (failures=1)
solution           -> Ran 1 test ... OK
```

## Equivalents
- IETF Idempotency-Key header (draft-ietf-httpapi-idempotency-key-header-08): the server side of this lab's payments stand-in
- Workflow engines (durable execution) persist each step and resume after crashes - the same 'state before side effect' rule
- MCP host confirmation prompts and Open WebUI's tool approval ('ask first') are UI versions of the approval queue

## Optional steps (not run in the sandbox)
**real model** – ollama pull qwen2.5:1.5b, then python safe_tools.py with the default LOCAL_MODEL_URL.
Expected: The model may or may not call send_refund; if it does, the call is queued - never executed without approval


## Troubleshooting
| Symptom | Action |
|---|---|
| Duplicates despite keys | Check the key is generated once per logical call and stored before the first attempt; a new key per retry is the classic bug (Try it 1). |
| 422 from the API | The same key was reused with different arguments - the arguments changed between proposal and execution; re-queue for approval. |
| Approvals pile up | Show the exact arguments, group similar requests, and add an expiry; auto-approve only under a tested policy. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_15` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Make a NEW idempotency key on every attempt (key-0, key-1, ...). | [{'id': 1, 'order_id': 'A-1001', 'amount': 25.0}, {'id': 2, 'order_id': 'A-1001', 'amount': 25.0}] - two again: a key only helps if retries reuse it. |
| Run the agent with ToolGate(..., dry_run=True). | Final answer: send_refund(order_id=A-1001, amount=25.0) = DRY RUN: would call send_refund with {"amount": 25.0, "order_id": "A-1001"} | approvals: 0 | refunds: [] |
