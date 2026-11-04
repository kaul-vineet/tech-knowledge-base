## Why it matters
A customer pays €10. The card is charged, but the response is lost. The shop can't tell whether the charge happened, so it retries — and charges twice.

## Mental model
Number every order before sending it. A cashier who sees ticket #42 again hands over a receipt copy instead of ringing it up twice. Ticket = idempotency key; receipt box = dedupe store.

```
A ─ POST key=k1 {amount: 10} ─▶ B: store[k1]=in-progress → charge → (201, ch_1)
A ✖ response lost
A ─ retry, SAME key k1 ───────▶ B: k1 seen, same fingerprint → replay (201, ch_1)
```

## How it works
1. **Lost responses + retries = duplicates.** With at-least-once delivery B may run one POST several times: 5 orders of 10 → 11 charges, total 110. → see lab step 2
2. **Same key on every retry; the server replays.** One key per logical operation, created before the retry loop. B stores key + fingerprint (body SHA-256) + response and replays it: 5 charges, total 50. → see lab step 3
3. **Error cases (IETF draft):** missing key → 400; same key, different payload → 422; retry while the original still runs → 409. → see lab step 4

## Common mistakes
- A new key per retry: deduplication never matches (tryIt 1).
- Storing the key separately after the side effect; a crash in between duplicates.
- Skipping the fingerprint check, so a reused key returns the wrong receipt.
