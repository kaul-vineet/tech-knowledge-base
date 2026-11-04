# 1. Hash and sign RFC 8785 (JCS) bytes, and treat release objects as opaque bytes everywhere

## Status
Accepted (2026-10-30)

## Context
The catalogue is JSON full of doubles (distance_pc = 1/parallax, absolute magnitudes). Every party that touches it has
its own JSON stack: the Python builder, mirrors that "normalise" uploads through a document store or REST layer, and
verifiers in other languages. A SHA-256 or a signature covers bytes, not values. In the failure lab mirror m2
re-serialises with `'%.17g'` doubles (Python's repr before 3.1; still common in printf-based writers):
`-3.94153` becomes `-3.9415300000000002`. The value is identical, the bytes are not, so:
- m2's catalogue hash no longer matches the signed manifest (client: `v4: catalogue.json missing or changed`);
- anti-entropy sees the same key with different digests and never converges (`rounds: null` for v1-v4).

Options measured on release v4 (6,536-byte catalogue):
- A, Python `json.dumps(sort_keys=True, separators=(',', ':'))`: deterministic in one runtime, but `5.0` vs
  ECMAScript `5`; mirrors still diverge (tryIt 1).
- B, RFC 8785 JCS: ECMAScript number layout, UTF-16 key order, no whitespace. Passes the RFC's Appendix B samples
  and the section 3.2.4 bytes; `dumps(loads(x)) == x` for every release (idempotent), so a re-serialising mirror
  is harmless.
- C, never parse: sign opaque bytes only (JWS-style base64). Robust, but the release is no longer readable JSON and
  every intermediate must promise not to touch it.

## Decision
B, plus C's discipline: the builder emits JCS; manifests, timestamps and log entries are JCS; mirrors store bytes
verbatim (re-encoding with JCS is tolerated because it is idempotent); the client parses with `loads_strict`, which
rejects any bytes that are not the JCS form of their own content (so `E+30` for `e+30` is refused, not "equivalent").
Integers above 2^53, NaN and Infinity are errors - send them as strings (RFC 8785 Appendix D).

## Consequences
- Fitness F1 holds: 15,586 / 15,586 single-bit flips across the v4 objects are rejected.
- The number formatter is the risky part (build task). Python's `repr` gives the shortest digits; only the layout
  changes. Tests use the RFC's own vectors, not our outputs.
- JCS is an Informational RFC, not a standard; other canonical forms exist (canonicaljson-spec, TUF's OLPC
  canonical JSON, which forbids floats). Pin the scheme by name in the manifest if you federate.
- Catalogue size grows when a stack writes 17 digits (7,901 vs 6,536 bytes) - a cheap smell test in CI.
