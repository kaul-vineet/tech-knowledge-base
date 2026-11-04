## Why it matters
Your orders database holds millions of encrypted card tokens. Policy says the key must rotate every year, and a leaked backup means it must rotate *today*. Re-encrypting every row takes hours and, if it dies half-way, leaves you guessing which rows use which key. Envelope encryption turns rotation into a small, resumable job over 60-byte headers instead of a rewrite of all data.

## Mental model
A **safe-deposit box**: each record is locked with its own key (the DEK); all those small keys sit in one envelope locked by the master key (the KEK). Changing the master lock means re-locking envelopes, not boxes; each envelope's label names its master key.

```
record = { kid: "orders-kek:v2", wdek: AEAD(KEK_v2, DEK, aad=kid), n, ct: AEAD(DEK, data, aad=ctx) }
keyring: v1 (retired?)  v2 (decrypt)  v3 (primary: wraps new DEKs)
```

## How it works
1. **Seal.** Each record gets a fresh 256-bit DEK. The data is encrypted once with AES-256-GCM and the record id as AAD; the DEK is wrapped by the primary KEK and the key ID goes into the header → see lab step 1.
2. **Key ID binding.** The kid is the AAD of the wrap, so a header edited from v1 to v2 fails with InvalidTag instead of decrypting under the wrong key → see lab step 1 (and tryIt 1).
3. **Rotate.** Rotation adds a version and makes it primary. Old versions stay, so existing records still decrypt and nothing is re-encrypted → see lab step 2.
4. **Rewrap.** The job unwraps each DEK with its old version and wraps it with the primary. The data ciphertext is byte-for-byte unchanged. Each move is a JSON log line, the job ends with a `records_by_kid` metric, and records already on the primary are skipped, so a rerun resumes → see lab step 3.
5. **Retire.** Only when the metric shows zero records for a version may it leave the keyring. OpenBao's transit engine does the same with `rotate`, `rewrap` and `min_decryption_version` → see lab steps 4, 6 and 7.

Worked example (one lab run): a wrapped DEK is 60 bytes (12 nonce + 32 key + 16 tag). Rewrapping 1,000 records of 4 KiB re-encrypts 32,000 key bytes instead of 4,096,000 data bytes. In the fault run the job crashed after 1 record, leaving `{'orders-kek:v1': 5, 'orders-kek:v2': 1}`; the naive retire then left `1/6 decrypt` and 5 records LOST.

## Failure modes
- **Deleting a version too early.** Every record still wrapped by it becomes noise forever. You notice weeks later, when a read hits an old row; the `records_by_kid` metric shows it beforehand.
- **Interrupted rewrap.** A crash leaves a mix of versions. Harmless while old versions remain; dangerous if someone assumes the job finished.
- **Unbound header.** If the kid is not authenticated, an attacker or a bug can relabel records and steer which key is tried.
- **KEK outside a boundary.** In this lab the KEK is a Python variable. In production it stays in a KMS, HSM or OpenBao; only wrap/unwrap calls cross the boundary.

## Common mistakes
- Rotating by *replacing* the key instead of adding a version.
- Reusing one DEK for all records: one leak exposes everything.
- Treating "rotation done" as an event instead of checking the per-version record count.
