# 21 · Open data and science software practice: VO standards, licences, citation and validation

`release.py` builds a small derived data release in `release/` and checks it the way CI would:
- `catalogue.vot` (VOTable 1.5, TABLEDATA);
- `CITATION.cff` (Citation File Format 1.2.0);
- `LICENSE.txt` (an SPDX id);
- `ACKNOWLEDGEMENTS.md` (each provider's credit text, verbatim);
- `metadata.json`;
- `MANIFEST.json` (SHA-256 of every file).

The rows are **synthetic** stand-ins. The input licences and credit texts are the real ones: Gaia DR3 is CC BY-NC 3.0 IGO, TESS/MAST data are public domain with a requested acknowledgement, and our own photometry is CC-BY-4.0.

Read the concept note first: `../../../content/concepts/L400/21-open-data-practice.md`. Main lab: Python 3.12 + stdlib (+ numpy for the seeded rows). The licence rules are conservative defaults that flag releases for **human review**. They are not legal advice.

## Run
```bash
python release.py
python defects.py
```
Windows (PowerShell) and macOS (zsh) use the same commands from the lab folder (`cd labs\L400\21-open-data-practice` on Windows, `cd labs/L400/21-open-data-practice` on macOS). `release/` is git-ignored.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Deterministic.
```
release licence: CC-BY-4.0
{
 "files": [
  "ACKNOWLEDGEMENTS.md",
  "CITATION.cff",
  "LICENSE.txt",
  "MANIFEST.json",
  "catalogue.vot",
  "metadata.json"
 ],
 "problems": [
  "licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)"
 ]
}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `release.py`):** `release_licence()` always answers CC-BY-4.0, our usual licence. The derived catalogue contains Gaia-derived columns under CC BY-NC 3.0 IGO, so the release silently drops a NonCommercial condition it does not own. Every file is present and well formed, and a "files present" review passes it.
- **Fix (your build task):** keep every input restriction (NC, SA) in the release licence (CC-BY-NC-4.0 here). When no standard licence fits both (NC + SA), stop with "needs human review" (`solution/release.py`).
- **Proof:** with `BUILD_TARGET=mine`, the shipped file fails 3 tests (2 build-task tests and the fitness test "published release is clean"); the solution passes. `TestFailureLab` in `test_release.py` keeps the fault reproducible.

## Design decision and fitness function
- ADR: `decisions/0001-release-gate.md` makes `check()` a blocking gate. On 6 seeded defects (`python defects.py`), a "files present" review catches 0/6 and `check()` catches 6/6:
```
{"defect": "catalogue edited after the manifest", "A_files_present": false, "B_check": true, "B_says": ["manifest: catalogue.vot missing or changed"]}
{"defect": "CITATION.cff without message", "A_files_present": false, "B_check": true, "B_says": ["citation: required key 'message' missing"]}
{"defect": "licence relaxed to CC-BY-4.0", "A_files_present": false, "B_check": true, "B_says": ["licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)"]}
{"defect": "Gaia credit paraphrased", "A_files_present": false, "B_check": true, "B_says": ["credit: verbatim acknowledgement for gaia_dr3_astrometry missing"]}
{"defect": "row with a missing TD", "A_files_present": false, "B_check": true, "B_says": ["votable: row 3 has 5 TD for 6 FIELD"]}
{"defect": "FIELD without unit", "A_files_present": false, "B_check": true, "B_says": ["votable: FIELD parallax has no unit"]}
caught: A 0/6, B 6/6
```
- Fitness: `test_fitness.py` requires check() to return [] for the published release and to catch all 6 defects. Observed: `Ran 2 tests ... OK`.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 11 tests ... OK (skipped=1)` - the astropy/cffconvert validators are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
1. + BY-SA input -> ValueError: NonCommercial and ShareAlike inputs conflict: needs human review
2. without Gaia -> CC-BY-4.0 | problems: []
```

## Build it (hardening task)
Fix `release_licence()` in `release.py` so the release keeps every restriction its inputs carry.

Hints:
- Each input has a `family` such as `BY`, `BY-NC`, `BY-SA` or `PD`. Collect the restrictions in `RESTRICTIVE = ["NC", "SA"]`.
- Build `CC-BY[-NC][-SA]-4.0` and make sure it is in `SPDX_OK`.
- A BY-SA adaptation must stay BY-SA, which permits commercial use, so NC + SA cannot both be kept: raise `ValueError`.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). Shipped file: `Ran 5 tests ... FAILED (failures=3)`; after the fix: `OK`.
Reference solution output (`python solution/release.py`):
```
release licence: CC-BY-NC-4.0
{
 "files": [
  "ACKNOWLEDGEMENTS.md",
  "CITATION.cff",
  "LICENSE.txt",
  "MANIFEST.json",
  "catalogue.vot",
  "metadata.json"
 ],
 "problems": []
}
```

## Library equivalents (pending-ci)
`validate_external.py` reads `catalogue.vot` with `astropy.io.votable.parse(..., verify="exception")` and runs `cffconvert --validate -i CITATION.cff` (cffconvert 2.0.0, if installed). STILTS `votlint` (bundled with TOPCAT) is the manual third check.

## Files
- `release.py` - main lab code (ships the unfixed `release_licence()`); `solution/release.py` - the fix
- `inputs.py` - inputs with their real licences and credit texts (synthetic rows); `votable.py` - VOTable writer/checker
- `defects.py` - seeded defects for the options evidence; `validate_external.py` - external validators (pending-ci)
- `decisions/0001-release-gate.md` - ADR; `test_fitness.py` - fitness function
- `try_it.py`; `test_release.py` (unit tests + fault reproduction); `test_build_task.py`
