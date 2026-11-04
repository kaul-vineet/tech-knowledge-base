# 10 · Light curves and periods

Find the period of a synthetic pulsating star in gappy ground-based data with a numpy Lomb-Scargle periodogram, see the 1-day alias, and see why it misses a transit.

Read the concept note first: `../../../content/concepts/L200/10-light-curves.md`.

## Run
```bash
python periods.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L200\10-light-curves` on Windows, `cd labs/L200/10-light-curves` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux; deterministic, identical on every run)
`python periods.py`:
```
1104 points over 29.3 d (23 clear nights)
variable true P 0.5671 d | LS best 0.5669 d (power 0.770) | next peak 1.3074 d | skew +0.01
transit  true P 3.2127 d | LS best 0.3211 d (power 0.032) | next peak 1.5998 d | skew +0.82
1-day alias of the variable: 1 / (1/0.5671 - 1) = 1.3100 d
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 13 tests ... OK (skipped=1)` - library comparisons are skipped locally (not installed) and run in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
one site      : peak power 0.770, power at the 1-day alias 0.541
no daily gaps : peak power 0.777, power at the 1-day alias 0.005
8 nights: best period 0.5665 d (true 0.5671), error 55 s
30 nights: best period 0.5669 d (true 0.5671), error 15 s
```

## Build it (your task)
Implement bootstrap_fap(t, y, freqs, n, seed): shuffle the magnitudes n times (same times, same noise, no signal), record the highest Lomb-Scargle peak each time, and return (count >= observed peak + 1) / (n + 1).

Hints:
- rng = np.random.default_rng(seed); rng.permutation(y) keeps the values but destroys the periodicity.
- Compare maxima over the whole grid, not the power at one frequency.
- +1 in numerator and denominator: never report exactly 0.

Check: `python -m unittest test_build_task -v` checks `solution/` by default. To check **your** edited file:
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v      # macOS / Linux
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v   # Windows PowerShell
```
Observed on the shipped (unfinished) file: `Ran 3 tests ... FAILED (errors=3)`. The reference solution output (`python solution/periods.py`):
```
1104 points over 29.3 d (23 clear nights)
variable true P 0.5671 d | LS best 0.5669 d (power 0.770) | next peak 1.3074 d | skew +0.01
transit  true P 3.2127 d | LS best 0.3211 d (power 0.032) | next peak 1.5998 d | skew +0.82
variable   bootstrap FAP (100 shuffles) = 0.010
transit    bootstrap FAP (100 shuffles) = 0.010
pure noise bootstrap FAP (100 shuffles) = 0.386
1-day alias of the variable: 1 / (1/0.5671 - 1) = 1.3100 d
```

## Library equivalent (pending-ci)
`periods_astropy.py` compares the power with Astropy 8.0.2 `LombScargle(fit_mean=False, center_data=True, normalization='standard')`. **Not run yet** (pending-ci). lightkurve wraps the same class for Kepler/TESS data.

## Agent assist (optional)
```bash
python agent_assist.py --fake   # deterministic fake model server
python agent_assist.py          # local Ollama at LOCAL_MODEL_URL
```
Observed with the fake server:
```
1. agent proposed: class='pulsating variable', period=1.31 d
2. code decided: class='pulsating variable' (agent agrees), period=0.5669 d -> agent period overruled: 1-day alias of the code's period
3. agent explained: The periodogram peaks at 0.5669 days, so the star repeats every 0.5669 days. The false-alarm probability is below 0.001%, so the signal is certain.
4. code checked 3 quoted numbers: 2 match; UNVERIFIED (treat as the model's guess): 0.001
```
The agent only proposes and explains. Code computes, decides and flags any quoted number that is not in the table. Tests: `python -m unittest test_agent_assist -v` (fake server only).

## Notes
Light curves are synthetic and seeded; `python periods.py --export` writes variable.csv and transit.csv for TOPCAT.

## Files
- `periods.py` - main lab code (bootstrap_fap unfinished)
- `solution/periods.py` - buildTask solution
- `periods_astropy.py` - Astropy 8.0.2 LombScargle equivalent (pending-ci)
- `agent_assist.py` - agent proposes class + period; code decides and checks
- `test_periods.py` - sine recovery, alias, transit miss
- `test_build_task.py` - buildTask check (BUILD_TARGET=mine switch)
- `test_agent_assist.py` - agent-assist tests (fake server only)
- `try_it.py` - tryIt script
- `labs/_shared/local_agent/` - vendored chat client + fake model server
