# 22 · Capstone: an exoplanet transit search pipeline

There are twelve **synthetic** TESS-like light curves: 27 days at a 10-minute cadence, with a 1-day gap, a slow instrumental drift, and noise of 400–1000 ppm. They contain three planets (3.12 d, 7.41 d, 12.35 d), two eclipsing binaries, a spotted star, a post-gap ramp and five quiet stars. `run_capstone.py` runs the whole search and prints a JSON-lines scorecard:
- **M1** detrend;
- **M2** BLS-lite search;
- **M3** vetting (code decides);
- **M4** MCMC fit (the trapezoid model and Metropolis sampler from L300 #15, imported);
- **M5** provenance (SHA-256 of every input + parameters, the L300 #16 idea);
- **M6** a local model *explains* each candidate behind a code gate (L400 #18 pattern).

Read the concept note first: `../../../content/concepts/L400/22-capstone.md`. Architecture: `architecture.mmd`. Decisions: `decisions/0001-detrending.md`, `0002-vetting-rules.md`, `0003-agent-boundary.md`. Main code: Python 3.12 + numpy only.

## Run
```bash
python run_capstone.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L400\22-capstone` on Windows, `cd labs/L400/22-capstone` on macOS). The first run writes `data/` (seeded, same bytes every time, git-ignored); it takes about 30 s. It writes `scorecard.jsonl` and `prov.jsonl`.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Seeded, identical on every run.
```
{"milestone": "M1 load + detrend", "pass": true, "rms_over_noise": {"S07": 0.988, "S08": 0.973, "S09": 1.02, "S10": 1.0, "S11": 0.981, "S12": 0.996}}
{"milestone": "M2 BLS search", "pass": true, "period_error_percent": {"S01": 0.032, "S02": 0.049, "S03": 0.045, "S04": 0.021, "S05": 0.021}}
{"milestone": "M3 vetting", "pass": true, "candidates": ["S01", "S02", "S03"], "rejected": {"S04": "secondary eclipse at phase 0.5 (5217 ppm)", "S05": "odd/even depths differ (5937 vs 11603 ppm)"}}
{"milestone": "M4 MCMC fit", "pass": true, "depth_minus_truth_in_sigma": {"S01": 2.22, "S02": -0.95, "S03": 0.9}, "fits": {"S01": {"depth_ppm": 8169, "depth_err_ppm": 76, "t14_h": 2.71, "acceptance": 0.239, "tau": 39.1}, "S02": {"depth_ppm": 2940, "depth_err_ppm": 63, "t14_h": 3.45, "acceptance": 0.288, "tau": 33.6}, "S03": {"depth_ppm": 5096, "depth_err_ppm": 107, "t14_h": 4.23, "acceptance": 0.285, "tau": 25.0}}}
{"milestone": "M5 provenance + reproducibility", "pass": true, "inputs_hashed": 12, "s01_sha256": "3a31a29c1689", "rerun_period_d": 3.1244}
{"milestone": "M6 agent explanation", "pass": true, "explained": 6, "published": [], "overclaims_blocked": ["S04", "S05", "S06"], "unverified_numbers": ["1.8"]}
{"scorecard": "PASS", "passed": 6, "total": 6}
```

## Milestones
| Milestone | Deliverable | Test |
|---|---|---|
| M1 load + detrend | `make_data.py`, `pipeline.detrend()` (0.75 d running median, masked re-detrend) | `test_capstone.py::M1Data` |
| M2 BLS search | `pipeline.bls()`: 6000 frequencies × 4 durations, SNR and SDE | `test_capstone.py::M2Search` |
| M3 vetting | `pipeline.vet()`: SNR/SDE, ≥ 2 transits, odd/even, secondary, duration | `test_capstone.py::M3Vetting` |
| M4 MCMC fit | `pipeline.fit()` → L300 #15 `transit_fit.fit_lm` + `mcmc.run` on folded data | `test_capstone.py::M4Fit` |
| M5 provenance | `prov.jsonl`: input SHA-256, parameters, output hash; deterministic rerun | `test_capstone.py::M5Provenance` |
| M6 agent explanation | `agent_explain.py` (facts only; numbers and claims checked) | `test_capstone.py::M6Agent` |

Fitness functions (`test_fitness.py`): recovery (3/3 planets, period error < 0.1 %), 0 false positives among the 9 other stars, depths within 3σ of the injection, and scorecard PASS with nothing gated published.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 13 tests ... OK` (about 60 s; the search runs once per test process). Run 3× in a row: OK, OK, OK.

## Try it
```bash
python try_it.py
```
Observed:
```
1. S03 window 0.75 d: period 12.3454 d, depth 4834 ppm, SNR 43.96
1. S03 window 0.25 d: period 12.3454 d, depth 726 ppm, SNR 6.69
2. S05 odd/even threshold 3.0 sigma -> ('rejected', ['odd/even depths differ (5937 vs 11603 ppm)'])
2. S05 odd/even threshold inf sigma -> ('planet_candidate', [])
```

## Agent assist
M6 sends each result with SNR ≥ 10 to the model as a facts block (marker `[[ASTRO-CANDIDATE]]`; the fake server in `../_agent/` calls every candidate "a planet" and invents "1.8 Earth radii"). Code blocks every explanation that contains an unverified number or calls a rejected candidate a planet; the verdicts were fixed before the call. `python run_capstone.py --real-model` uses `LOCAL_MODEL_URL` / `LOCAL_MODEL` (Ollama `qwen2.5:1.5b` by default). Only the facts are sent. Not run here against a real model.

## Derived formula: the transit-duration bound
The vetting rule "T14 ≤ 1.5 × 13 h × (P / 1 yr)^(1/3)" in `pipeline.vet()` is **derived, not quoted**:
1. A central transit (b = 0) on a circular orbit lasts T14 ≈ (P/π)(R★/a) when R★ ≪ a and Rp ≪ R★. This is the small-angle limit of the duration formula in Seager & Mallén-Ornelas (2003), used in lesson 15.
2. By Kepler's third law, a = 1 au × (P / 1 yr)^(2/3) for one solar mass.
3. So T14 ≈ (P/π) × 0.00465 × (P / 1 yr)^(−2/3) = (8766 h / π) × 0.00465 × (P / 1 yr)^(1/3) ≈ 13.0 h × (P / 1 yr)^(1/3), using R☉/au = 0.00465.

A central transit is the longest possible, so this is an upper bound for a Sun-like star; the ×1.5 margin allows for larger stars and eccentric orbits. Example: P = 6.27 d gives 13.0 × 0.258 = 3.35 h, so the rule rejects durations above 5.03 h. See `decisions/0002-vetting-rules.md`.

## Real data (pending-ci, needs network)
`fetch_tess.py` downloads π Mensae (TESS sector 1, SPOC) with lightkurve 2.6.0 and runs the same `detrend` + `bls`. The published period of π Men c is 6.27 d (Huang et al. 2018; Gandolfi et al. 2018). TESS data are public at MAST; acknowledge them as in lesson 21.

## Files
- `run_capstone.py` - runs M1-M6, prints and writes the scorecard; `pipeline.py` - stages; `make_data.py` - seeded data + truth
- `agent_explain.py` - gated explanations; `fetch_tess.py` - real-data path (pending-ci)
- `architecture.mmd`; `decisions/0001-0003`; `try_it.py`; `test_capstone.py`; `test_fitness.py`
