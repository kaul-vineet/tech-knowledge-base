# ADR-0022-3: The audit log is hash-chained and signed through a token handle; rules decide anomalies, an agent only explains

## Status
Accepted (2026-10-28, capstone).

## Context
Insiders and intruders try to hide access by editing or deleting log lines. Detecting misuse such as bulk reads or reads
after revocation must not depend on a model's judgement. Measured in M3: a 50-entry log. On the clean log the rules
report exactly `access_after_revoke` and `unwrap_burst`. A copy with one edited entry (seq 10) and one deleted entry adds
`bad_signature`, `chain_break` and `seq_gap`. In M6 the fake model explained all 7 anomalies and invented one (A99), which the code rejected.

## Decision
1. Format `audit-v1`: each entry holds seq, timestamp, actor, operation, object and `prev` (the SHA-256 of the previous entry). The SHA-256 of the entry is signed with the token's `audit-log` key (Ed25519, non-exportable).
2. Verification reports, at the point of failure, a bad signature, a chain break, or a sequence gap or reordering.
3. Behaviour rules are code: more than 5 unwraps per user within 60 s, a successful read after revocation, and a timestamp going backwards. The ACL cache (300 s) is a known weakness that the audit rules detect.
4. `agent_explain.py` sends only anomaly lines, after lesson 16's scanner and lesson 9's secret gate. Explanations for anomaly ids that the rules did not report are rejected. The action (page on-call for integrity findings, otherwise a ticket) is decided by code.
5. Flooding and log shipping are out of scope (T27, accepted).

## Consequences
- Truncating the end of the log is not detected by the chain alone. Ship entries off-host promptly, or anchor the latest hash in a second system.
- The hash function is fixed by the format version. A change means `audit-v2`, and verifiers must keep reading v1.
- Rules give false positives (a legitimate bulk export). The agent's explanation helps triage, but it cannot close an alert.
