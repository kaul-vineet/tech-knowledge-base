# L600 #06 - A verifiable, replicated science-data release pipeline

Combines **astronomy** (parallax -> distance, Gaia licence terms), **cryptography** (canonical bytes, SHA-256 Merkle
manifest, Ed25519 + ML-DSA-65 signatures, key rotation, transparency log) and **distributed systems** (4 mirrors,
push-pull anti-entropy with Merkle buckets, lag, rollback/freeze). Everything is seeded and runs offline on a fake clock.

Data: the rows are **synthetic** stand-ins from astronomy L400 #21 (`inputs.rows()`); the licence and credit texts
are the providers' real ones. Gaia data are CC BY-NC 3.0 IGO, so the derived release is CC-BY-NC-4.0 and carries
ESA/DPAC's acknowledgement verbatim in `ACKNOWLEDGEMENTS.md` (covered by the signature).

## Run
```
# macOS (zsh)                                   # Windows (PowerShell)
cd integrated/labs/L600/06-signed-science-data  cd integrated\labs\L600\06-signed-science-data
python3 run_project.py                          py -3.12 run_project.py
python3 run_project.py --inject float-format    py -3.12 run_project.py --inject float-format
python3 -m unittest discover -s tests -t tests  py -3.12 -m unittest discover -s tests -t tests
python3 try_it/try_1_python_json.py             py -3.12 try_it\try_1_python_json.py
python3 try_it/try_2_short_ttl.py               py -3.12 try_it\try_2_short_ttl.py
BUILD_TARGET=mine python3 -m unittest tests.test_build_task   # PowerShell: $env:BUILD_TARGET="mine"; py -3.12 -m unittest tests.test_build_task
```
Needs Python 3.12, numpy and a cryptography release with ML-DSA support (validated with 50.0.2). It imports (never copies) astronomy
L100 #4 + L400 #21, cryptography L200 #7 + L300 #14 + L400 #17 and distributed-systems L400 #17 through `_kb.py`.

## Files
| file | role |
|---|---|
| `science.py` | processing: inverse parallax only when parallax/error >= 5 (Bailer-Jones 2015), else `needs-prior` |
| `canonical.py` | RFC 8785 JCS encoder, strict parser, and the seeded `'%.17g'` platform encoder (the fault) |
| `merkle.py` | RFC 9162 Merkle tree hash, inclusion + consistency proofs and their iterative verifiers |
| `trust.py` | signed envelopes, root of trust, dual-signature rule, retired-key windows, root chain (TUF 5.3) |
| `publisher.py` | licence gate -> files -> manifest + Merkle root -> release.json -> log entry -> timestamp |
| `tlog.py` | append-only transparency log with signed tree heads |
| `mirrors.py` | mirrors, Merkle-bucket anti-entropy, push-pull gossip rounds on the distributed L400 #17 `Sim` |
| `client.py` | the verifier (timestamp, rollback/freeze, signatures, hashes, Merkle root, licence, log proofs) |
| `world.py` / `checks.py` / `run_project.py` | the seeded story, every check, the scorecard |
| `build_task/jcs_number.py` / `solution/jcs_number.py` | build task: ECMAScript number layout |
| `decisions/000{1,2,3}-*.md` | ADRs: canonical encoding, log + freshness, rotation windows |

## Expected output (real run, Linux, Python 3.12, cryptography 50.0.2)
`python3 run_project.py`
```
{"kind": "milestone", "id": "M1", "title": "process: parallax -> distance on the L400 #21 rows", "pass": true, "rows": 28, "needs_prior": 10, "first": "4000000 270.70193010476163 pc"}
{"kind": "milestone", "id": "M2", "title": "content-addressed release with a Merkle manifest", "pass": true, "files": 5, "merkle_root": "3b45768398c20ed6", "licence": "CC-BY-NC-4.0"}
{"kind": "milestone", "id": "M3", "title": "dual-signed (Ed25519 + ML-DSA-65) with a root key rotation", "pass": true, "rfc8032_t1": true, "algs": ["Ed25519", "ML-DSA-65"], "sig_bytes": [64, 3309], "root_versions": 2}
{"kind": "milestone", "id": "M4", "title": "replicated to 4 mirrors by anti-entropy", "pass": true, "rounds": {"1": 2, "2": 2, "3": 2, "4": 4}, "conflicts": []}
{"kind": "milestone", "id": "M5", "title": "client verifies signatures, hashes and log proofs", "pass": true, "verified_from": ["m0", "m1", "m2", "m3"], "log_size": 4}
{"kind": "seam", "id": "S1", "title": "astronomy floats <-> SHA-256: canonical encoding (RFC 8785)", "pass": true, "jcs_bytes": 6536, "platform_bytes": 7901, "mirrors_agree": true}
{"kind": "seam", "id": "S2", "title": "key rotation <-> verifying old releases", "pass": true, "old_releases_verify": [1, 2, 3, 4], "retired_key_signs_v5": "release v5: no valid Ed25519 signature from a key trusted for v5"}
{"kind": "seam", "id": "S3", "title": "mirror lag <-> client freshness (rollback / freeze)", "pass": true, "lagging": "m3-lagging: offers v3, client has seen v4 (rollback)", "frozen": "m3-lagging: timestamp expired at 6000 (freeze attack or stale mirror)"}
{"kind": "seam", "id": "S4", "title": "licence + attribution <-> the signed release", "pass": true, "licence": "CC-BY-NC-4.0", "gate": "signed", "stripped_mirror": "v4: ACKNOWLEDGEMENTS.md missing or changed"}
{"kind": "fitness", "id": "F1", "title": "any single-byte tamper is detected", "pass": true, "caught": 15586, "total": 15586, "rate": 1.0}
{"kind": "fitness", "id": "F2", "title": "mirrors converge within 4 gossip rounds", "pass": true, "bound": 4, "all_up": 3, "all_up_mean": 2.04, "m3_down_3": 1, "m3_down_3_mean": 1.0}
{"kind": "fitness", "id": "F3", "title": "client rejects a release older than the newest seen", "pass": true, "older_versions_rejected": [1, 2, 3]}
{"scorecard": "PASS", "passed": 12, "total": 12, "inject": null, "seconds": 277.4}
```
(`seconds` is dominated by module loading from the sandbox's network mount; compute is ~25 s of CPU.)
M4 rounds are 1-based round numbers; for v4, m3 is unreachable in rounds 1-3 and catches up in round 4.

### Failure lab: `python3 run_project.py --inject float-format` (exit 1)
```
{"kind": "milestone", "id": "M4", ... "pass": false, "rounds": {"1": null, "2": null, "3": null, "4": null}, "conflicts": ["releases/v1/catalogue.json", "releases/v2/catalogue.json", "releases/v3/catalogue.json"]}
{"kind": "milestone", "id": "M5", ... "pass": false, "verified_from": ["m0", "m1", "m3"], "log_size": 4, "rejected": {"m2": "v4: catalogue.json missing or changed"}}
{"kind": "seam", "id": "S1", ... "pass": false, "jcs_bytes": 6536, "platform_bytes": 7901, "mirrors_agree": false}
{"kind": "diagnose", "first_difference_v1_catalogue": {"m0": "\"dec\":-3.94153,\"distance_pc\":270.7", "m2": "\"dec\":-3.9415300000000002,\"distanc", "offset": 168}}
{"scorecard": "FAIL", "passed": 9, "total": 12, "inject": "float-format", "seconds": 281.5}
```
Other seeded faults (each exit 1): `drop-old-key` -> S2 `old_releases_verify: [4]` (11/12);
`no-freshness` -> S3 `lagging: ACCEPTED, frozen: ACCEPTED`, F3 `older_versions_rejected: []` (10/12);
`licence-drop` -> S4 `gate: licence CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)` (11/12).

### Tests
`python3 -m unittest discover -s tests -t tests` -> `Ran 44 tests in 125.249s` / `OK` (3 runs, see validation).
Build task: `BUILD_TARGET=mine python3 -m unittest tests.test_build_task` on the shipped file ->
`Ran 5 tests` / `FAILED (failures=3)` (Appendix B samples, integral doubles, small numbers); against
`solution/jcs_number.py` -> `Ran 5 tests` / `OK`.

### tryIt
```
1) m2 = json.dumps: converged True | rounds {1: 2, 2: 2, 3: 2, 4: 4} | conflicts []
1) json.dumps: ['5.0', '2.5e-05', '1e-07', '1e+21', '270.70193010476163']
1) JCS       : ['5', '0.000025', '1e-7', '1e+21', '270.70193010476163'] | differ: 3 of 5
2) TTL 3600 s: usable mirrors ['m0', 'm1', 'm2', 'm3']
2) TTL  120 s: usable mirrors none | timestamp expired at 3720 (freeze attack or stale mirror)
```
tryIt 1: Python's json happens to agree with JCS on today's catalogue (after a JCS parse every whole number is an int)
- it would split the mirrors the day a release carries a value below 1e-4 or a producer writes 5.0.
tryIt 2: a TTL shorter than re-sign interval + replication lag turns every honest mirror into a "freeze".

## Seams and the tests that guard them
| seam | contract | test |
|---|---|---|
| astronomy <-> cryptography | hashes cover JCS bytes; re-encoding is idempotent; strict parse | `tests/test_seam_canonical.py` |
| cryptography <-> distributed systems | old releases on mirrors stay verifiable after rotation; retired keys cannot sign new versions | `tests/test_seam_rotation.py` |
| distributed systems <-> cryptography | lagging mirror -> rollback refused; frozen mirror -> expiry refused; failover works | `tests/test_seam_freshness.py` |
| astronomy <-> cryptography | licence gate before signing; licence + attribution inside the signed manifest | `tests/test_seam_licence.py` |

## Caution
Demo keys are derived from fixed seeds so the output is reproducible - never do that with real keys. Licence rules
are conservative defaults from astronomy L400 #21, not legal advice; Gaia's commercial-use terms need a human.
