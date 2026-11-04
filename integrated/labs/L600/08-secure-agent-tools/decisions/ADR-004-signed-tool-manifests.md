# ADR-004: Tools load only from Ed25519-signed manifests that pin the implementation digest and the definition

## Status
Accepted (2026-10-30). Fitness: M1 (`tests/test_m1_signed_tools.py`); seam `tests/test_seam_manifest_loader.py`.

## Context
The policy trusts manifest facts (sideEffect, risk, x-provenance, x-sensitive). If a tool's code or manifest can
change after review, a 'read-only' label or a softer risk would silently bypass the policy; MCP's spec says clients
must treat tool annotations as untrusted unless they come from trusted servers. A server can also change a tool
description after review (tool poisoning).

## Decision
A publisher signs canonical JSON (sorted keys, no spaces) of each manifest with Ed25519 (RFC 8032), including the
SHA-256 of the implementation file (cryptography L300 #14's digest/key_id). The loader checks signer kid in the
keyring, the signature over the exact bytes, then the digest of the file it is about to import; a failing tool is
excluded, the others still load. When tools are served over MCP, the host compares tools/list (name, description,
inputSchema) to the signed manifests and refuses any drift.

## Consequences
- Modified implementation, edited manifest and unsigned manifest: each rejected (1/1); a poisoned description refused.
- Publishing a tool is now a signing step; key rotation = add the new kid to the keyring, later remove the old one.
- The demo uses a seeded key for reproducible output - a real publisher key is random and kept offline.
