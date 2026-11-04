# 18 · Time-domain alerts: difference detection, alert schema and broker filters

A **synthetic** survey field is imaged twice per night (exposures a and b, 20 minutes apart) for 8 nights against a deep reference. Seeing and transparency change every night. The truth contains a supernova from night 3, a catalogued variable star V1, an asteroid and cosmic rays. `alerts.py`:
1. subtracts the reference;
2. detects 5σ residuals;
3. writes alert packets (ZTF/Rubin-style fields, validated by `schema.py`);
4. runs a broker: three options, A firehose, B classify and drop bogus, C B plus one alert per object per night.

`agent_assist.py` lets a local model *explain* an alert; code has already classified it.

Read the concept note first: `../../../content/concepts/L400/18-alert-broker.md`. Main lab: Python 3.12 + numpy only; the agent uses the vendored helper in `../_agent/` (fake server in tests).

## Run
```bash
python alerts.py
python agent_assist.py
```
Windows (PowerShell) and macOS (zsh) use the same commands from the lab folder (`cd labs\L400\18-alert-broker` on Windows, `cd labs/L400/18-alert-broker` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
{"option": "A", "alerts_per_night": 192.4, "real_fraction": 0.027, "classes": {"bogus": 944, "moving": 155, "transient": 440}, "schema_errors": 0}
{"option": "B", "alerts_per_night": 74.4, "real_fraction": 0.045, "classes": {"moving": 155, "transient": 440}, "schema_errors": 0}
{"option": "C", "alerts_per_night": 58.2, "real_fraction": 0.045, "classes": {"moving": 155, "transient": 311}, "schema_errors": 0}
option C, night 7: 70 alerts; first 5:
```
(The shipped run then lists the first 5 of night 7's 70 alerts.)

## Failure lab: break it, see it, fix it
- **Fault (shipped in `alerts.py`):** `difference()` returns new − reference. The reference has sharper seeing (σ 1.2 px) and full transparency, so every star leaves a ring and a residual. The result is an alert storm: 192.4 per night in the firehose and 58.2 per night even after the broker, only 4.5 % real. Constant stars become "transients".
- **Fix (your build task):** blur the reference to the night's seeing, σ_k = √(σ_new² − σ_ref²), fit new = a·ref + b by least squares, and subtract (`solution/alerts.py`). Option C then gives 3.5 alerts per night, 85.7 % real.
- **Proof:** with `BUILD_TARGET=mine`, `test_constant_stars_vanish` (build task) and `test_alert_volume_and_purity` (fitness) fail on the shipped file; all 6 pass on the solution. The supernova is bright enough to be found either way, so that test passes on both. `TestFailureLab` in `test_alerts.py` keeps the fault reproducible.

## Design decision and fitness function
- ADR: `decisions/0001-alert-broker-design.md` chooses **C** on matched differences. A gives 9.8 alerts per night (46.2 % real), B 4.2 (88.2 %), C 3.5 (85.7 %).
- Fitness: `test_fitness.py` requires ≤ 6 alerts per night, ≥ 0.8 real, 0 schema errors, the supernova as a transient on nights 3–7, V1 always `known_variable`, and ≥ 80 % of asteroid detections `moving`. Observed: `Ran 4 tests ... OK`.

## Agent assist (explains, never decides)
`python agent_assist.py` sends one alert of each class as a facts block to the model (here the fake server, marker `[[ASTRO-ALERT]]`). Code publishes the explanation only if it names code's class and nothing else, and every number in it is one of the facts. Observed with the fake model:
```
{"candid": 23, "code_class": "known_variable", "class_ok": false, "unverified": ["2.5"], "publish": false}
{"candid": 33, "code_class": "moving", "class_ok": true, "unverified": ["2.5"], "publish": false}
{"candid": 32, "code_class": "transient", "class_ok": true, "unverified": ["2.5"], "publish": false}
```
The fake model calls V1 "a new transient" (it ignored the cross-match) and invents "2.5 magnitudes". Both are caught. With `--real`, the script uses `LOCAL_MODEL_URL` / `LOCAL_MODEL` (Ollama `qwen2.5:1.5b` by default). Only the facts block is sent: no images, no keys. Not run here against a real model.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK (skipped=1)` - the fastavro round-trip is skipped locally (not installed) and runs in CI. Run 3× in a row: identical.

## Try it
```bash
python try_it.py
```
Observed:
```
1. PSF matched, flux not, option A: 43.8 alerts/night, classes {'bogus': 320, 'known_variable': 2, 'moving': 18, 'transient': 10}
1. PSF matched, flux not, option C: 3.0 alerts/night, classes {'known_variable': 1, 'moving': 18, 'transient': 5}
2. no known-variable catalogue: V1 alerts classified as ['transient', 'transient']
```
Matching only the PSF leaves every star as a *negative* residual (320 bogus in the firehose). The broker drops them, but a fading real source would be dropped the same way.

## Build it (hardening task)
Replace `difference()` in `alerts.py` with a PSF- and flux-matched subtraction.

Hints:
- `blur(img, sigma)` exists. Blur the **reference** (the sharper image), never the new one, by √(σ_new² − σ_ref²) (`sim.REF_SIGMA` = 1.2).
- Fit `new ≈ a·ref_blurred + b` with `np.linalg.lstsq` on all pixels. The few variable pixels hardly move a and b.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). Shipped file: `Ran 6 tests ... FAILED (failures=2)`; after the fix: `OK`.
Reference solution output (`python solution/alerts.py`):
```
{"option": "A", "alerts_per_night": 9.8, "real_fraction": 0.462, "classes": {"bogus": 44, "known_variable": 3, "moving": 18, "transient": 13}, "schema_errors": 0}
{"option": "B", "alerts_per_night": 4.2, "real_fraction": 0.882, "classes": {"known_variable": 3, "moving": 18, "transient": 13}, "schema_errors": 0}
{"option": "C", "alerts_per_night": 3.5, "real_fraction": 0.857, "classes": {"known_variable": 2, "moving": 18, "transient": 8}, "schema_errors": 0}
option C, night 7: 4 alerts; first 5:
{"night": 7, "exposure": "a", "objectId": "AKB034041", "class": "transient", "flux": 110.4, "n_prv": 0}
{"night": 7, "exposure": "a", "objectId": "AKB049044", "class": "moving", "flux": 4137.9, "n_prv": 0}
{"night": 7, "exposure": "a", "objectId": "AKB020045", "class": "transient", "flux": 15141.0, "n_prv": 4}
{"night": 7, "exposure": "b", "objectId": "AKB050044", "class": "moving", "flux": 4601.3, "n_prv": 0}
```

## Library equivalent (pending-ci)
`alert_avro.py` writes the option-C packets to an Avro container with fastavro 1.13.1 (`parse_schema`, `validate`, `writer`/`reader`, deflate), the wire format ZTF and Rubin use, and reads them back.

## Files
- `alerts.py` - main lab code (ships the unfixed `difference()`); `solution/alerts.py` - the fix
- `alert_sim.py` - seeded sky + truth; `schema.py` - packet schema + validator; `alert_avro.py` - fastavro equivalent (pending-ci)
- `agent_assist.py` - local-model explanation behind a code gate; `decisions/0001-alert-broker-design.md` - ADR
- `try_it.py`; `test_alerts.py`; `test_build_task.py`; `test_fitness.py`; `test_agent_assist.py`
