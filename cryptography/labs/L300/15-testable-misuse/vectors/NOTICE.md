# Vendored test vectors

`aes_gcm_subset.json` and `ed25519_subset.json` contain a few test cases from **Project Wycheproof**
(https://github.com/C2SP/wycheproof), Copyright 2016-2026 The Wycheproof Authors, licensed under the
Apache License, Version 2.0 (full text: `LICENSE-APACHE-2.0.txt`, copied verbatim from the Apache-2.0 licence
file shipped with pyca/cryptography 50.0.2). Changes: only a subset of tests was kept, and a `vendored`
field describes where each subset was copied from; `flags: ["v0"]` marks tests taken from the older
eddsa_test.json. The values themselves are unchanged and were checked locally against pyca/cryptography 50.0.2.

## Provenance (exact, not yet checked against upstream)
The cases were **not** copied from the upstream C2SP repository. Upstream raw files could not be fetched
from the authoring sandbox (no direct network; the web tools returned no document for raw.githubusercontent.com,
the GitHub file and commit pages, or jsDelivr; retried 2026-10-28, see KNOWN-GAPS 47).

| Subset | Copied from (a downstream copy, not upstream) | Upstream file it should match |
|---|---|---|
| `aes_gcm_subset.json` tcId 1, 10-13 | Wycheproof 0.4-format `aes_gcm_test.json` redistributed in pycryptodome 3.7.2 (`SelfTest/Cipher/test_vectors/wycheproof/`), read via search-result text of a third-party package mirror (gemfury.com) | `testvectors_v1/aes_gcm_test.json` |
| `ed25519_subset.json` tcId 1-6 | BoringSSL `third_party/wycheproof_testvectors/ed25519_test.json`, search-result text of boringssl.googlesource.com | `testvectors_v1/ed25519_test.json` |
| `ed25519_subset.json` tcId 10-14 (`v0`) | BoringSSL `third_party/wycheproof_testvectors/eddsa_test.json` (older file), same source | same key pair; expected in `testvectors_v1/ed25519_test.json` ("special values for r and s"), possibly under other tcIds |

"Checked against pyca/cryptography" proves the *valid* cases only; for an *invalid* case it shows that the
library rejects it, not that upstream labels it invalid. The real check is `upstream_diff.py`: it looks up every
vendored case by content in an upstream `testvectors_v1/` folder and fails on any miss. CI runs it on every push
(job `wycheproof-upstream`: shallow clone of `main`, commit hash and date printed in the log). Until that job has
passed once, treat these 16 cases as unverified copies.

`derived_vectors.json` is **not** Wycheproof data: it is derived by this lab (truncated tags, trailing bytes,
S + L) to model bugs in *our* wrappers. Each entry names the Wycheproof test it was derived from.

To use the full, current files, add the upstream repository as a git submodule and point the harness at
`testvectors_v1/` (see the lesson's README).
