# Lab 12 – CQRS and read models: projections that survive crashes

Commands go to the lesson-8 `Member` aggregate, which is rebuilt from an append-only SQLite event log; every accepted command appends one event. A **projector** thread turns events into a query-shaped **read model** (`member_loans`, `book_status`) in its own database, stores a **checkpoint**, and logs every applied event as a JSON line with `lag_ms` (the consistency window). The base projector works on the happy path but loses an event if it is killed at the wrong moment; you harden it.

## Files
| File | Purpose |
|---|---|
| `projector.py` | Projector, `LoansView`, `rebuild()`, `drift()` (lesson code) |
| `write_model.py` | `Member` aggregate, `EventStore`, `LoanCommands` (write side) |
| `app.py` | Demo: 40 seeded commands, projector thread (20 ms poll), lag, stale reads, rebuild; writes `out/projector.jsonl` |
| `failure_lab.py` | Seeded crash at seq 31, restart, drift: base vs solution |
| `test_cqrs.py` | Write/read side, JSON log, rebuild, drift, symptom |
| `test_build_task.py` | Build task check (fails on the base file, passes on the solution) |
| `solution/projector.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L300/12-cqrs-read-models
python app.py
python failure_lab.py
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
Lag and stale-read counts change from run to run (6 runs here: p50 9.6–12.8 ms, p95 18.0–54.7 ms, max 19.1–57.0 ms, stale reads 25–28 of 33); event counts, view and drift do not.
```
$ python app.py
write side : 40 commands -> 33 events, 7 rejected by the aggregate
read side  : consistency window from the projector log: p50 9.6 ms, p95 18.0 ms, max 19.1 ms (poll every 20 ms)
stale reads: 28 of 33 reads straight after the command did not see it yet
view       : {'m1': 2, 'm2': 3, 'm3': 2}
log        : out/projector.jsonl (33 lines); first: {"evt": "projected", "lag_ms": 0.2, "projector": "loans_view", "seq": 1, "type": "LoanCreated"}
rebuild    : replayed 33 events, view identical: True, drift: []
```

## failureLab: the projector dies between checkpoint and apply
`random.Random(12)` picks seq 31 of 33. The base projector has already saved checkpoint 31 when it dies, so the restarted projector starts at 32 and never applies event 31. Nothing raises an error; only the drift check notices.
```
$ python failure_lab.py
base     projector.py: projector died at seq 31; restarted at position 33 of 33; drift: 2 row(s)
    member_loans[m3]: view 1, events say 2
    book_status[b6]: view None, events say 'm3'
    recovery: rebuild() -> drift []
solution projector.py: projector died at seq 31; restarted at position 33 of 33; drift: 0 row(s)
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_checkpoint_does_not_move_past_a_crash (test_build_task.HardenedProjectorTest...) ... ok
test_crash_then_restart_leaves_no_drift (test_build_task.HardenedProjectorTest...) ... ok
test_replayed_event_changes_nothing (test_build_task.HardenedProjectorTest...) ... ok
test_threaded_run_converges (test_cqrs.DemoTest...) ... ok
test_symptom_base_projector_misses_an_event_after_a_crash (test_cqrs.FailureLabTest...) ... ok
test_drift_finds_a_tampered_row (test_cqrs.ReadSideTest...) ... ok
test_log_is_one_json_object_per_line (test_cqrs.ReadSideTest...) ... ok
test_rebuild_reproduces_the_view (test_cqrs.ReadSideTest...) ... ok
test_return_updates_both_tables (test_cqrs.ReadSideTest...) ... ok
test_view_is_behind_until_the_projector_runs (test_cqrs.ReadSideTest...) ... ok
test_aggregate_rejects_fourth_loan_and_records_nothing (test_cqrs.WriteSideTest...) ... ok
----------------------------------------------------------------------
Ran 11 tests in 0.374s

OK
```

## Build task (the hardening change)
Make `projector.py` apply the event and save the checkpoint in **one** transaction, and make the handlers **idempotent** (recount `active` from `book_status` instead of `active + 1`).

- Solution: `solution/projector.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `projector.py`:
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged projector.py
FAIL: test_checkpoint_does_not_move_past_a_crash
FAIL: test_crash_then_restart_leaves_no_drift
FAIL: test_replayed_event_changes_nothing
FAILED (failures=3)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first (tasks and predictions are in the lesson's `tryIt` field), then run. Lag values vary per run.
```
$ python try_it.py
[1] poll every  20 ms -> consistency window p50 11.7 ms, max 55.7 ms
[1] poll every 200 ms -> consistency window p50 154.2 ms, max 197.6 ms
[2] projector died at seq 31, after apply, before checkpoint
[2] restart -> drift: ['member_loans[m3]: view 3, events say 2']
```
Other runs: 20 ms poll p50 13.7–17.1 ms, max 53.7–58.4 ms; 200 ms poll p50 111–121 ms, max 197.5–197.8 ms.

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines. `out/projector.jsonl` is written with `encoding="utf-8"`; read it with `head -3 out/projector.jsonl` (zsh) or `Get-Content out\projector.jsonl -TotalCount 3` (PowerShell). Windows' coarser timer may raise the measured lag slightly; the drift results do not depend on timing.

## Troubleshooting
| Symptom | Action |
|---|---|
| `drift` lists rows after a restart | The checkpoint moved without the view change (or an event was applied twice). `rebuild()`, then fix the transaction boundary. |
| `lag_ms` keeps growing | The projector is behind or stopped: compare `position()` with the last event seq. |
| A borrow is not visible right after the command | Expected (eventual consistency); return the command result or wait for the checkpoint to reach its seq. |
