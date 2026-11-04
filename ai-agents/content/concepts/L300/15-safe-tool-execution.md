**Concept: safe tool execution – idempotency keys, dry-run, an approval queue and an audit log**

## Why it matters
Reading tools can be retried freely; acting tools cannot. A refund call that times out may already have moved the money – the response was simply late. The happy-path loop treats the timeout as "didn't happen" and retries, and the customer gets paid twice. An agent adds a second risk: the model, not a person, decided to act. Both are fixed outside the model, in the code that runs tools.

## Mental model
A bank teller with a stamped form. The agent fills in a numbered form (approval request with an idempotency key) and drops it in a tray (SQLite queue). A supervisor signs it. The teller processes each form number once; if a form comes back twice, the teller hands back the first receipt. Every step goes into the ledger (audit log).

```
model ─► send_refund(args) ─► gate: read-only? ─yes─► run now
                                 │ no
                                 ▼
               dry-run? ─yes─► "would refund 25.00" (nothing changes)
                                 │ no
                                 ▼
      approvals: #1 pending (key = hash(run, call, tool)) ─► human approves ─► executor
                                                                    │ POST + Idempotency-Key, retry on timeout
                                                                    ▼
                                                   payments API: key seen? replay : refund once
```

## How it works
1. **Classify tools.** A table in code marks `lookup_order` read-only and `send_refund` side-effecting and not idempotent, like MCP's `readOnlyHint` / `idempotentHint` – but our own table, because servers' hints are untrusted. → see lab step 2
2. **Queue, don't act.** The gate stores side-effecting calls as `pending` rows in SQLite and tells the model "queued as #1, nothing sent". The database survives restarts. → see lab step 3
3. **Human decision.** `decide(id, approver, approve)` changes `pending` to `approved` or `rejected`; only approved rows run. → see lab step 2
4. **Idempotency key.** The key is derived from run id, tool-call id and tool name, so the same call always carries the same key. The payments API stores key → response with the refund in one transaction, replays it for a repeat and answers 422 if the same key comes with a different body. → see lab step 4
5. **Audit log.** Every decision is an appended row: queued, approved, timeout_retry, executed. → see lab step 3
6. **Worked example.** First response delayed 0.6 s, client timeout 0.3 s. Naive retry: 2 refunds. Gate: 0 refunds before approval, then 1 refund; the retry came back with `Idempotent-Replayed: true`; audit `['queued', 'approved', 'timeout_retry', 'executed']`. → see lab step 2

## Failure modes
- **New key per attempt:** the key changes on every retry and duplicates return (Try it 1).
- **Crash between "sent" and "done":** a row stuck in `executing`; resume with the stored key (build task).
- **Rubber-stamp approvals:** approvals with no visible arguments; reviewers must see the exact amount and target.

## Common mistakes
- Treating a timeout as "nothing happened".
- Letting the model choose or see the idempotency key.
- Keeping the audit log in the same table the agent can update.
