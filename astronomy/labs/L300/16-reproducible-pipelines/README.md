# 16 · Reproducible data pipelines: provenance, caching and versioned inputs

A three-step pipeline (load → detrend → Lomb–Scargle period) runs on a **synthetic** variable-star light curve. Each step result is cached, and each step run appends one provenance record to `prov.jsonl` (W3C PROV idea: activity, used entity + SHA-256, parameters, code version, generated hash, cache hit/miss). The data arrives in two releases. In v1, telescope B wrote JD − 2460000 instead of MJD − 60000, so half the times are 0.5 d late. v2 corrects this.

Read the concept note first: `../../../content/concepts/L300/16-reproducible-pipelines.md`. Main lab: Python 3.12 + numpy only. The joblib equivalent needs the L300 pins: `python -m pip install -r ../requirements.txt`.

## Run
```bash
python pipeline.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\16-reproducible-pipelines` on Windows, `cd labs/L300/16-reproducible-pipelines` on macOS). The demo writes `work/` (cache + `prov.jsonl`, git-ignored). `python make_data.py` rewrites `data/` with the same bytes.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
v1 input        : {'period_d': 0.43049, 'power': 0.5201}
v1 re-run       : {'period_d': 0.43049, 'power': 0.5201}
v2 (corrected)  : {'period_d': 0.43049, 'power': 0.5201}   <- true period 0.3011 d
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "miss"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "5a283c0d0f18", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `pipeline.py`):** `cache_key()` = step name + input **file name** + parameters. When the corrected v2 release replaces `lightcurve.csv`, both steps report `"cache": "hit"`. The pipeline returns the v1 alias, 0.43049 d, for v2 data whose true period is 0.3011 d. There is no error and no warning.
- **Symptom (read it in `prov.jsonl`):** the last two records show a **new** input hash (`6141395bece9` instead of `4c4576852c83`) next to `"cache": "hit"` and the **old** generated hash. The provenance log notices; the cache did not.
- **Fix (your build task):** content-address the key with the upstream data's hash, the step's source-code hash and the parameters (`solution/pipeline.py`). v2 → miss, miss → 0.30112 d.
- **Proof:** `test_build_task.py`. With `BUILD_TARGET=mine` on the shipped file, 2 of 3 tests fail (new release recomputed; parameter change reaches downstream); on the solution all pass, and identical input still hits. `TestFailureLab` in `test_pipeline.py` keeps the fault reproducible.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK (skipped=1)` - the joblib test is skipped locally (not installed) and runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. shipped: window 5 -> {'period_d': 0.30112, 'power': 0.882}; window 1 -> {'period_d': 0.30112, 'power': 0.882}; cache ['miss', 'miss', 'miss', 'hit']
2. fixed, FREQ changed: before {'period_d': 0.30112, 'power': 0.882}; after {'period_d': 0.30112, 'power': 0.882}; cache ['miss', 'miss', 'hit', 'hit']
```
In tryIt 2, the "after" result is stale: a 0.05–3.0 c/d grid cannot even reach 3.32 c/d. A module-level constant is hidden input. Pass it as a parameter, or hash it into the code version.

## Build it (hardening task)
Change `cache_key()` in `pipeline.py` so a cached result is reused only for the same data, code and parameters.

Hints:
- `cache_key()` already receives `upstream` (the data the step consumes) - hash it with `sha256(upstream)`.
- `inspect.getsource(step)` gives the step's code; hash it, so editing a step invalidates its results.
- A file name is not an identity; releases keep the same name.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 3 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/pipeline.py` (observed: `Ran 3 tests ... OK`).
Reference solution output (`python solution/pipeline.py`):
```
v1 input        : {'period_d': 0.43049, 'power': 0.5201}
v1 re-run       : {'period_d': 0.43049, 'power': 0.5201}
v2 (corrected)  : {'period_d': 0.30112, 'power': 0.882}   <- true period 0.3011 d
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "miss"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "2a2afa4414a8", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "d3c83e662e46", "cache": "hit"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "4c4576852c83"}, "upstream_sha256": "d3c83e662e46", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "dab630b559eb", "cache": "hit"}
{"activity": "detrend", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "5a283c0d0f18", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "generated_sha256": "8dbcf371c9c4", "cache": "miss"}
{"activity": "best_period", "used": {"entity": "lightcurve.csv", "sha256": "6141395bece9"}, "upstream_sha256": "8dbcf371c9c4", "params": {}, "code_sha256": "eaac370b4f42", "generated_sha256": "85c5f7d18979", "cache": "miss"}
```

## Stretch (after the build task)
Write `lineage(prov_lines, generated_sha)`: start from a result's hash and walk `generated → upstream` records back to the input file. That answers "where did this number come from?" from the log alone.
Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`). Reference (`python solution/lineage.py`):
```
{"activity": "best_period", "params": {}, "code_sha256": "eaac370b4f42", "input_file_sha256": "6141395bece9"}
{"activity": "detrend", "params": {"window_nights": 5}, "code_sha256": "6d5af32b5516", "input_file_sha256": "6141395bece9"}
```

## Library equivalent (pending-ci)
`cache_joblib.py` shows that `joblib.Memory` hashes the call **arguments**. Keyed on a path string it returns the stale 0.43049 d; keyed on the loaded data it returns 0.30112 d. The test expects exactly that pair. It is skipped here and runs in CI.

## Files
- `pipeline.py` - main lab code (ships the unfixed `cache_key()`)
- `periodogram.py` - numpy Lomb–Scargle; `make_data.py` + `data/lightcurve_v1.csv`, `data/lightcurve_v2.csv` (synthetic)
- `cache_joblib.py` - joblib equivalent (pending-ci)
- `solution/pipeline.py` - buildTask solution; `solution/lineage.py` - stretch solution
- `try_it.py`; `test_pipeline.py` (unit tests + fault reproduction); `test_build_task.py`; `test_stretch.py`
