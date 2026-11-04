# 05 · Idempotency keys

Payment service B commits each charge, then "loses" ~40% of responses (seeded). The client retries until it gets an answer (at-least-once delivery). Without a key every retry is a new charge; with an `Idempotency-Key` header and a server-side dedupe store, retries replay the stored response — exactly-once *effect*.

Files: `idempotency.py` (the lesson code), `helpers.py` (plumbing: quiet handler, `reply()`, background server), `try_it.py` (tryIt experiments), `test_idempotency.py`. `PaymentB.loss_rate` (default 0.4) sets how many responses are lost.

## Run
```bash
python idempotency.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; seeded)
```
--- Idempotency-Key OFF: 5 orders x 10 ---
order 1: 201 {'charge_id': 'ch_2'} after 2 attempt(s)
order 2: 201 {'charge_id': 'ch_4'} after 2 attempt(s)
order 3: 201 {'charge_id': 'ch_5'} after 1 attempt(s)
order 4: 201 {'charge_id': 'ch_8'} after 3 attempt(s)
order 5: 201 {'charge_id': 'ch_11'} after 3 attempt(s)
ledger: 11 charges, total 110 (expected 50)
--- Idempotency-Key ON: 5 orders x 10 ---
order 1: 201 {'charge_id': 'ch_1'} after 2 attempt(s)
order 2: 201 {'charge_id': 'ch_2'} after 1 attempt(s)
order 3: 201 {'charge_id': 'ch_3'} after 2 attempt(s)
order 4: 201 {'charge_id': 'ch_4'} after 1 attempt(s)
order 5: 201 {'charge_id': 'ch_5'} after 1 attempt(s)
ledger: 5 charges, total 50 (expected 50)
reuse key with amount 99 -> (422, {'title': 'Idempotency-Key is already used'})
no key at all            -> (400, {'title': 'Idempotency-Key is missing or malformed'})
```

## Test
```bash
python -m unittest -v          # Ran 4 tests ... OK  (includes the 409 in-progress case)
```

## Status codes used (from draft-ietf-httpapi-idempotency-key-header-08)
| Case | Response |
|---|---|
| Key missing on an operation that requires it | 400 |
| Same key reused with a different payload | 422 |
| Retry arrives while the original is still processing | 409 |
| Retry after the original completed | the original response, replayed |

The dedupe store here is an in-memory dict; real services persist it (same transaction as the side effect) and expire keys after a published TTL.

## Try it (real run, Python 3.12.15, Linux — seeded loss pattern, identical on every run)
```bash
python try_it.py
```
```
tryIt 1: new key per attempt -> ledger 11 charges, total 110 (expected 50)
tryIt 2: same key x3 -> [(201, {'charge_id': 'ch_1'}), (201, {'charge_id': 'ch_1'}), (201, {'charge_id': 'ch_1'})]; ledger 1 charge(s)
```
