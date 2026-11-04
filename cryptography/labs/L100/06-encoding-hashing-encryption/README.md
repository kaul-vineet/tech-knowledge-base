# 06 – Encoding vs hashing vs encryption

## Run
```bash
python compare.py
python -m unittest -v     # 12 tests: compare (4) + agent assist (8)
```

## Expected output (observed locally; the AES-GCM column changes every run)
```
technique        key     reversible?     output (truncated)
encoding/base64  none    yes, by anyone  ZGJfcGFzc3dvcmQ9U3VwM3JTM2NyZXQ=
encoding/hex     none    yes, by anyone  64625f70617373776f72643d53757033725333637265
hash/SHA-256     none    no (one-way)    df1e2c750bcd0e95ed602232da343dcc1aa20b09e655
encrypt/AES-GCM  secret  only with key   oDgF61CdqZFG/CnmPS3oOF0a/W5ECG8tLMwhbzBNqqhh
decrypt with wrong key -> InvalidTag
hash is deterministic  -> True
encryption randomised  -> True
RFC 4648 vectors       -> True True
Common mistakes:
 - 'encrypting' with base64 in config files / HTTP Basic auth without TLS
 - storing passwords with SHA-256 or encryption instead of Argon2id
 - using a hash where a keyed MAC (HMAC) or AEAD is needed
```

## Try it yourself
Same command in zsh (macOS) and PowerShell (Windows); `python -m base64 -d` avoids the macOS/GNU `base64` flag differences:
```bash
echo ZGJfcGFzc3dvcmQ9U3VwM3JTM2NyZXQ= | python -m base64 -d     # prints the "secret": no key needed
```
Observed locally: `db_password=Sup3rS3cret`

## Try it (concept experiments)
1. Run the three tools on `b"Hi"` instead of SECRET. *Predict first*, then compare.
2. Change SECRET's last character and count changed output characters. *Predict first*, then compare.
```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) base64: SGk= | hex: 4869 | sha256 hex chars: 64 | AES-GCM blob bytes: 30
2) base64 chars changed: 1 of 32 | sha256 hex chars changed: 56 of 64
```

## Agent assist: a local model reviews code for crypto misuse (the linter is the judge)
`review_me.txt` holds a small snippet with three planted misuses (it is read as text, never run).
`misuse_lint.py` is a deterministic AST linter: CRY001 `random` used for a token, CRY002 constant (reused) AEAD nonce,
CRY003 fast hash (MD5/SHA-x) on a password. `agent_assist.py` sends the numbered snippet to a model, parses
`CRYxxx line N: reason` lines and sorts every claim into CONFIRMED / MISSED / REJECTED against the linter.
The agent only explains; the verdict is computed by code.

```bash
python misuse_lint.py              # the judge on its own
python agent_assist.py             # default: deterministic fake model server on 127.0.0.1 (no download)
python agent_assist.py --real      # your local model: Ollama on the Mac mini or Windows PC
```
Observed locally (`misuse_lint.py`, then `agent_assist.py` with the fake server):
```
CRY001 line 9: random.choice() is a predictable PRNG
CRY002 line 21: AEAD nonce is a constant (reused per key)
CRY003 line 13: hashlib.md5() used on a password
3 finding(s) in review_me.txt
CONFIRMED CRY001 line 9   agent explains: the random module is a predictable PRNG; use secrets.token_urlsafe() or secrets.token_hex() for tokens.
CONFIRMED CRY003 line 13  agent explains: fast hash applied to a secret; store passwords with Argon2id (or scrypt), never MD5/SHA-x.
MISSED    CRY002 line 21  linter: AEAD nonce is a constant (reused per key) (agent did not report it)
REJECTED  CRY003 line 17  agent claim not backed by the linter: fast hash applied to a secret; store passwords with Argon2id (or scrypt), never MD5/SHA-x.
VERDICT (from linter, not agent): FAIL - 3 misuse(s)
```
The fake "agent" is a deliberately naive regex reviewer: it misses the nonce reuse (needs data flow: `NONCE` is
defined on line 5 and used on line 21) and over-flags the SHA-256 file fingerprint on line 17, which is a correct use.

Real model (`--real`): `ollama pull qwen2.5:1.5b`, keep Ollama running, optionally set `LOCAL_MODEL_URL`
(default `http://localhost:11434/v1`) and `LOCAL_MODEL` (default `qwen2.5:1.5b`). Wording and findings will differ
run to run and model to model; the linter verdict does not.
**Never paste real keys, passwords or tokens into a model prompt.** `agent_assist.py` refuses to send text that
looks like a PEM private key, a long hex, base64 or base64url string (a 32-byte key is 44 or 43 characters), a JWK private
member (`"d"`, `"k"`, ...) or an AWS key id (`find_secrets`), but that guard is a safety net, not a reason to try.

## If it fails
| Symptom | Action |
|---|---|
| `binascii.Error: Incorrect padding` | Input was truncated or is base64url (`-`/`_`); use `base64.urlsafe_b64decode` |
