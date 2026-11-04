# Run log for content/explain/NN.md (cryptography)

Every output quoted in `content/explain/*.md` was produced by the commands below in the Linux sandbox
(Python 3.12.15, cryptography 50.0.2, Python ssl on OpenSSL 3.3.7; node 24 unused). Lessons 01-10 were run on
**2026-11-02** (first writer), lessons 11-27 on **2026-11-03** (this pass). Checked by `research/explain_checks.py`.

## Environment and method
- Each command was run from the lab folder with `PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1`, one at a time (slow, flaky storage),
  through the helper below; stdout+stderr are copied verbatim. Long unit-test output is filtered with `grep` (the filter is part of the recorded command).
- Not installed, so marked "Expected (not run here)" in the explanations and taken from the lab READMEs / official docs, not from this log:
  OpenSSL CLI, step CLI, KeyStore Explorer, minisign, Sigstore cosign, OpenBao, Gitleaks, liboqs-python, SoftHSM2/python-pkcs11,
  Python 3.15 + OpenSSL 3.5 (TLS hybrid group probe), OpenMLS/cargo, Ollama (agent labs ran their built-in fake model), Wireshark, CyberChef.
- Lesson 10 reused the lab-9 PKI written by `local_ca.py --out` to a scratch folder in the session workspace (not in the topic).
- Lessons 24, 25 and 27: the worked-problem arithmetic was checked with the `python -c` one-liners recorded below.
- Capstone (22): the unittest run left an empty temp folder `labs/L400/22-capstone/tmptx2tehfe` (TemporaryDirectory cleanup failed
  on the slow mount); it was deleted. Two older leftovers of the same kind (`tmp_bbxhqw4`, `tmphek9w_zh`) predate this pass and were left untouched.

## Outputs that differ from the lab READMEs / lesson JSON
- Timings (µs, ms, test durations) differ everywhere, as the READMEs warn; only the ones that change an argument are listed.
- 01: `openssl` CLI is not installed (`/bin/sh: line 1: openssl: command not found`); the bundled OpenSSL line and the KATs matched.
- 03, 05, 06: random tokens, salts, nonces and Argon2/scrypt timings differ per run, as the READMEs say.
- 09: dates are the run date (`2026-11-02 -> 2026-12-02` vs README `2026-10-28 -> 2026-11-27`); try_it 2 printed `DER 422 B, PEM 627 B`
  vs README `DER 424 B, PEM 631 B` (ECDSA DER signatures vary in length by a few bytes); the ratio 1.49 matched.
- 14: the signer key id is random per run (`eeaa4068b2dd254d` here, `4793bac0a5cc620b` in the README).
- 15: naive-loop ns values differ (558/727/895/1178 vs 567/730/897/1187; 403/1035 and 123 vs 398/1023 and 119); ratios 2.57 / 1.00 matched.
- 16: the real output prints the full demo bearer token in the leaked log line; the explanation trims it with "…".
- 17: ML-DSA-65 sign 864.3 µs here vs 1380.1 µs in the README/ADR (the ADR notes run-to-run variance); sizes and counts matched.
- 18: hybrid handshake 431.5 µs vs 390.5 (X25519 144.8 vs 140.7); Ed25519 verify 314.0 µs vs 108.0 (noise); sizes matched.
- 19: **KMS-style remote signing measured 587.5 µs here vs ≈5001.5 µs in the README and ADR-0019.** On this run option B met the
  1 ms constraint, which weakens the ADR's stated latency argument against B (B was still ~15x the token handle's 40.3 µs).
  The explanation reports this; the ADR itself was not edited.
- 20: commit_and_process_ms 1.6 / 17.3 / 86.0 vs 1.7 / 71.8 / 89.5; all counts and bytes matched.
- 21: build-task solution `Ran 4 tests in 0.109s` vs 4.843s; full suite `Ran 14 tests in 29.833s` vs 182.982s.
- 22: M2 `"no client cert": "refused (SSLEOFError)"` vs README `refused (SSLError)` (both: the KMS aborted the handshake); tests 30.858s vs 37.749s.
- 23-25: every line of each theorem's `checkOutput` in content/L500.json appeared verbatim in the run (compared by script).
- 25: lesson JSON problem 25-P8's solution text quotes `147/1000` toy-Regev errors, but the stored checkOutput and this run show
  `122/1000` (an inconsistency inside L500.json; not edited, noted in 25.md).
- 27-P3: log10(26!) = 26.61 gives a unicity distance of ~38 letters, above Shannon's rounded estimate (as the lesson's solution says).
- Everything else matched the READMEs.

## Helper (kept in the session folder, not in the topic)
### explain_run.py
```python
import subprocess, sys, datetime, pathlib, os
# usage: explain_run.py NN labdir_rel "command"
nn, lab, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
root = pathlib.Path('/mnt/workspace/working/kb/cryptography')
cwd = root / lab
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=env, timeout=900)
out = p.stdout + (p.stderr if p.stderr else '')
rec = f"\n### [{nn}] {datetime.date.today()} — `cd {lab} && {cmd}` (exit {p.returncode})\n```\n{out.rstrip()}\n```\n"
with open(pathlib.Path(__file__).parent / 'explain_raw' / f'{nn}.md', 'a') as f: f.write(rec)
print(rec)
```

## Recorded runs

## Lesson 01

### [01] 2026-11-02 — `cd labs/L100/01-setup-workbench && python sanity_check.py` (exit 0)
```
python                 3.12.15
machine                Linux x86_64
cryptography           50.0.2
cryptography_pinned    True
openssl                OpenSSL 4.0.3 29 Sep 2026
sha256_known_answer    True
secrets_token_len      32
aesgcm_roundtrip       True
argon2id_available     True
WORKBENCH OK
```

### [01] 2026-11-02 — `cd labs/L100/01-setup-workbench && python -m unittest -v 2>&1` (exit 0)
```
test_argon2id (test_sanity_check.TestWorkbench.test_argon2id) ... ok
test_known_answer_and_roundtrip (test_sanity_check.TestWorkbench.test_known_answer_and_roundtrip) ... ok
test_pinned_version (test_sanity_check.TestWorkbench.test_pinned_version) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.009s

OK
```

### [01] 2026-11-02 — `cd labs/L100/01-setup-workbench && python try_it.py` (exit 0)
```
1) PINNED=49.0.0 -> cryptography_pinned: False | WORKBENCH NOT READY
2) sha256('abc\n') = edeaaff3f1774ad2888673770c6d64097e391bc362d7d6fb34982ddf0efd18cb | matches NIST 'abc': False
```

### [01] 2026-11-02 — `cd labs/L100/01-setup-workbench && printf abc | sha256sum; openssl version 2>&1 || true` (exit 0)
```
ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad  -
/bin/sh: line 1: openssl: command not found
```

## Lesson 02

### [02] 2026-11-02 — `cd labs/L100/02-hashing-integrity && python hash_and_hmac.py` (exit 0)
```
sha256('abc')        ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad True
sha256('')           e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 True
file (python)        e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d
file (OS tool)       e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d via sha256sum
stdlib file_digest   e23c0cda5bcdecddec446b54439995c7260c8cdcf2953eec9f5cdb6948e5898d
after 1-byte tamper  64ae272a9529a4637e6f2a81ed6e1cc111f52f288435df80c2871c416c450eeb MISMATCH -> tampered
HMAC RFC4231 TC2     5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843 True
verify good msg      True
verify edited msg    False
verify wrong key     False
```

### [02] 2026-11-02 — `cd labs/L100/02-hashing-integrity && python try_it.py` (exit 0)
```
1) chunk sizes [7, 4096, 65536] -> distinct digests: 1 | digest: e23c0cda5bcdecdd...
2) jefe tag: f5886a2776d40a67... | verifies against Jefe tag: False | bits differing: 136 of 256
```

### [02] 2026-11-02 — `cd labs/L100/02-hashing-integrity && python -m unittest 2>&1 | tail -3` (exit 0)
```
Ran 4 tests in 0.032s

OK
```

## Lesson 03

### [03] 2026-11-02 — `cd labs/L100/03-secure-randomness && python randomness.py` (exit 0)
```
api_token_urlsafe  fZY7qc_gJ8QoEeO_ZIq1VycPIj0kKriQIHq2uEO44a8
session_id_hex     f1835511e7ef5e73bb35a3f40688cd1d
aes256_key         40aa9a489fcca493b78b3c810a97142a8da8f347e33bfb5f7ddb51cef9f9ecc7
gcm_nonce          8aee0593f6782e2e50409142
pin_6_digits       139900
insecure token       2ff56b2cc5980a19382c5a939fc48556
attacker found seed  1793621970 == issued_at: True (0.095s)
attacker can mint    True
same seed same token True
secrets differs      True
```

### [03] 2026-11-02 — `cd labs/L100/03-secure-randomness && python try_it.py` (exit 0)
```
1) token issued 2 h ago, window +/-1 h -> attacker finds: None
   same token, window +/-3 h       -> attacker finds seed == issued_at: True
2) secrets.token_hex(16) scanned over 7,201 seeds -> attacker finds: None
```

### [03] 2026-11-02 — `cd labs/L100/03-secure-randomness && python -m unittest 2>&1 | tail -3` (exit 0)
```
Ran 3 tests in 0.042s

OK
```

## Lesson 04

### [04] 2026-11-02 — `cd labs/L100/04-authenticated-encryption && python aead_demo.py` (exit 0)
```
RFC 8439 2.8.2 ChaCha20-Poly1305 vector: True
GCM spec TC14 AES-256-GCM vector:        True
--- AES-256-GCM (blob 42 bytes = 12 nonce + 14 ct + 16 tag)
  decrypt ok         card=4111-1111
  1 bit flipped      InvalidTag (rejected)
  AAD changed        InvalidTag (rejected)
--- ChaCha20-Poly1305 (blob 42 bytes = 12 nonce + 14 ct + 16 tag)
  decrypt ok         card=4111-1111
  1 bit flipped      InvalidTag (rejected)
  AAD changed        InvalidTag (rejected)
nonce reuse leaks p1^p2: True
attacker who knows p1 recovers p2: b'retreat at dusk!'
```

### [04] 2026-11-02 — `cd labs/L100/04-authenticated-encryption && python try_it.py` (exit 0)
```
1) nonce bit flipped -> InvalidTag (rejected)
2) plaintext    0 B -> blob   28 B (overhead 28 B)
2) plaintext   14 B -> blob   42 B (overhead 28 B)
2) plaintext 1000 B -> blob 1028 B (overhead 28 B)
```

### [04] 2026-11-02 — `cd labs/L100/04-authenticated-encryption && python -m unittest 2>&1 | tail -3` (exit 0)
```
Ran 5 tests in 0.013s

OK
```

## Lesson 05

### [05] 2026-11-02 — `cd labs/L100/05-password-storage && python -c 'from cryptography.hazmat.primitives.kdf.argon2 import Argon2id; print("import ok")'` (exit 0)
```
import ok
```

### [05] 2026-11-02 — `cd labs/L100/05-password-storage && python passwords.py` (exit 0)
```
RFC 9106 Argon2id tag: 0d640df58d78766c08c037a34a8b53c9d01ef0452d75b65eb52520e96b01e659
RFC 7914 scrypt  dk  : fdbabe1c9d3472007856e7190d01e9fe ...
argon2id hash (0.074s): $argon2id$v=19$m=19456,t=2,p=1$g5ceMJLum61jNjwqIKSj/Q$BR6iDe0IvizvcF8tBUHluQQLV7C8DEoXxEOKIQTBX6Q
same password, new salt -> different hash: True
verify right password: True
verify wrong password: False
scrypt fallback (1.303s): scrypt$131072$8$1$cYjfszzyB4zk4sR/tSDnyA==$v3LUtC2UV4JSvpa7QLj5W2OIC2xRWZFOhe2ILoge3B4=
scrypt verify right/wrong: True False
```

### [05] 2026-11-02 — `cd labs/L100/05-password-storage && python try_it.py` (exit 0)
```
1) new PHC prefix: $argon2id$v=19$m=38912,t=2,p=1$ | time 0.175s -> 0.329s (x1.9)
   old m=19456 hash still verifies: True
2) verify 'hunter2'   -> True
2) verify 'hunter2 '  -> False
2) verify 'Hunter2'   -> False
```

### [05] 2026-11-02 — `cd labs/L100/05-password-storage && python -m unittest 2>&1 | tail -3` (exit 0)
```
Ran 3 tests in 6.807s

OK
```

## Lesson 06

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && python compare.py` (exit 0)
```
technique        key     reversible?     output (truncated)
encoding/base64  none    yes, by anyone  ZGJfcGFzc3dvcmQ9U3VwM3JTM2NyZXQ=
encoding/hex     none    yes, by anyone  64625f70617373776f72643d53757033725333637265
hash/SHA-256     none    no (one-way)    df1e2c750bcd0e95ed602232da343dcc1aa20b09e655
encrypt/AES-GCM  secret  only with key   9EazfX7xtCFXBF0Ws+wVEtOII7PqlGECmzWCW2arO3Hc
decrypt with wrong key -> InvalidTag
hash is deterministic  -> True
encryption randomised  -> True
RFC 4648 vectors       -> True True
Common mistakes:
 - 'encrypting' with base64 in config files / HTTP Basic auth without TLS
 - storing passwords with SHA-256 or encryption instead of Argon2id
 - using a hash where a keyed MAC (HMAC) or AEAD is needed
```

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && echo ZGJfcGFzc3dvcmQ9U3VwM3JTM2NyZXQ= | python -m base64 -d; echo` (exit 0)
```
db_password=Sup3rS3cret
```

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && python misuse_lint.py` (exit 0)
```
CRY001 line 9: random.choice() is a predictable PRNG
CRY002 line 21: AEAD nonce is a constant (reused per key)
CRY003 line 13: hashlib.md5() used on a password
3 finding(s) in review_me.txt
```

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && python agent_assist.py` (exit 0)
```
CONFIRMED CRY001 line 9   agent explains: the random module is a predictable PRNG; use secrets.token_urlsafe() or secrets.token_hex() for tokens.
CONFIRMED CRY003 line 13  agent explains: fast hash applied to a secret; store passwords with Argon2id (or scrypt), never MD5/SHA-x.
MISSED    CRY002 line 21  linter: AEAD nonce is a constant (reused per key) (agent did not report it)
REJECTED  CRY003 line 17  agent claim not backed by the linter: fast hash applied to a secret; store passwords with Argon2id (or scrypt), never MD5/SHA-x.
VERDICT (from linter, not agent): FAIL - 3 misuse(s)
```

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && python try_it.py` (exit 0)
```
1) base64: SGk= | hex: 4869 | sha256 hex chars: 64 | AES-GCM blob bytes: 30
2) base64 chars changed: 1 of 32 | sha256 hex chars changed: 56 of 64
```

### [06] 2026-11-02 — `cd labs/L100/06-encoding-hashing-encryption && python -m unittest 2>&1 | tail -3` (exit 0)
```
Ran 12 tests in 4.009s

OK
```

## Lesson 07

### [07] 2026-11-02 — `cd labs/L200/07-ed25519-signatures && python signatures.py` (exit 0)
```
RFC 8032 TEST 1 public key: True
RFC 8032 TEST 1 signature:  True
sizes: raw private 32 B, raw public 32 B, PEM private 119 B, PEM public 113 B
signature file: app-1.0.tar.gz.sig 64 bytes
verify original:        True
verify with other key:  False
verify after 1 change:  False
```

### [07] 2026-11-02 — `cd labs/L200/07-ed25519-signatures && python try_it.py` (exit 0)
```
1) same key + same message -> identical signatures: True | first 8 bytes: 8081583b8784835c
2) raw 32 B | PEM 113 B | OpenSSH 80 B | PEM loads back to same key: True
   OpenSSH form: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINdamAGCsQq31Uv+08lkBzoO4XLz2qYjJa8CGmj3B1Ea
```

### [07] 2026-11-02 — `cd labs/L200/07-ed25519-signatures && python -m unittest -v 2>&1 | tail -12` (exit 0)
```
test_key_id_is_stable_and_short (test_build_task.TestKeyring.test_key_id_is_stable_and_short) ... ok
test_rotation (test_build_task.TestKeyring.test_rotation) ... ok
test_public_pem_has_no_private_material (test_signatures.TestSignatures.test_public_pem_has_no_private_material) ... ok
test_rfc8032_test1 (test_signatures.TestSignatures.test_rfc8032_test1) ... ok
test_roundtrip_through_pem (test_signatures.TestSignatures.test_roundtrip_through_pem) ... ok
test_tamper_and_wrong_key (test_signatures.TestSignatures.test_tamper_and_wrong_key) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.031s

OK
```

### [07] 2026-11-02 — `cd labs/L200/07-ed25519-signatures && BUILD_IMPL=signatures python -m unittest test_build_task 2>&1 | tail -4` (exit 0)
```
----------------------------------------------------------------------
Ran 2 tests in 0.027s

FAILED (errors=2)
```

## Lesson 08

### [08] 2026-11-02 — `cd labs/L200/08-hybrid-encryption && python seal_box.py` (exit 0)
```
RFC 7748 6.1 Alice public:   True
RFC 7748 6.1 shared secret:  True
sealed 29 B -> 77 B (overhead 48 = 32 eph_pub + 16 tag)
bob opens:    b'db password rotation at 02:00'
same msg sealed twice -> different blobs: True
eve opens:    InvalidTag (rejected)
aad changed:  InvalidTag (rejected)
eph swapped:  InvalidTag (rejected)
```

### [08] 2026-11-02 — `cd labs/L200/08-hybrid-encryption && python try_it.py` (exit 0)
```
1) plaintext    0 B -> blob   48 B
1) plaintext   29 B -> blob   77 B
1) plaintext 4096 B -> blob 4144 B
2) receiver uses info v2, sender used v1 -> InvalidTag (keys differ, domain separation works)
```

### [08] 2026-11-02 — `cd labs/L200/08-hybrid-encryption && python -m unittest -v 2>&1 | tail -6` (exit 0)
```
test_wrong_key_tamper_aad (test_seal_box.TestSealBox.test_wrong_key_tamper_aad) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.062s

OK (skipped=1)
```

## Lesson 09

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python local_ca.py` (exit 0)
```
root: CN=KB Local Root CA | CA: True
leaf SAN: ['localhost', '127.0.0.1']
leaf valid: 2026-11-02 -> 2026-12-02
localhost              OK, chain length 2
wrong host             FAIL: validation failed: leaf certificate has no matching subjectAltName
31 days later          FAIL: validation failed: cert is not valid at validation time
untrusted root         FAIL: validation failed: candidates exhausted: all candidates exhausted with no interior errors
```

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python try_it.py` (exit 0)
```
1) ask localhost       FAIL: validation failed: leaf certificate has no matching subjectAltName
1) ask ip-only.test    OK, chain length 2
2) DER 422 B, PEM 627 B, ratio 1.49; DER->cert == PEM->cert: True
```

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python agent_assist.py` (exit 0)
```
wrong host    verifier=FAIL  code says HOSTNAME_MISMATCH agent says HOSTNAME_MISMATCH CONFIRMED
              agent explains: the name the client asked for is not in the certificate's SAN list.
expired       verifier=FAIL  code says EXPIRED           agent says EXPIRED           CONFIRMED
              agent explains: the certificate's validity period has ended.
clock skew    verifier=FAIL  code says NOT_YET_VALID     agent says EXPIRED           REJECTED
untrusted CA  verifier=FAIL  code says UNTRUSTED_ISSUER  agent says UNTRUSTED_ISSUER  CONFIRMED
              agent explains: no trusted root signed this chain.
VERDICTS come from the verifier; categories from diagnose(); the agent only explains.
```

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python -m unittest 2>&1 | tail -3` (exit 0)
```
untrusted CA  verifier=FAIL  code says UNTRUSTED_ISSUER  agent says UNTRUSTED_ISSUER  CONFIRMED
              agent explains: no trusted root signed this chain.
VERDICTS come from the verifier; categories from diagnose(); the agent only explains.
```

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 13 tests in 1.433s
OK
```

### [09] 2026-11-02 — `cd labs/L200/09-local-ca && python local_ca.py --out ../../../../../../.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/pki9 | tail -1; ls ../../../../../../.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/pki9` (exit 0)
```
wrote ca.pem, server.pem, server-key.pem
ca.pem
server-key.pem
server.pem
```

## Lesson 10

### [10] 2026-11-02 — `cd labs/L200/10-tls-localhost && python tls_localhost.py` (exit 0)
```
Python ssl uses OpenSSL 3.3.7 7 Apr 2026
trusted CA       TLSv1.3 TLS_AES_256_GCM_SHA384 (256-bit) -> b'hello over TLS\n'
wrong hostname   REFUSED verify_code=62: Hostname mismatch, certificate is not valid for 'example.com'.
untrusted CA     REFUSED verify_code=20: unable to get local issuer certificate
```

### [10] 2026-11-02 — `cd labs/L200/10-tls-localhost && python try_it.py` (exit 0)
```
1) client max TLS 1.2 -> TLSv1.2 ECDHE-ECDSA-AES256-GCM-SHA384
2) server_hostname='127.0.0.1' -> TLSv1.3 b'hello over TLS\n'
```

### [10] 2026-11-02 — `cd labs/L200/10-tls-localhost && python -m unittest -v 2>&1 | grep -E 'skip|^Ran|^OK|FAIL'` (exit 0)
```
test_trusted_and_untrusted (test_openssl_cli.TestOpenSSLClient.test_trusted_and_untrusted) ... skipped 'openssl CLI not installed'
Ran 7 tests in 1.001s
OK (skipped=1)
```

## Lesson 11

### [11] 2026-11-03 — `cd labs/L200/11-tokens && python tokens.py` (exit 0)
```
valid token: alice (211 chars)
alg none        naive ACCEPTS role=admin | safe rejects (algorithm 'none' not allowed)
key confusion   naive ACCEPTS role=admin | safe rejects (algorithm 'HS256' not allowed)
expired         naive ACCEPTS role=?     | safe rejects (expired or no exp)
wrong audience  naive ACCEPTS role=?     | safe rejects (wrong audience)
payload edited  naive rejects            | safe rejects (bad signature)
```

### [11] 2026-11-03 — `cd labs/L200/11-tokens && python try_it.py` (exit 0)
```
1) expired 20 s ago, leeway=30: accepted
1) expired 20 s ago, leeway= 0: rejected (expired or no exp)
2) payload read with NO key: {'sub': 'alice', 'email': 'alice@example.com', 'aud': 'orders-api', 'exp': 1800000060}
```

### [11] 2026-11-03 — `cd labs/L200/11-tokens && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 13 tests in 0.012s
OK
```

## Lesson 12

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && python envelope.py` (exit 0)
```
sealed 6 records with orders-kek:v1 | header: {'kid': 'orders-kek:v1', 'ctx': 'order-1'}
rotate -> orders-kek:v2 | old records still: 6/6 decrypt
{"event": "rewrap", "id": "order-1", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-2", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-3", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-4", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-5", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-6", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"metric": "records_by_kid", "orders-kek:v2": 6}
data ciphertext unchanged by rewrap: True
retire v1 after a full rewrap: 6/6 decrypt
--- fault: rotate again, the rewrap job crashes, the operator deletes v2 anyway
rotate -> orders-kek:v3
{"event": "rewrap", "id": "order-1", "from": "orders-kek:v2", "to": "orders-kek:v3"}
job: rewrap job crashed after 1 records | counts: {'orders-kek:v2': 5, 'orders-kek:v3': 1}
after retire v2: 1/6 decrypt; LOST ['order-2', 'order-3', 'order-4', 'order-5', 'order-6'] ({'no KEK for orders-kek:v2'})
```

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && python try_it.py` (exit 0)
```
1) relabelled header: InvalidTag - the kid is bound to the wrapped DEK as AAD
2) wrapped DEK = 60 B (12 nonce + 32 key + 16 tag); rewrapping 1000 x 4096 B records re-encrypts 32,000 key bytes instead of 4,096,000 data bytes
```

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && python solution_retire.py` (exit 0)
```
injected: rewrap job crashed after 2 records
retire refused: orders-kek:v1 still wraps 2 record(s): finish the rewrap job first
resumed job moved 2 record(s); 4/4 decrypt
```

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && BUILD_IMPL=envelope python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_primary_cannot_be_retired (test_build_task.TestRetireAfterRewrap.test_primary_cannot_be_retired)
FAIL: test_retire_refused_while_records_use_the_version (test_build_task.TestRetireAfterRewrap.test_retire_refused_while_records_use_the_version)
Ran 3 tests in 0.043s
FAILED (failures=2)
```

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 3 tests in 0.002s
OK
```

### [12] 2026-11-03 — `cd labs/L300/12-envelope-rotation && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 11 tests in 0.003s
OK (skipped=1)
```

## Lesson 13

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && python cert_lifecycle.py` (exit 0)
```
{"hour": 0, "metric": "cert_expires_in_hours", "value": 159.0, "handshake": "ok", "renewals": 0}
{"hour": 24, "metric": "cert_expires_in_hours", "value": 135.0, "handshake": "ok", "renewals": 0}
{"hour": 48, "metric": "cert_expires_in_hours", "value": 111.0, "handshake": "ok", "renewals": 0}
{"hour": 72, "metric": "cert_expires_in_hours", "value": 87.0, "handshake": "ok", "renewals": 0}
{"hour": 96, "metric": "cert_expires_in_hours", "value": 63.0, "handshake": "ok", "renewals": 0}
{"hour": 120, "metric": "cert_expires_in_hours", "value": 39.0, "handshake": "ok", "renewals": 0}
{"hour": 144, "metric": "cert_expires_in_hours", "value": 15.0, "handshake": "ok", "renewals": 0}
{"hour": 160, "metric": "cert_expires_in_hours", "value": -1.0, "handshake": "FAIL", "renewals": 0}
{"hour": 168, "metric": "cert_expires_in_hours", "value": -9.0, "handshake": "FAIL", "renewals": 0}
static server: first failed handshake at hour 160, 32 failed hours of 192
lifetime: 160.0 h, notBefore backdated 1 h
CRL check now:         revoked (key_compromise)
CRL check other cert:  good
CRL check 25 h later:  stale CRL
skew 5 min, notBefore = issue time: False
skew 5 min, notBefore backdated 1 h: True
```

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && python try_it.py` (exit 0)
```
1) distinct renewal hours for 100 servers: no jitter 1, jitter 20
2) client clock  5 min slow: handshake ok
2) client clock 59 min slow: handshake ok
2) client clock 61 min slow: handshake FAIL (not yet valid)
```

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && python solution_renewal.py` (exit 0)
```
renewing server, 21 days: 0 failed handshakes, 4 renewals, 0 alerts
CA down hours 90-124: 0 failed handshakes, 4 renewals, 6 alert lines
first alert: {"alert": "cert_expiry_soon", "hours_left": 40.0}
```

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && BUILD_IMPL=cert_lifecycle python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
ERROR: test_jitter_spreads_a_fleet (test_build_task.TestRenewal.test_jitter_spreads_a_fleet)
FAIL: test_ca_outage_alerts_and_recovers (test_build_task.TestRenewal.test_ca_outage_alerts_and_recovers)
FAIL: test_no_expired_cert_is_ever_served (test_build_task.TestRenewal.test_no_expired_cert_is_ever_served)
Ran 3 tests in 0.179s
FAILED (failures=2, errors=1)
```

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 3 tests in 0.241s
OK
```

### [13] 2026-11-03 — `cd labs/L300/13-cert-lifecycle && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 8 tests in 0.275s
OK
```

## Lesson 14

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && python release_sign.py` (exit 0)
```
manifest lists 4 files; signer eeaa4068b2dd254d
clean release                installed 4 files
installer pins another key   REJECTED: unknown signer eeaa4068b2dd254d
fault: attacker swapped README.txt and added app/zz_extra.pth; manifest + signature unchanged
tampered release             installed 5 files
```

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && python try_it.py` (exit 0)
```
1) both keys trusted  v1.0.0: 4 files                                  v2.0.0: 4 files
1) old key removed    v1.0.0: REJECTED (unknown signer 34750f98bd59fcfc) v2.0.0: 4 files
2) one hex digit changed in MANIFEST.json: manifest signature invalid
```

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && python solution_strict.py` (exit 0)
```
clean release:    4 files installed
tampered release: REJECTED: unknown file(s): ['app/zz_extra.pth']
```

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && BUILD_IMPL=release_sign python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_seeded_attack_rejected (test_build_task.TestStrictInstall.test_seeded_attack_rejected)
FAIL: test_swapped_file_rejected (test_build_task.TestStrictInstall.test_swapped_file_rejected)
FAIL: test_unknown_file_rejected (test_build_task.TestStrictInstall.test_unknown_file_rejected)
Ran 4 tests in 0.192s
FAILED (failures=3)
```

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 4 tests in 0.018s
OK
```

### [14] 2026-11-03 — `cd labs/L300/14-supply-chain-signing && python -m unittest -v 2>&1 | grep -E 'skip|^Ran|^OK|FAILED'` (exit 0)
```
test_sign_verify_and_detect_edit (test_cli_equivalents.TestMinisign.test_sign_verify_and_detect_edit) ... skipped 'minisign not installed'
Ran 9 tests in 0.038s
OK (skipped=1)
```

## Lesson 15

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python wycheproof_check.py` (exit 0)
```
aes_gcm_subset.json    5/5 pass
derived_vectors.json   1/5 pass
ed25519_subset.json    11/11 pass
  FAIL tcId 9001 ['TruncatedTag']: expected invalid, wrapper said valid
  FAIL tcId 9002 ['TruncatedTag']: expected invalid, wrapper said valid
  FAIL tcId 9101 ['TrailingBytes']: expected invalid, wrapper said valid
  FAIL tcId 9102 ['NonCanonicalS']: expected invalid, wrapper said valid
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python try_it.py` (exit 0)
```
1) 4-byte tag accepted by lenient wrapper: True | forgery odds per try: 1 in 4,294,967,296 (16-byte tag: 1 in 2**128)
2) naive loop, wrong at byte 0/8/16/31: 558 ns < 727 ns < 895 ns < 1178 ns | increasing: True
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python timing_demo.py` (exit 0)
```
naive loop           wrong at byte 0:    403 ns | wrong at byte 31:   1035 ns | ratio 2.57
hmac.compare_digest  wrong at byte 0:    123 ns | wrong at byte 31:    123 ns | ratio 1.00
A ratio well above 1 means time reveals how many leading bytes were right.
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python nonce_guard.py` (exit 0)
```
in-process tripwire: NonceReuseError on the 2nd seal with the same nonce
buggy seeded nonces  2 restarts x 2 messages: tripwire silent, offline scan finds 2 reused [[0, 2], [1, 3]]
os.urandom nonces    2 restarts x 2 messages: tripwire silent, offline scan finds 0 reused []
attacker knows run-1 message 0, recovers run-2 message 0: b'pay mal 9999'
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python solution_strict.py` (exit 0)
```
aes_gcm_subset.json    5/5 pass
derived_vectors.json   5/5 pass
ed25519_subset.json    11/11 pass
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && BUILD_IMPL=wycheproof_check python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_every_vector_passes (test_build_task.TestStrictWrappers.test_every_vector_passes)
FAIL: test_non_canonical_signatures_rejected (test_build_task.TestStrictWrappers.test_non_canonical_signatures_rejected)
FAIL: test_truncated_tag_rejected (test_build_task.TestStrictWrappers.test_truncated_tag_rejected)
Ran 3 tests in 0.158s
FAILED (failures=3)
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 3 tests in 0.024s
OK
```

### [15] 2026-11-03 — `cd labs/L300/15-testable-misuse && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 12 tests in 0.072s
OK
```

## Lesson 16

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python secrets_app.py` (exit 0)
```
loaded from file: Secret('***') | length 40
6 JSON log lines, e.g. {"headers": {"Accept": "application/json", "Authorization": "Bearer sk_demo_5993718a7211a334e3a12aea88313527"}, "level": "DEBUG", "msg": "upstream request", "order": 1}
scanner findings:
  line 1: BEARER (pattern)
  line 1: KNOWN_SECRET (value of a configured secret)
  line 1: SENSITIVE_KEY (Authorization)
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python try_it.py` (exit 0)
```
1) plain str : {'service': 'orders', 'api_key': 'sk_demo_c0ffeec0ffeec0ffeec0ffeec0ffee'}
1) Secret    : {'service': 'orders', 'api_key': Secret('***')}
2) scan with known=[key]:           []
2) scan with known=[key, b64(key)]: [(1, 'KNOWN_SECRET', 'value of a configured secret')]
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python solution_redact.py` (exit 0)
```
{"headers": {"Accept": "application/json", "Authorization": "[REDACTED]"}, "level": "DEBUG", "msg": "upstream request", "order": 1}
scanner findings after the fix: []
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python agent_assist.py` (exit 0)
```
sent to the model (redacted):
  {"level": "INFO", "msg": "service start", "config": "/etc/orders/app.yaml"}
  {"headers": {"Authorization": "[REDACTED]"}, "level": "DEBUG", "msg": "upstream request"}
  db_password: "[REDACTED]"
  token_ttl_seconds: 3600
  {"level": "INFO", "msg": "order sent", "status": 200}
  smtp_url: smtp://[REDACTED]@mail.local:587
line 2: MISSED by agent (scanner found it)
line 3: CONFIRMED - agent explains: a credential appears to be logged here; remove it or log a
line 4: REJECTED (scanner: no leak)
line 6: MISSED by agent (scanner found it)
LEAKS = [2, 3, 6] (decided by scan_log); the agent only proposes and explains.
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && BUILD_IMPL=secrets_app python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_message_args_and_nested_fields (test_build_task.TestNoSecretsInLogs.test_message_args_and_nested_fields)
FAIL: test_seeded_request_mix_leaves_clean_logs (test_build_task.TestNoSecretsInLogs.test_seeded_request_mix_leaves_clean_logs)
Ran 2 tests in 0.032s
FAILED (failures=2)
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 2 tests in 0.002s
OK
```

### [16] 2026-11-03 — `cd labs/L300/16-secrets-handling && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 11 tests in 1.064s
OK
```

## Lesson 17

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python agile_envelope.py` (exit 0)
```
1) sealed 3 docs | header: {'v': 2, 'aead': 'A256GCM', 'kid': 'dk-1'} | ct bytes: 37 | sigs: [('Ed25519', 64), ('ML-DSA-65', 3309)]
2) default -> C20P1305 | opened: 4 of 4
{"metric": "envelopes_by_aead", "A256GCM": 3, "C20P1305": 1}
3) negotiate: A256GCM | only A128CBC offered -> no common active algorithm in ['A128CBC']
4) legacy v1 opens: invoice 0: amount=0 | migrate -> {'v': 2, 'aead': 'C20P1305', 'kid': 'dk-2'}
--- fault: the Ed25519 key leaked; a co-tenant re-signs an edited document with Ed25519 only
legit verify: True | forged doc-4 verify: True | sigs on forged: ['Ed25519']
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python measure_options.py` (exit 0)
```
{"option": "A one algorithm, no id", "header_bytes": 43, "swap_rewrites_before_switch": 1000, "trial_decryptions_per_read": 2.0, "rewrite_all_seconds_est": 0.006}
{"option": "B per-algorithm ids + registry", "header_bytes": 74, "extra_header_bytes_vs_A": 31, "swap_rewrites_before_switch": 0, "old_docs_readable_after_switch": "1000/1000", "dual_signature_bytes": 3373}
{"option": "C suite ids", "ids_needed_for_suites": 6, "ids_needed_per_algorithm": 4, "after_adding_one_aead": 9}
{"per_algorithm": {"A256GCM": {"seal_4KiB_us": 1.5}, "C20P1305": {"seal_4KiB_us": 2.3}, "Ed25519": {"sig_bytes": 64, "sign_us": 34.0, "verify_us": 107.7}, "ML-DSA-65": {"sig_bytes": 3309, "sign_us": 864.3, "verify_us": 195.4}}}
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python try_it.py` (exit 0)
```
1) migrated 5/10, then disallowed A256GCM: 5/10 readable; {'metric': 'envelopes_by_aead', 'A256GCM': 5, 'C20P1305': 5}
2) orders/storage.py:1: imports cryptography.hazmat.primitives.ciphers.aead
2) orders/storage.py:3: names algorithm AESGCM
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python solution_agile.py` (exit 0)
```
phase: transition | required: ['Ed25519', 'ML-DSA-65']
legit verify: True | stripped (Ed25519 only) verify: False
phase: pq-only | legit verify: True | stripped verify: False
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && BUILD_TARGET=mine python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_pq_only_envelope_needs_pq_only_phase (test_build_task.TestPolicyDecidesSignatures.test_pq_only_envelope_needs_pq_only_phase)
FAIL: test_stripped_envelope_rejected_in_transition (test_build_task.TestPolicyDecidesSignatures.test_stripped_envelope_rejected_in_transition)
Ran 4 tests in 0.031s
FAILED (failures=2)
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 4 tests in 0.020s
OK
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 15 tests in 1.607s
OK
```

### [17] 2026-11-03 — `cd labs/L400/17-crypto-agility && python agility_lint.py; echo exit=$?` (exit 0)
```
agility_lint: 0 violation(s)
exit=0
```

## Lesson 18

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python pq_hybrid.py` (exit 0)
```
{"kem": "X25519", "client_share": 32, "server_share": 32, "secret": 32, "on_wire": 64}
{"kem": "ML-KEM-768", "client_share": 1184, "server_share": 1088, "secret": 32, "on_wire": 2272}
{"kem": "ML-KEM-1024", "client_share": 1568, "server_share": 1568, "secret": 32, "on_wire": 3136}
{"kem": "X25519MLKEM768", "client_share": 1216, "server_share": 1120, "secret": 64, "on_wire": 2336}
1) hybrid handshake: client share 1216 B, server share 1120 B, keys match: True, mode: X25519MLKEM768
2) quantum attacker with X25519 broken recovers the key: False
--- fault: an on-path attacker rewrites the server share to its X25519 part only (downgrade)
client accepted a 32-byte server share | mode: X25519 (fallback) | quantum attacker recovers key: True
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python pq_measure.py` (exit 0)
```
{"option": "X25519", "on_wire_bytes": 64, "handshake_us": 144.8, "safe_if_CRQC_exists": false, "safe_if_lattice_break": true}
{"option": "ML-KEM-768", "on_wire_bytes": 2272, "handshake_us": 187.8, "safe_if_CRQC_exists": true, "safe_if_lattice_break": false}
{"option": "X25519MLKEM768", "on_wire_bytes": 2336, "handshake_us": 431.5, "safe_if_CRQC_exists": true, "safe_if_lattice_break": true}
{"signature": "Ed25519", "public_key_bytes": 32, "signature_bytes": 64, "sign_us": 34.4, "verify_us": 314.0}
{"signature": "ML-DSA-44", "public_key_bytes": 1312, "signature_bytes": 2420, "sign_us": 772.9, "verify_us": 131.5}
{"signature": "ML-DSA-65", "public_key_bytes": 1952, "signature_bytes": 3309, "sign_us": 1156.0, "verify_us": 202.3}
{"signature": "ML-DSA-87", "public_key_bytes": 2592, "signature_bytes": 4627, "sign_us": 1465.5, "verify_us": 323.3}
{"hpke": "MLKEM768_X25519 (X-Wing)", "enc_bytes": 1120, "wrapped_32B_key_bytes": 1168, "classic_X25519_enc_bytes": 32, "seal_us": 141.5}
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python try_it.py` (exit 0)
```
1) SecP384r1MLKEM1024: client share 1665 B, server share 1665 B, on wire 3330 B (X25519MLKEM768: 2336 B)
2) root+leaf certificates + CertificateVerify: Ed25519 478 B, ML-DSA-65 14106 B (30x)
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python solution_strict.py` (exit 0)
```
normal: X25519MLKEM768 | keys match: True
{"event": "handshake_abort", "alert": "illegal_parameter", "share_bytes": 32}
downgraded 32-byte share: refused (illegal_parameter: X25519MLKEM768 server share must be 1120 bytes, got 32)
{"event": "handshake_abort", "alert": "illegal_parameter", "share_bytes": 33}
downgraded 33-byte share: refused (illegal_parameter: X25519MLKEM768 server share must be 1120 bytes, got 33)
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && BUILD_TARGET=mine python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_downgraded_share_is_refused (test_build_task.TestNoSilentFallback.test_downgraded_share_is_refused)
FAIL: test_one_extra_byte_is_refused (test_build_task.TestNoSilentFallback.test_one_extra_byte_is_refused)
Ran 3 tests in 0.084s
FAILED (failures=2)
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 3 tests in 0.058s
OK
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python -m unittest -v 2>&1 | grep -E 'skip|^Ran|^OK|FAILED'` (exit 0)
```
test_liboqs_interop (test_pending_ci.TestPendingCI.test_liboqs_interop) ... skipped 'liboqs-python not installed (CI ubuntu job installs it)'
test_probe_reports_why_it_skips (test_pending_ci.TestPendingCI.test_probe_reports_why_it_skips) ... ok
test_tls_negotiates_hybrid_group (test_pending_ci.TestPendingCI.test_tls_negotiates_hybrid_group) ... skipped 'needs Python 3.15+ and OpenSSL 3.5+ (have 3.12.15, OpenSSL 3.3.7 7 Apr 2026)'
Ran 15 tests in 0.011s
OK (skipped=2)
```

### [18] 2026-11-03 — `cd labs/L400/18-post-quantum && python oqs_crosscheck.py; python pq_tls_probe.py` (exit 0)
```
liboqs-python not installed: skipped (CI ubuntu job installs liboqs-python==0.16.0.1)
skipped: needs Python 3.15+ with OpenSSL 3.5+ (have Python 3.12.15, OpenSSL 3.3.7 7 Apr 2026)
```

## Lesson 19

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python soft_token.py` (exit 0)
```
1) wrong PIN: CKR_PIN_INCORRECT
2) signed via handle 1 | sig bytes: 64 | public key DER bytes: 44
--- fault: a compromised app asks the token for the private key
attributes: {'CKA_SENSITIVE': False, 'CKA_VALUE': 48, 'CKA_EXTRACTABLE': True}
after logout the stolen key still signs offline: True | audit events: 6
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python key_storage_options.py` (exit 0)
```
{"option": "file key", "app_can_read_key": true, "sign_us": 34.4, "attacker_signs_after_cleanup": true}
{"option": "KMS-style remote signing (HTTP, 127.0.0.1)", "app_can_read_key": false, "sign_us": 587.5, "attacker_signs_after_cleanup": false}
{"option": "token handle (PKCS#11-shaped, non-exportable)", "app_can_read_key": false, "sign_us": 40.3, "attacker_signs_after_cleanup": false}
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python ceremony.py` (exit 0)
```
{"step": 1, "do": "SO initialises token, sets USER PIN (out of band)", "by": "SO", "seen_by": ["witness-b", "witness-c"]}
{"step": 2, "do": "generate release-signing-2026 in token (CKM_EDDSA, non-exportable)", "by": "custodian-a", "seen_by": ["witness-b", "witness-c"]}
{"step": 3, "do": "export PUBLIC key and read fingerprint aloud", "sha256": "488b44540607e1cb3a4ce429a8ded55666e801db3a00b14178e1cfd3c294c2a1", "seen_by": ["witness-b", "witness-c"]}
transcript verifies: True
edited transcript verifies: False
custodian as own witness: need 2 distinct witnesses who are not the custodian
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python try_it.py` (exit 0)
```
1) logins: ['CKR_PIN_INCORRECT', 'CKR_PIN_INCORRECT', 'CKR_PIN_INCORRECT', 'CKR_PIN_LOCKED']
2) sign via handle 39.7 us vs raw key 33.9 us (overhead 1.17x, plus one audit event per call: 502 events)
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python solution_nonexportable.py` (exit 0)
```
attributes: {'CKA_SENSITIVE': True, 'CKA_EXTRACTABLE': False, 'CKA_ALWAYS_SENSITIVE': True, 'CKA_NEVER_EXTRACTABLE': True}
read CKA_VALUE: CKR_ATTRIBUTE_SENSITIVE
wrap (export) the key: CKR_KEY_UNEXTRACTABLE
flip CKA_EXTRACTABLE back on: CKR_ATTRIBUTE_READ_ONLY
template asking extractable: CKR_TEMPLATE_INCONSISTENT
signing via handle still works: 64 byte signature
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && BUILD_TARGET=mine python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_attributes_prove_lifetime_protection (test_build_task.TestNonExportableByDefault.test_attributes_prove_lifetime_protection)
FAIL: test_key_cannot_be_wrapped_out (test_build_task.TestNonExportableByDefault.test_key_cannot_be_wrapped_out)
FAIL: test_private_value_cannot_be_read (test_build_task.TestNonExportableByDefault.test_private_value_cannot_be_read)
FAIL: test_template_cannot_opt_out (test_build_task.TestNonExportableByDefault.test_template_cannot_opt_out)
Ran 4 tests in 0.013s
FAILED (failures=4)
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 4 tests in 0.002s
OK
```

### [19] 2026-11-03 — `cd labs/L400/19-hsm-pkcs11 && python -m unittest -v 2>&1 | grep -E 'skip|^Ran|^OK|FAILED'` (exit 0)
```
test_non_exportable_key_signs_via_handle (test_pending_ci.TestSoftHSM.test_non_exportable_key_signs_via_handle) ... skipped 'PKCS11_MODULE not set (CI ubuntu job: softhsm2 + python-pkcs11)'
Ran 14 tests in 0.034s
OK (skipped=1)
```

## Lesson 20

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python group_keys.py` (exit 0)
```
1) group of 8 | epoch 0 | alice -> all: kick-off at 10
2) carol updates her path: HPKE encryptions: 3 | epoch 1 | all in sync: True
--- fault: frank removes dave; the removed leaf's parent keys are not blanked
commit HPKE encryptions: 3 | epoch 2 | can read post-removal message: {'alice': True, 'bob': True, 'carol': True, 'dave': True, 'erin': True, 'frank': True, 'grace': True, 'heidi': True}
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python compare_designs.py` (exit 0)
```
{"design": "pairwise", "n": 8, "encryptions_per_message": 7, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": true}
{"design": "sender keys", "n": 8, "encryptions_per_message": 1, "encryptions_per_removal": 42, "bytes_per_removal": 3360, "real_crypto": true}
{"design": "MLS-style tree (toy)", "n": 8, "encryptions_per_message": 1, "encryptions_per_removal": 4, "bytes_per_removal": 320, "removed_can_read": false, "commit_and_process_ms": 1.6, "real_crypto": true}
{"design": "pairwise", "n": 64, "encryptions_per_message": 63, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": true}
{"design": "sender keys", "n": 64, "encryptions_per_message": 1, "encryptions_per_removal": 3906, "bytes_per_removal": 312480, "real_crypto": true}
{"design": "MLS-style tree (toy)", "n": 64, "encryptions_per_message": 1, "encryptions_per_removal": 10, "bytes_per_removal": 800, "removed_can_read": false, "commit_and_process_ms": 17.3, "real_crypto": true}
{"design": "pairwise", "n": 256, "encryptions_per_message": 255, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": false}
{"design": "sender keys", "n": 256, "encryptions_per_message": 1, "encryptions_per_removal": 64770, "bytes_per_removal": 5181600, "real_crypto": false}
{"design": "MLS-style tree (toy)", "n": 256, "encryptions_per_message": 1, "encryptions_per_removal": 14, "bytes_per_removal": 1120, "removed_can_read": false, "commit_and_process_ms": 86.0, "real_crypto": true}
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python try_it.py` (exit 0)
```
1) attacker with carol's stolen state reads: before update True, after carol's update False
2) unfixed remove leaks in 48 of 56 pairs; safe only when the committer is the removed member's sibling: [('alice', 'bob'), ('bob', 'alice'), ('carol', 'dave'), ('dave', 'carol')] ...
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python solution_remove.py` (exit 0)
```
frank removes dave: commit HPKE encryptions 4 | can read post-removal message: {'alice': True, 'bob': True, 'carol': True, 'dave': False, 'erin': True, 'frank': True, 'grace': True, 'heidi': True}
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && BUILD_TARGET=mine python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_every_committer_removed_pair (test_build_task.TestRemovalExcludes.test_every_committer_removed_pair)
FAIL: test_seeded_removal_from_the_lab (test_build_task.TestRemovalExcludes.test_seeded_removal_from_the_lab)
Ran 2 tests in 0.244s
FAILED (failures=2)
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 2 tests in 0.285s
OK
```

### [20] 2026-11-03 — `cd labs/L400/20-group-e2ee && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 9 tests in 0.302s
OK
```

## Lesson 21

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python threat_model.py` (exit 0)
```
1) elements 11 (flows 5, crossing a boundary 4) | STRIDE-per-element candidates 41 | threats 18 | controls 12
2) checker problems: [] | controls whose tests exist: 12/12
3) cheapest open attack path: cost 9 via ['phish an authorised user']
--- fault: model drift (a test is deleted in a refactor; a SIEM export flow is added)
control C-NO-FALLBACK now points at a missing test: True | checker problems: [] | new flow app-log->siem threats: []
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python agent_assist.py` (exit 0)
```
doc-api->envelope-db T (an attacker swaps a stored envelope for ) -> CONFIRMED - C-DUAL-SIG proven by TestPolicyDecidesSignatures::test_stripped_envelope_rejected_in_transition
app-log I (bearer tokens end up in the application ) -> CONFIRMED - C-REDACT proven by TestNoSecretsInLogs::test_seeded_request_mix_leaves_clean_logs
signer R (nobody can prove which operator signed a) -> GAP - valid threat with no control: triage it (not added automatically)
client->doc-api E (privilege escalation over the wire) -> REJECTED - E does not apply to a flow
blockchain-ledger T (the ledger is rewritten) -> REJECTED - unknown element
envelope-db I (database backups are readable by the bac) -> REJECTED - control C-QUANTUM-SHIELD does not exist
verdicts {'CONFIRMED': 2, 'GAP': 1, 'REJECTED': 3}; the model only proposes - the checker decides, and nothing is merged automatically.
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python try_it.py` (exit 0)
```
1) without T3: ['client->doc-api: boundary-crossing flow lacks T']
2) C-NONEXPORT unverified -> cheapest path cost 6 via ['compromise the app host', 'read key bytes out of the token'] (was 9 via ['phish an authorised user'])
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python solution_verified.py` (exit 0)
```
clean model problems: [] | verified controls: 12 of 12
after drift:
  - C-NO-FALLBACK: test missing labs/L400/18-post-quantum/test_build_task.py::TestNoSilentFallback::test_removed_in_refactor
  - siem: no threats modelled
  - app-log->siem: no threats modelled
  - app-log->siem: boundary-crossing flow lacks T
  - app-log->siem: boundary-crossing flow lacks I
cheapest open attack path with only VERIFIED controls: cost 8 via ['record traffic on path', 'client accepts classical-only share', 'wait for a quantum computer']
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && BUILD_TARGET=mine python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```
FAIL: test_deleted_test_is_reported (test_build_task.TestModelDriftIsCaught.test_deleted_test_is_reported)
FAIL: test_unmodelled_boundary_flow_is_reported (test_build_task.TestModelDriftIsCaught.test_unmodelled_boundary_flow_is_reported)
FAIL: test_unverified_control_does_not_close_the_attack_tree (test_build_task.TestModelDriftIsCaught.test_unverified_control_does_not_close_the_attack_tree)
Ran 4 tests in 0.022s
FAILED (failures=3)
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python -m unittest -v test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```
Ran 4 tests in 0.109s
OK
```

### [21] 2026-11-03 — `cd labs/L400/21-threat-model && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 14 tests in 29.833s
OK
```

## Lesson 22

### [22] 2026-11-03 — `cd labs/L400/22-capstone && python run_capstone.py` (exit 0)
```
{"milestone": "M1 envelope + versioned KEK + rotation", "crash_after": 3, "records_by_kid_after_crash": {"docs-kek:v1": 3, "docs-kek:v2": 3}, "retire_refused_while_in_use": true, "resumed": 3, "retired": "docs-kek:v1", "readable": "6/6", "pass": true}
{"milestone": "M2 mTLS between doc service and KMS", "doc_service_client": "ok", "no client cert": "refused (SSLEOFError)", "cert from another CA": "refused (SSLEOFError)", "pass": true}
{"milestone": "M3 signed, hash-chained audit log", "entries": 50, "clean_log_anomalies": ["access_after_revoke", "unwrap_burst"], "tampered_at_seq": 10, "tampered_log_findings": ["access_after_revoke", "bad_signature", "chain_break", "seq_gap", "unwrap_burst"], "pass": true}
{"milestone": "M4 PQ-hybrid sharing (HPKE)", "kem": "HPKE-XWING", "pq": true, "recipient_opened": true, "wrapped_dek_bytes": 1168, "new_share_with_HPKE-X25519": "refused", "pass": true}
{"milestone": "M5 fitness functions + threat model + secret handling", "agility_lint_violations": 0, "key_export_calls": 0, "token_keys_exportable": 0, "threat_model_problems": 0, "secrets_in_logs": 0, "pass": true}
{"milestone": "M6 agent explains, code decides", "anomalies": 7, "accepted": 7, "rejected": ["A99"], "action": "page on-call (integrity)", "pass": true}
{"scorecard": "capstone", "passed": 6, "total": 6, "decided_by": "code"}
```

### [22] 2026-11-03 — `cd labs/L400/22-capstone && python agent_explain.py` (exit 0)
```
{'id': 'A1', 'verdict': 'ACCEPTED', 'text': 'rule unwrap_burst fired; check who triggered it and whether it was expected.'}
{'id': 'A99', 'verdict': 'REJECTED (no such anomaly)', 'text': 'entry 3 also looks suspicious to me.'}
```

### [22] 2026-11-03 — `cd labs/L400/22-capstone && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 19 tests in 30.858s
OK
```

## Lesson 23

### [23] 2026-11-03 — `cd labs/L500/23-number-theory && python theorem_checks.py` (exit 0)
```
[T23.1] Bezout / extended Euclid
a*x + b*y = gcd(a, b) = math.gcd(a, b): 5000/5000 random 256-bit pairs
inverse exists exactly when gcd = 1 (and a*inv = 1 mod b): 5000/5000
egcd(240, 46) = (2, -9, 47) | modinv(17, 3120) = 2753
[T23.2] Euler's theorem a^phi(n) = 1 (mod n) when gcd(a, n) = 1
exhaustive n = 2..400: 48677/48677 coprime pairs satisfy it
Fermat a^(p-1) = 1 (mod p), 303 primes < 2000, bases 2,3,5,7: 1208/1208
phi(3233) = 3120 = (61-1)*(53-1) = 3120; 2^560 mod 561 = 1 (561 is composite)
[T23.3] Chinese remainder theorem
x -> (x mod 3, x mod 5, x mod 7) on 0..104: 105 distinct images (bijection onto 3*5*7 = 105)
crt() reconstructs x: 105/105 | crt([2, 3, 2], [3, 5, 7]) = 23
pyca 2048-bit key: CRT decryption = plain decryption = m for 20/20 random m
pyca CRT parameters match ours: dmp1 = True | dmq1 = True | iqmp = True
[T23.4] RSA correctness m^(e*d) = m (mod n) for every m in Z_n
n = 3233 (61*53), e = 17, d = 2753: 3233/3233 messages round-trip, incl. 113 with gcd(m, n) > 1
pyca 2048-bit key (e = 65537): 45/45 round-trip (40 random + p, 5q, 0, 1, n-1)
pyca d satisfies e*d = 1 mod lcm(p-1, q-1): True
[D23] textbook RSA malleability and textbook DH (insecure toys)
Enc(65) = 2790; attacker sends c * 2^e mod n = 3017; Dec = 130 (= 2 * 65)
Enc(6) * Enc(7) mod n decrypts to 42 (= 6 * 7)
DH p=23 g=5 a=6 b=15: A = 8, B = 19, B^a = 2, A^b = 2
pyca FFDH exchange == our pow(Y, x, p): True | pyca 50.0.2 warns FFDH deprecated: True
```

### [23] 2026-11-03 — `cd labs/L500/23-number-theory && python nt_toys.py` (exit 0)
```
1) egcd(240, 46) = (2, -9, 47) | modinv(17, 3120) = 2753
2) crt([2, 3, 2], [3, 5, 7]) = 23
3) textbook RSA round trip: True | CRT decrypt agrees: True
   deterministic (same m -> same c): True
4) malleability: Dec(c * 2^e) == 2*m: True
5) toy DH (p=23, g=5) both sides agree: True
INSECURE LEARNING TOYS - use RSA-OAEP/PSS, X25519+HKDF or ML-KEM from pyca/cryptography in real code
```

### [23] 2026-11-03 — `cd labs/L500/23-number-theory && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 8 tests in 0.305s
OK
```

## Lesson 24

### [24] 2026-11-03 — `cd labs/L500/24-probability && python theorem_checks.py` (exit 0)
```
[T24.1] Union bound P[collision] <= q(q-1)/(2N)
exact <= bound in 20/20 (N, q) cases; N = 365, q = 23: exact 0.507297, bound 0.693151
96-bit nonces, q = 2^32: bound = 2^-33.00
[T24.2] Lower bound P >= 1 - exp(-q(q-1)/(2N)) and the 50 % threshold q ~ 1.1774 sqrt(N)
lower <= exact in 20/20 cases
N = 365: first q with P >= 1/2 is 23 (formula 22.49)
N = 2^32: first q with P >= 1/2 is 77164 (formula 77163)
simulation N = 2^24, q = 4096, 2000 trials: observed 0.400, predicted 0.393
[T24.3] Nonce budget for 96-bit random nonces under one key
P[collision] after 2^32 messages = 1.1642e-10 = 2^-33.00
messages for risk 2^-32 = 6.0740e+09 = 2^32.50; risk 1/2 at 2^48.24
collisions among 2^20 os.urandom(12) nonces: 0 | pyca AES-GCM: 96-bit nonce, 16-byte tag
[T24.4] H_min <= H <= log2|X| (equality iff uniform); poly * negligible is negligible
random distributions satisfying both inequalities: 1000/1000
uniform 2^128: H = H_min = 128 bits | PIN with P('1234') = 0.1: H = 12.43, H_min = 3.32 bits
n^10 * 2^-n < n^-3 for every n >= 83 (checked to 5000); 1/n^3 is not negligible (n^4 * n^-3 = n grows)
2^40 queries, 2^-128 per query: union bound 2^-88
```

### [24] 2026-11-03 — `cd labs/L500/24-probability && python prob_tools.py` (exit 0)
```
96-bit random nonces, q = 2^28: P[collision] = 4.547e-13 (~2^-41.0)
96-bit random nonces, q = 2^32: P[collision] = 1.164e-10 (~2^-33.0)
96-bit random nonces, q = 2^40: P[collision] = 7.629e-06 (~2^-17.0)
96-bit random nonces, q = 2^48: P[collision] = 3.935e-01 (~2^-1.3)
messages per key for risk 2^-32: 6.074e+09 (~2^32.50)
at 1,000,000 messages/s one key reaches 2^32 messages in 71.6 minutes
4-digit PIN where '1234' has 10%: Shannon 12.43 bits, min-entropy 3.32 bits
```

### [24] 2026-11-03 — `cd labs/L500/24-probability && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 6 tests in 0.721s
OK
```

### [24] 2026-11-03 — `cd labs/L500/24-probability && python -c "import math; q=2**32/10000; print('24-P4 seconds =', round(q,1), 'days =', round(q/86400,2)); o=0.9/9999; H=0.1*math.log2(10)+0.9*math.log2(1/o); print('24-P6 H =', round(H,3), 'H_min =', round(-math.log2(0.1),3))"` (exit 0)
```
24-P4 seconds = 429496.7 days = 4.97
24-P6 H = 12.428 H_min = 3.322
```

## Lesson 25

### [25] 2026-11-03 — `cd labs/L500/25-security-definitions && python theorem_checks.py` (exit 0)
```
[T25.1] One-time pad: Pr[M = m | C = c] = Pr[M = m]; perfect secrecy needs |K| >= |M|
3-bit OTP, non-uniform prior: posterior = prior for 64/64 (m, c) pairs
2-bit key on 3-bit messages: 32 of 32 possible (m, c) pairs have posterior != prior; e.g. Pr[M=7 | C=7] = 4/13 vs prior 2/9
pad reused: c1 XOR c2 == m1 XOR m2: True
[T25.2] Deterministic (or nonce-reusing) encryption has IND-CPA advantage 1
  AES-ECB (deterministic)      advantage 1.000 (1000 games)
  AES-GCM fixed nonce          advantage 1.000 (1000 games)
  Encrypt-and-MAC (tag on m)   advantage 1.000 (1000 games)
  AES-GCM random nonce         advantage 0.000 (1000 games)
  Encrypt-then-MAC             advantage 0.000 (1000 games)
[T25.3] Encrypt-then-MAC: Adv_INT-CTXT(A) <= Adv_EUF-CMA(B), and IND-CPA + INT-CTXT => IND-CCA
1-byte tags, 2560 trials: A forges EtM 12 times, B (running A) forges the MAC 12 times; equal: True; expected about 2560/256 = 10
  IND-CCA bit-flip adversary vs AES-CTR (no MAC)   advantage 1.000
  IND-CCA bit-flip adversary vs AES-GCM            advantage 0.002
  IND-CCA bit-flip adversary vs Encrypt-then-MAC   advantage 0.015
[T25.4] Hardness: BSGS solves discrete log in O(sqrt(q)); LWE without error is linear algebra
  q ~ 2^16: recovered x: True, group ops 368 <= 2*ceil(sqrt(q)) = 446: True
  q ~ 2^20: recovered x: True, group ops 1560 <= 2*ceil(sqrt(q)) = 1786: True
  q ~ 2^24: recovered x: True, group ops 4461 <= 2*ceil(sqrt(q)) = 6688: True
  q ~ 2^28: recovered x: True, group ops 17007 <= 2*ceil(sqrt(q)) = 30720: True
  q = 3329, n = 16: error 0 -> elimination recovers s: True; error in [-2, 2] -> recovers s: False
  toy Regev, m = 32 samples: decryption errors 0/1000 bits with |e| <= 2, 122/1000 with |e| <= 300 (threshold q/4 = 832)
  pyca ML-KEM-768: encapsulation key 1184 B, ciphertext 1088 B, shared secret 32 B, decapsulates: True
[D25] EUF-CMA: textbook RSA signatures vs RSA-PSS
textbook RSA n = 3233: no-message forgeries accepted 100/100, multiplicative (2 oracle queries) 100/100
pyca RSA-PSS 2048: product of two signatures accepted: False
```

### [25] 2026-11-03 — `cd labs/L500/25-security-definitions && python games.py` (exit 0)
```
IND-CPA advantage (equality adversary, 400 games):
  AES-ECB (deterministic)    1.000
  AES-GCM random nonce       0.000
  AES-GCM fixed nonce        1.000
  Encrypt-and-MAC            1.000
  Encrypt-then-MAC           0.000
IND-CCA advantage (bit-flip + decryption oracle, 400 games):
  AES-CTR (no MAC)           1.000
  AES-GCM                    0.005
  Encrypt-then-MAC           0.005
EUF-CMA textbook RSA (n = 3233): no-message forgeries accepted 100/100, multiplicative 99/100; Ed25519 random signatures accepted 0/100
```

### [25] 2026-11-03 — `cd labs/L500/25-security-definitions && python -m unittest 2>&1 | grep -E '^(Ran|OK|FAILED)'` (exit 0)
```
Ran 7 tests in 0.097s
OK
```

### [25] 2026-11-03 — `cd labs/L500/25-security-definitions && python -c "m1=b'attack at dawn'; x=bytes.fromhex('051112040d0f00151c454406161e'); print('25-P2 m2 =', bytes(a^b for a,b in zip(m1,x))); s=pow(6,2753,3233)*pow(7,2753,3233)%3233; print('25-P6 m(100) =', pow(100,17,3233), '| sigma6 =', pow(6,2753,3233), 'sigma7 =', pow(7,2753,3233), 'sigma42 =', s, '| sigma42^17 mod n =', pow(s,17,3233))"` (exit 0)
```
25-P2 m2 = b'defend the gap'
25-P6 m(100) = 1773 | sigma6 = 2902 sigma7 = 2667 sigma42 = 3065 | sigma42^17 mod n = 42
```

## Lesson 26
No lab run (no lab for this lesson); quoted numbers come from the lesson 24/25 runs above.

## Lesson 27

### [27] 2026-11-03 — `cd labs/L500/23-number-theory && python -c "import math; print('27-P2 2^100 =', '%.3e' % 2**100, '| log2(2^100/400) =', round(100-math.log2(400),2)); h=math.log10(math.factorial(26)); print('27-P3 log10(26!) =', round(h,2), '| unicity distance H/0.7 =', round(h/0.7,1), 'letters')"` (exit 0)
```
27-P2 2^100 = 1.268e+30 | log2(2^100/400) = 91.36
27-P3 log10(26!) = 26.61 | unicity distance H/0.7 = 38.0 letters
```
