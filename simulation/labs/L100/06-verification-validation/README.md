# 06 · Is the model right? Verification vs validation

Unit-test a queue model's rule, validate it with replications against M/M/1, and sweep one parameter.

Read the concept note first: `../../../content/concepts/06-verification-validation.md`.

## Run
```bash
python vv.py
```

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
1. reproducibility: seed 1 -> ef34cf71198d, seed 1 again -> ef34cf71198d, seed 2 -> ac9c300ece80
2. validation (lam=0.8): simulated 4.046 +/- 0.195 min vs formula 4.000 -> PASS
3. sensitivity to arrival rate (utilisation = lam/mu):
   lam=0.5  simulated  1.003 +/- 0.020   formula  1.000
   lam=0.6  simulated  1.506 +/- 0.037   formula  1.500
   lam=0.7  simulated  2.353 +/- 0.075   formula  2.333
   lam=0.8  simulated  4.046 +/- 0.195   formula  4.000
   lam=0.9  simulated  8.952 +/- 0.730   formula  9.000
```
The hash covers waits rounded to 9 decimals, so a last-bit difference in the C math library (`math.log` inside `expovariate`) on macOS or Windows cannot change it.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK (skipped=1)` - 7 V&V tests (the SciPy t-quantile test is skipped locally, runs in CI) + 7 agent-assist tests against the fake model server.

## Try it
```bash
python try_it.py
```
Observed:
```
buggy rule: min wait -5168.4 min, mean wait -2619.9 min  (negative waits are impossible)
warm-up   0: average of 50 short runs = 3.92 min (formula 4.00)
warm-up 500: average of 50 short runs = 4.02 min (formula 4.00)
```

## Agent assist (optional): a local model proposes the sweep, code decides
```bash
python agent_assist.py --fake      # deterministic fake model server, no download
python agent_assist.py             # your local Ollama (http://localhost:11434/v1, model qwen2.5:1.5b)
```
Observed with `--fake`:
```
1. agent proposed: {"parameter": "lam", "values": [0.5, 0.7, 0.9, 1.2], "customers": 20000}
2. code validated: run lam=[0.5, 0.7, 0.9] with 20000 customers; rejected: 1.2: outside [0.05, 0.95] (unstable or trivial queue)
3. code ran 10 replications per value:
   lam | simulated mean wait (min) | 95% CI half-width | M/M/1 formula (min)
   0.50 | 1.014 | 0.033 | 1.000
   0.70 | 2.396 | 0.105 | 2.333
   0.90 | 9.141 | 1.275 | 9.000
4. agent explained: Mean wait grows faster than the arrival rate: at lam=0.50 the simulation gives 1.014 min (formula 1.000), at lam=0.90 it gives 9.141 min (formula 9.000). Extrapolating, at lam=0.95 the wait would be about 19.0 min.
5. code checked 8 quoted numbers: 6 match the table; UNVERIFIED (treat as the model's guess): 0.95, 19.0
```
The agent proposed lam=1.2 (an overloaded queue): code rejected it before anything ran. The explanation's numbers were checked against the table; the extrapolated `0.95 -> 19.0` claim was flagged because the simulation never produced it.
**Caution:** the agent never runs code, never chooses what is accepted, and never sees secrets - only parameter names and the results table are sent. With a real model the replies change from run to run; the checks stay the same.

## Files
- `vv.py` - main lab code
- `test_vv.py` - verification + validation tests
- `try_it.py` - tryIt script
- `agent_assist.py` - agent proposes / code validates, runs and checks
- `test_agent_assist.py` - plan validation, number check, end-to-end with the fake server
- `../../_shared/local_agent/` - vendored client + fake model server (one topic rule, see its header)
