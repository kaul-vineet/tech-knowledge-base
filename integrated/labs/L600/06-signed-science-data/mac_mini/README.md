# 06 on the Mac mini — mirrors as real HTTP servers, catalogue-scale Merkle trees, and a second JCS implementation

In the lab, four mirrors are Python objects exchanging dictionaries on a simulated clock. On the Mac mini each mirror
is its own process serving HTTP on 127.0.0.1, anti-entropy is real HTTP traffic, one mirror is killed and recovers
from disk, and the client verifies every release over the network. The Mac also has the memory to build and sign
Merkle trees for 10^5–10^7 catalogue rows, and Node to check that another language produces the same signed bytes.

| File | What it does |
|---|---|
| `mirror_server.py` | one mirror process: `mirrors.Mirror` (immutable keys, max-version timestamp, 16 buckets) persisted to append-only files; HTTP `GET /root`, `/bucket/<i>`, `/obj`, `/timestamp`, `PUT /obj`, `/timestamp`, `POST /pull?port=`; `--encoder platform` = the failure lab's m2 |
| `http_world.py` | publisher → m0 over HTTP → push-pull gossip over HTTP (seeded) → the victim mirror is SIGKILLed, restarted from disk, kept down for 2 rounds → `client.Client` verifies the latest release from every mirror over HTTP; H1/H2/H3 |
| `scale_bench.py` | rows → `science.process` → JCS → RFC 9162 leaves → tree (bottom-up, or `--streaming` with O(log n) memory) → Ed25519 + ML-DSA-65 signature → 100 inclusion proofs; rows/s per step, RSS per row, max rows by RAM |
| `jcs_crosscheck.py` + `jcs_node/` | the same values canonicalised by Python (`canonical.dumps`) and by Node (RFC 8785's JSON.stringify recipe; optionally the npm package `canonicalize` 5.1.0, Apache-2.0) must give identical bytes |
| `ci.sh` | medium-size Mac runs for `.github/workflows/mac-mini.yml`: 8 mirrors × 10 releases, the HTTP failure lab (must exit 1), 10^5 rows, JCS with the npm package when `npm` exists |
| `tests/test_mac_mini.py` | 7 tests (tree maths against `merkle.py`, mirrors with and without the fault, JCS) |

## Run
```bash
# macOS (zsh), from integrated/labs/L600/06-signed-science-data, inside the lab venv
python mac_mini/http_world.py --mirrors 8 --releases 40 --out ~/kb-runs/06-http.jsonl
python mac_mini/http_world.py --here --inject float-format            # failure lab over HTTP: exit 1
python mac_mini/scale_bench.py --rows 1e5 1e6 1e7 --out ~/kb-runs/06-scale.jsonl
python mac_mini/scale_bench.py --rows 1e7 --streaming
(cd mac_mini/jcs_node && npm install) && python mac_mini/jcs_crosscheck.py   # Node 24: shared/WORKSTATION-SETUP.md
python -m unittest discover -s mac_mini/tests -t mac_mini/tests
```

## Real output here (Linux sandbox, 2026-11-02 — sandbox values, NOT Mac values)
```
$ python mac_mini/http_world.py --here
{"experiment": "06 mirrors over HTTP", "mirrors": 4, "releases": 4, "seed": 6, "inject": null, "http_requests": 231, "bytes_moved": 174951, ...}
{"fitness": "H1 every release converges on every mirror", "rounds_per_release": {"1": 2, "2": 2, "3": 2, "4": 3}, "max_rounds": 20, "conflicts": {}, "pass": true}
{"fitness": "H2 client verifies the latest release from every mirror over HTTP", "verified": {"m0": true, "m1": true, "m2": true, "m3": true}, "reasons": {}, "pass": true}
{"fitness": "H3 killed mirror recovered its objects from disk", "mirror": "m3", "objects_before_kill": 18, "recovered_on_restart": 18, "pass": true}
$ python mac_mini/http_world.py --here --inject float-format
{"experiment": "06 mirrors over HTTP", ..., "inject": "float-format", "http_requests": 2604, "bytes_moved": 4839263, ...}
{"fitness": "H1 every release converges on every mirror", "rounds_per_release": {"1": null, "2": null, "3": null, "4": null}, "conflicts": {"m0": ["releases/v1/catalogue.json", ...], ...}, "pass": false}
{"fitness": "H2 client verifies the latest release from every mirror over HTTP", "verified": {"m0": true, "m1": true, "m2": false, "m3": true}, "reasons": {"m2": "v4: catalogue.json missing or changed"}, "pass": false}
$ python mac_mini/scale_bench.py --here
{"rows": 10000, "streaming": false, "bytes_per_row_jcs": 249.0, "same_root_as_merkle_mth": true, "root": "8923a7bff6a28e32", "rows_per_s": {"process": 341607, "canonicalise": 5622, "leaf_hash": 399614, "tree": 129062}, "sign_ms": 1.76, "verify_ms": 0.55, "proof_verify_us": 56.1, "signatures_valid": true, "proofs_valid": true, "proof_hashes_max": 14, ...}
$ python mac_mini/jcs_crosscheck.py --here
{"check": "python canonical.dumps reproduces the published RFC 8785 sample", "pass": true}
{"cross_language": "python canonical.dumps vs node v24.7.0 builtin", "vectors": 8, "identical": 8, "different": [], "platform_dumps_vectors_that_differ": 6, "pass": true}
```
With the fault, gossip never settles: m2 keeps re-serialising, its bucket hashes never match, and every round moves
the same objects again — 28× the bytes of the healthy run for the same four releases. The client still gets a good
release from m0, m1 and m3 (a bad mirror cannot stop updates from good ones), and refuses m2's.

## Experiments (what you should see on the Mac and how to read it)
1. **Mirrors over HTTP.** Expect H1–H3 to pass with 8 mirrors and 40 releases; `rounds_per_release` around
   log2(mirrors) + 1–2, a bit more for the release during which a mirror was down. `bytes_moved` should be close to
   (mirrors − 1) × release size per release: anti-entropy sends only missing keys. A round count that grows with the
   release number means the bucket comparison is not narrowing the exchange.
2. **Catalogue scale.** Expect `canonicalise` to be the slowest step by far (pure-Python JCS; 10^7 rows at the sandbox's
   5,600–9,900 rows/s would take 17–30 min), leaf hashing and tree building to be cheap, signing to stay in
   milliseconds whatever the size (one signature over the root), and `proof_hashes_max` = 24 at 10^7 rows. Read the
   `wall` line from the largest size (`reliable: true` only from 10^5 rows): if `max_rows_by_ram_GB` for your Mac is
   below your catalogue, ship the streaming tree (`--streaming`: same root, flat memory) and keep levels on disk for
   proofs. That is an ADR-0002 addendum (how the log/manifest is built), not a change to what is signed.
3. **Second implementation of RFC 8785.** Expect `identical` = all vectors for both `builtin` and `canonicalize`,
   and `platform_dumps_vectors_that_differ` > 0. One differing vector means one of the two implementations is wrong
   for that value — a signature made in one language would not verify in the other. Here the built-in recipe already
   ran under Node v24.7.0; the npm package is pendingMac.

## Overnight
`http_world.py --mirrors 8 --releases 40` then `scale_bench.py --rows 1e5 1e6 1e7` (and `--streaming`). Together they
show the two costs that grow with the archive: gossip traffic per release and the time/memory of building a manifest
for a big catalogue.

## Limits
`http.server` is "not recommended for production" (Python docs): it binds 127.0.0.1 here and serves only the lab's
objects. A real mirror would sit behind a production web server; the protocol (roots → buckets → keys) is the point.

Sources and verification notes: `integrated/research/mac-mini-evidence.md`, section 06.
