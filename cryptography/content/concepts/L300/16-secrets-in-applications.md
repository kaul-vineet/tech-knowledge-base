## Why it matters
Leaked credentials are rarely stolen by breaking crypto; they are read from a log index, a crash report, a CI transcript or an environment dump. One debug line that prints request headers puts the API key into every log store, often for months. Four habits help: load secrets from the right place, keep them out of strings, redact at the log handler, rotate without downtime.

## Mental model
A secret is **radioactive material**: kept in a labelled container (`Secret`), passed through few hands, and checked with a detector (the scanner) wherever it might spill.

```
secret store / mounted file ─▶ load_secret() ─▶ Secret('***') ─▶ use (header) ─╳─▶ log handler ─▶ RedactingFilter ─▶ JSON lines
                                                                                     scan_log() in tests + agent-assist gate
rotation: [ current ] + [ previous until grace_until ]  ─▶ log which one was used
```

## How it works
1. **Loading.** `NAME_FILE` (a mounted file such as Docker's `/run/secrets/<name>`) wins over `NAME` (an environment variable). OWASP warns that environment variables are visible to all processes and end up in dumps. A missing secret fails closed → see lab steps 1-2.
2. **In memory.** `Secret` keeps the value in a bytearray, hides it in `repr` and can wipe that buffer. Python may still hold copies, so this reduces damage; it guarantees nothing → see tryIt 1.
3. **The fault.** A seeded request takes a debug path that logs the outgoing headers. The scanner finds a Bearer pattern, the configured key value and a sensitive key name on that JSON line → see lab step 1.
4. **Redaction.** The build task adds a `logging.Filter` on the handler. It masks sensitive key names, known secret values and token patterns in the message, args and nested `extra` fields → see lab step 4.
5. **Rotation.** The server stores SHA-256 hashes of the current and previous key and accepts the previous one until `grace_until`. Comparison uses `hmac.compare_digest`; logging which key matched shows when clients have moved → see lab step 3.
6. **Agent assist.** A local model reviews a redacted log; a gate refuses anything secret-like, and the scanner decides → see lab step 6.

Worked example (one lab run): with the fault, line 1 of the log produced three findings: BEARER, KNOWN_SECRET and SENSITIVE_KEY (Authorization). After the fix the scanner returned `[]` over 20 seeded requests. With a 24-hour grace window the old key returned `previous` at 23 h and `None` at 25 h. In agent assist the scanner found leaks on lines 2, 3 and 6; the naive model confirmed line 3, wrongly flagged line 4 (`token_ttl_seconds`) and missed lines 2 and 6.

## Failure modes
- **Debug logging in production.** Invisible until someone searches the log store; a CI test that scans emitted logs catches it at the commit.
- **Encoded leaks.** A base64 or URL-encoded secret slips past an exact-value scanner (tryIt 2); add the encodings you actually use.
- **Endless grace windows.** Without the "previous key used" metric, nobody knows when it is safe to drop the old key.
- **Over-redaction.** Masking every value hides what you need for debugging.

## Common mistakes
- Putting the filter on the logger instead of the handler, so records from child loggers bypass it.
- Logging `repr(config)` or whole request objects.
- Sending raw logs to an AI assistant or a ticket; redact first, then gate.
