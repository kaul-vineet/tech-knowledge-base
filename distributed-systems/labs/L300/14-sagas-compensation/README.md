# 14 · Sagas with compensation

One order touches three services that each own their data: **orders** (create / cancel), **payments** (charge / refund), **shipping** (ship — the last step; once it succeeds nothing is undone). There is no shared database and no distributed transaction, so the order is a **saga**: a sequence of local steps where each completed step has a **compensating action** that undoes it semantically (a refund is a new ledger entry, not a deleted charge). An **orchestrator** runs the steps and writes every one to a **saga log (JSON lines)**. Forward steps are already **idempotent** (lesson 5): a retried charge or shipment does nothing new.

Happy path: six orders, all shipped, audit clean. Fault (seeded): shipping has no courier slot for 30% of orders. The lesson orchestrator marks those orders FAILED — and keeps the money.

Files: `saga.py` (lesson: services, `Orchestrator`, `audit`) · `choreography.py` (the same saga without an orchestrator: services react to events on an at-least-once bus) · `helpers.py` (plumbing: `SagaLog`, `StepFailed`, `Crash`, `crash_once_after` fault injector) · `try_it.py` · `test_saga.py` · build task: `solution_saga.py` + `test_build_task.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python saga.py
python choreography.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; seeded)
```
happy path: {'o1': 'completed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'completed', 'o6': 'completed'} | audit: OK
fault (30% of shipments fail, seed 14): {'o1': 'failed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'failed', 'o6': 'failed'}
saga log of o1 (JSON lines):
  {"saga": "o1", "step": "saga", "status": "started", "amount": 10}
  {"saga": "o1", "step": "create", "status": "done"}
  {"saga": "o1", "step": "charge", "status": "done"}
  {"saga": "o1", "step": "ship", "status": "failed", "error": "no courier slot"}
audit:
  o1: FAILED, shipped=False, money kept=10 of 10
  o5: FAILED, shipped=False, money kept=50 of 50
  o6: FAILED, shipped=False, money kept=60 of 60
```
```
choreography: 21 events delivered, audit: OK
```
The saga log tells the story an on-call engineer needs: `charge done`, `ship failed`, and **no** compensation entry. The audit checks the invariant from each service's own data: an order that did not ship must keep no money and must not be APPROVED. The choreography version already refunds (its `ShippingFailed` handler is the compensation), so its audit is clean — until events are duplicated (tryIt 2).

## Test
```bash
python -m unittest -v     # Ran 8 tests ... OK  (4 lesson tests + 4 build-task tests against the solution)
```

## Build task: compensate, idempotently, and recover from the log
1. On `StepFailed`, run the compensations of the **completed** steps in **reverse** order (refund, then cancel), logging `compensating` / `compensated` for each and `saga compensated` at the end.
2. Make `Payments.refund` idempotent: one refund per saga, for the amount actually charged; a no-op if nothing was charged.
3. Add `Orchestrator.recover()`: a new orchestrator reads the saga log and finishes every saga without a final entry. The step that was in flight when the old process died is **in doubt** — compensate it too (safe because compensations are idempotent and harmless if the step never ran).
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change (real run): `Ran 4 tests ... FAILED (failures=3, errors=1)` (`AttributeError: 'Orchestrator' object has no attribute 'recover'`; audit still lists `o1: FAILED, shipped=False, money kept=10 of 10`). The reference `solution_saga.py` prints:
```
happy path: {'o1': 'completed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'completed', 'o6': 'completed'} | audit: OK
fault (30% of shipments fail, seed 14): {'o1': 'compensated', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'compensated', 'o6': 'compensated'}
saga log of o1 (JSON lines):
  {"saga": "o1", "step": "saga", "status": "started", "amount": 10}
  {"saga": "o1", "step": "create", "status": "done"}
  {"saga": "o1", "step": "charge", "status": "done"}
  {"saga": "o1", "step": "ship", "status": "failed", "error": "no courier slot"}
  {"saga": "o1", "step": "charge", "status": "compensating"}
  {"saga": "o1", "step": "charge", "status": "compensated"}
  {"saga": "o1", "step": "create", "status": "compensating"}
  {"saga": "o1", "step": "create", "status": "compensated"}
  {"saga": "o1", "step": "saga", "status": "compensated"}
audit:
  OK
```

## Try it (real run — `python try_it.py`)
```
    orchestrator died right after refund('o1', 10)
tryIt 1: idempotent refund=False: refunds [-10, -10], audit: ['o1: CANCELLED, shipped=False, money kept=-10 of 10']
    orchestrator died right after refund('o1', 10)
tryIt 1: idempotent refund=True: refunds [-10], audit: OK
tryIt 2: lesson Payments: 32 deliveries, audit: | o6: CANCELLED, shipped=False, money kept=-60 of 60
tryIt 2: solution Payments: 32 deliveries, audit: | OK
```
tryIt 1: the orchestrator dies after the refund call succeeded but before it logged `compensated`; recovery runs the refund again — the customer is refunded twice unless the refund is idempotent. tryIt 2: choreography over a bus that duplicates ~20% of events (seeded): a duplicated `ShippingFailed` refunds twice with the plain refund.

## Platform notes
Pure computation: no sockets, no sleeps, no files (the saga log is an in-memory list of JSON lines; in production it is a table or a topic). Same output on macOS, Windows and Linux.
