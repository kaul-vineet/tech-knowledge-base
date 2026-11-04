# ADR-0022-1: The KEK lives in a separate KMS component reached only over mutual TLS

## Status
Accepted (2026-10-28, capstone). In production, the KMS is OpenBao transit (`exportable=false`) or an HSM-backed `external-key`. Neither is run here; that is pending CI.

## Context
Documents are encrypted with per-document data keys (DEKs). Whoever holds the key-encryption key (KEK) can read every
document. The document service runs on an application host that is the most likely thing to be compromised. Measured in M2:
a client without a certificate and a client with a certificate from another CA were both refused (`SSLEOFError`); the
document service's own client worked.

## Decision
1. The KMS (`kms.py`) holds the versioned KEK keyring from lesson 12. It exposes only wrap, unwrap, rewrap, rotate and retire. Rewrap never returns a DEK to the caller.
2. Transport is TLS 1.2+ with `CERT_REQUIRED` and the lab CA (lesson 10 build task). The KMS takes the caller's identity from the verified certificate CN, combined with the user on whose behalf the call is made. Each call writes an audit entry.
3. Retirement is decided by the KMS from the caller's `records_by_kid` (retire-after-rewrap, lesson 12). The primary version can never be retired.
4. User-facing TLS, which terminates at the edge, is out of scope (threat T3, accepted). Edge key exchange follows ADR-0018.

## Consequences
- A compromised document-service host can still ask the KMS to unwrap: misuse continues while the attacker is present. The audit rules (unwrap burst) are the detective control. Stealing the KEK, however, needs a KMS compromise.
- Every read costs one mTLS round trip. In this lab a new connection per call made the run noticeably slower; production clients reuse connections or cache DEKs briefly, which trades exposure for latency.
- In the lab, the KMS keeps KEKs in process memory (threat T7, accepted). The boundary is real only with OpenBao or an HSM.
