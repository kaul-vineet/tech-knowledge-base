# Lab 09 – Event-driven integration: domain events, outbox, AsyncAPI

Each loan change writes its domain event (`LoanCreated`, `LoanReturned`) into an `outbox` table **in the same SQLite transaction**. A relay publishes pending rows in order to an in-process bus; idempotent consumers send notifications and keep a projection. `asyncapi.json` (AsyncAPI 3.1.0) describes the events, and every published event is validated against it.

## Files
| File | Purpose |
|---|---|
| `outbox.py` | `LoansWithOutbox` (change + event in one transaction) and `Relay` (lesson code) |
| `events.py` | `new_event()`: eventId (uuid4), eventType, occurredAt + data |
| `bus.py` | In-process bus: channel -> handlers |
| `consumers.py` | Idempotent consumers: notifications, active-loans projection |
| `asyncapi.json` | AsyncAPI 3.1.0 document: 2 channels, 2 `send` operations, 2 messages |
| `asyncapi_check.py` | Structural checks + payload validation (JSON Schema subset) |
| `app.py` | Demo: loans -> outbox -> relay -> consumers, contract-checked |
| `agent_assist.py` | Agent assist: a local model proposes the `LoanOverdue` entry; code decides |
| `test_events.py` | Outbox atomicity, ordering, redelivery, AsyncAPI checks |
| `test_agent_assist.py` | Proposal judge + check/retry loop (fake model server only) |
| `test_build_task.py` | Build task check (retries + dead letters) |
| `solution/outbox.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L200/09-event-driven-integration
python app.py
python asyncapi_check.py
python agent_assist.py          # fake model; --real for Ollama
python -m unittest -v
```
## Expected output (observed 2026-10-28, Python 3.12.15, Linux)

```
$ python app.py
borrow b1 by m1 -> outbox pending: 1
borrow b1 by m2 -> BookAlreadyOnLoan; outbox pending: 1 (rolled back, no event)
return loan 1   -> outbox pending: 2
relay run 1     -> published 2: [('loanCreated', 'LoanCreated'), ('loanReturned', 'LoanReturned')]
relay run 2     -> published 0 (nothing pending)
notifications   -> ['to m1: you borrowed b1', 'to m1: thanks for returning b1']
projection      -> active loans per member {'m1': 0}
asyncapi.json   -> 2 events checked, problems: []
```

```
$ python asyncapi_check.py
asyncapi.json: AsyncAPI 3.1.0, 2 channels, 2 operations: OK
```

## Agent assist (fake model server, observed 2026-10-28)
The agent only proposes; `check_document()` and the real event the code would emit decide. `asyncapi.json` is never written. The fake server's first reply is wrong on purpose (documented in `labs/_shared/local_agent/fake_model_server.py`).
```
$ python agent_assist.py
model: fake model server (deterministic stand-in, not a language model)
attempt 1: REJECTED
  - components.schemas.LoanOverduePayload: house rule - payload schema must list 'required' fields
  - operations.sendLoanOverdue: action must be 'send' or 'receive' (AsyncAPI 3), got 'publish'
  - sample event from code: payload.loanId: expected string, got int 7
  - sample event from code: payload.daysOverdue: expected string, got int 3
attempt 2: OK
proposal adds: channel loanOverdue (library.loans.overdue), operation sendLoanOverdue, message LoanOverdue
sample LoanOverdue event from code validates against the proposal: OK
asyncapi.json unchanged: True (a human reviews the proposal and edits the file)
```
With a real model: `ollama pull qwen2.5:1.5b`, then `python agent_assist.py --real` (`LOCAL_MODEL_URL`, `LOCAL_MODEL` select the server and model). Not run here.

Official validator (CI, pending-ci; needs Node.js 24): `npx --yes @asyncapi/cli@6.2.1 validate asyncapi.json`

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_first_reply_rejected_then_fixed (test_agent_assist.FakeModelLoopTest.test_first_reply_rejected_then_fixed) ... ok
test_main_prints_unchanged_file (test_agent_assist.FakeModelLoopTest.test_main_prints_unchanged_file) ... ok
test_base_document_is_not_modified (test_agent_assist.ValidateProposalTest.test_base_document_is_not_modified) ... ok
test_cannot_replace_existing_contract (test_agent_assist.ValidateProposalTest.test_cannot_replace_existing_contract) ... ok
test_good_fragment_passes (test_agent_assist.ValidateProposalTest.test_good_fragment_passes) ... ok
test_prose_is_rejected (test_agent_assist.ValidateProposalTest.test_prose_is_rejected) ... ok
test_sample_event_from_code_is_the_judge (test_agent_assist.ValidateProposalTest.test_sample_event_from_code_is_the_judge) ... ok
test_failure_does_not_block_later_events (test_build_task.DeadLetterTest.test_failure_does_not_block_later_events) ... ok
test_poison_event_is_dead_after_three_attempts (test_build_task.DeadLetterTest.test_poison_event_is_dead_after_three_attempts) ... ok
test_redelivery_stays_idempotent (test_build_task.DeadLetterTest.test_redelivery_stays_idempotent) ... ok
test_detects_asyncapi_2_style_operation (test_events.AsyncApiTest.test_detects_asyncapi_2_style_operation) ... ok
test_detects_operation_pointing_at_unknown_channel (test_events.AsyncApiTest.test_detects_operation_pointing_at_unknown_channel) ... ok
test_document_is_structurally_valid (test_events.AsyncApiTest.test_document_is_structurally_valid) ... ok
test_event_validation (test_events.AsyncApiTest.test_event_validation) ... ok
test_change_and_event_commit_together (test_events.OutboxTest.test_change_and_event_commit_together) ... ok
test_consumer_failure_keeps_event_pending (test_events.OutboxTest.test_consumer_failure_keeps_event_pending) ... ok
test_failed_event_rolls_back_the_change (test_events.OutboxTest.test_failed_event_rolls_back_the_change) ... ok
test_redelivery_is_ignored_by_idempotent_consumers (test_events.OutboxTest.test_redelivery_is_ignored_by_idempotent_consumers) ... ok
test_relay_publishes_in_commit_order_once (test_events.OutboxTest.test_relay_publishes_in_commit_order_once) ... ok
test_rule_violation_writes_no_event (test_events.OutboxTest.test_rule_violation_writes_no_event) ... ok

----------------------------------------------------------------------
Ran 20 tests in 2.123s

OK
```

## Build task
Make the relay survive a failing consumer: on an exception, keep the row pending, add 1 to `attempts`, store `last_error`, and continue with the next row. After 3 failed attempts set `dead_at` (a dead letter) and skip the row from then on. Add `dead_letters()` to list them.

- Solution: `solution/outbox.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `outbox.py`:
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
```
$ python -m unittest test_build_task   # against the solution, observed 2026-10-28
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first (the tasks and predictions are in the lesson's `tryIt` field), then run. `try_it.py` never edits the lab files.
```
$ python try_it.py
[1] relay run 1 -> relay process killed; outbox pending: 1
[1] relay run 2 -> naive consumer sent 2 mails, idempotent consumer sent 1 (ignored 1 duplicate)
[2] bookId -> book: ["payload: missing required field 'bookId'", "payload: unexpected field 'book'"]
```

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines (`python3`/`py -3.12` also work outside a venv). Use `\` in paths on Windows. Tests bind 127.0.0.1 on port 0 and create scratch folders inside the lab folder, never in a system temp path.

## Troubleshooting
| Symptom | Action |
|---|---|
| Relay raises and stops at the first failing consumer | Expected in the base lab (that is the build task). |
| `asyncapi must be a 3.x.y version` | You loaded an AsyncAPI 2 document; v3 moved operations out of channels and uses `send`/`receive`. |
| Agent assist prints `proposal rejected` | Read the listed problems; with `--real`, try a larger model. The checks, not the model, decide. |
