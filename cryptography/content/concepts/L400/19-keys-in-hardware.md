## Why it matters
Your release-signing key signs every artifact customers install. If it is a PEM file on a build host, an intruder who reads it once can sign malware forever: rotating the build host does not help, and you may never learn the key was copied. HSMs, smart cards and KMSs change the question from "who has the key?" to "who can ask it to sign?": theft becomes misuse, bounded in time and visible in logs. PKCS#11 (OASIS v3.1, 2023) is the common interface to such devices; SoftHSM2 implements it in software.

## Mental model
A **bank vault with a teller window**. You never enter the vault; you pass a request through the window together with a ticket number (the object **handle**), and the teller signs inside. Two attributes decide whether the key can ever come out: `CKA_SENSITIVE` (never revealed in plaintext) and `CKA_EXTRACTABLE` (never wrapped out). Both are one-way switches, and the token records the history in `CKA_ALWAYS_SENSITIVE` and `CKA_NEVER_EXTRACTABLE`.

```
app ── C_Login(PIN) ── C_FindObjects("release-signing") → handle 1
app ── C_Sign(handle 1, CKM_EDDSA, data) ──────────────→ signature
app ── C_GetAttributeValue(handle 1, CKA_VALUE) ───────→ CKR_ATTRIBUTE_SENSITIVE
```

## Design space
- **File key** (PEM, encrypted or not). Zero infrastructure and the fastest, but any process that can read it, and any backup, owns it forever.
- **KMS-style remote signing** (OpenBao transit with `exportable=false`, a cloud KMS). The key lives in a service: you get a network call per operation, central policy, audit and instant disable.
- **HSM or token through PKCS#11.** The key is generated and used inside a hardware boundary and the app holds handles. Latency is local, but you take on device management, PIN handling and backup ceremonies. OpenBao's `external-key` lets a KMS front an HSM.
- **Key ceremony.** How a long-term key is born: generated inside the device, under dual control, with witnesses, ending with a published fingerprint and a proof of possession.

## How to decide
Criteria: can the application process read key bytes, can an attacker keep signing after clean-up, signing latency and throughput, recovery when the device is lost, and audit.

Evidence from `key_storage_options.py`, a simulated compromise followed by clean-up (→ see lab step 3):

| Option | App can read key | Sign latency | Attacker signs after clean-up |
|---|---|---|---|
| File key | yes | ≈35 µs | **yes** |
| KMS-style remote signing (HTTP, 127.0.0.1) | no | ≈5.0 ms (new connection per call) | no: key disabled |
| Token handle | no | ≈40 µs, ≈1.2× a raw key (tryIt 2) | no |

While the attacker controls the host, all three let them sign. Only the file key also lets them sign *afterwards*.

Worked example from one lab run (→ see lab steps 1, 2 and 4). A wrong PIN returns `CKR_PIN_INCORRECT`; three in a row lock the token (`CKR_PIN_LOCKED`, tryIt 1). The app generates `release-signing` relying on the token's defaults and signs through handle 1.

Then the fault. A compromised app asks for the attributes and gets `CKA_SENSITIVE: False`, `CKA_EXTRACTABLE: True` and 48 bytes of PKCS#8 key. After logout the stolen key still signs offline: `True`. The fix moves the decision into the token: private keys are always created sensitive and non-extractable, a template asking otherwise fails with `CKR_TEMPLATE_INCONSISTENT`, reads fail with `CKR_ATTRIBUTE_SENSITIVE`, and wrapping fails with `CKR_KEY_UNEXTRACTABLE`. The ceremony script (`ceremony.py`) produces a transcript signed by the new key; editing one witness list afterwards makes verification fail.

## Failure modes at scale
- **Defaults decide.** PKCS#11 leaves `CKA_SENSITIVE` and `CKA_EXTRACTABLE` defaults to the token. Code that omits them is portable in the worst way. Audit the inventory (`ALWAYS_SENSITIVE` and `NEVER_EXTRACTABLE` must be true), as the fitness test does.
- **A signing oracle.** Non-exportable keys still sign for whoever holds a session. Alert on unusual signing volume or new callers (the capstone audit rules), and keep PINs out of environment variables and logs.
- **Lost hardware.** "Non-exportable" means no software backup. Provision a second device in the same ceremony, or use the HSM vendor's wrapped backup, and rehearse the recovery.
- **Throughput.** Remote calls add milliseconds: batch or keep connections open, never cache the key.

## Common mistakes
- Generating the key on a laptop and importing it "into the HSM". It was exposed before it got there, and `NEVER_EXTRACTABLE` will be false.
- Letting the security officer (SO) role also use keys. Separate administration from use.
- Treating a software token as protection. It teaches the interface; the boundary comes from hardware (SoftHSM2 run pending CI).
