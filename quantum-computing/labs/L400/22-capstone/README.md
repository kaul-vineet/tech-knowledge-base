# Capstone 22 — an end-to-end quantum optimisation service

`service.py` (HTTP on 127.0.0.1) → `pipeline.py`: feasibility gate (lesson 19) → orchestrated noisy QAOA with batched jobs,
transpile cache and retries (lesson 17) on a compiled fake device (lesson 20) with a validated noise model → readout
mitigation (lesson 13) → fair benchmark against greedy and annealing (lesson 18) → **code decides** → report →
a local model explains, code checks. Diagram: `architecture.mmd`; decisions: `docs/adr/0001`–`0004`.
Seeded faults: job attempts 3 and 4 fail; coupler (1,2) drifted to 15 %.

## Run
```bash
python run_capstone.py          # scorecard (JSON lines)
python pipeline.py              # one default request, full report
python service.py --port 8765   # then POST JSON to http://127.0.0.1:8765/solve
python agent_assist.py --fake
python try_it.py
python -m unittest -v
```

## Expected output
**`python run_capstone.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs):
```
{"milestone": "M1 API and validation", "pass": true, "measure": {"health": 200, "solve": 200, "bad_request": 400, "bad_reason": "n must be an integer in [4, 16]"}}
{"milestone": "M2 orchestrated quantum path (batched, cached, retried)", "pass": true, "measure": {"jobs": 10, "retries": 2, "transpiles": 1, "wall_s": 28.8, "mode": "batched"}}
{"milestone": "M3 compile + noise model", "pass": true, "measure": {"esp": 0.5072, "cx": 52, "depth": 42, "gate_fidelity": 0.6224, "tvd_model": 0.0213, "tvd_ideal": 0.073}}
{"milestone": "M4 readout mitigation", "pass": true, "measure": {"ideal": 7.3525, "gate_noise_only": 6.8418, "raw": 6.774, "mitigated": 6.8549, "calibration_shots": 32000}}
{"milestone": "M5 fair benchmark + code decides", "pass": true, "measure": {"winner": "annealing", "n12_winner": "annealing", "n12_reason": "needs 12 qubits > 8 on the device"}}
{"milestone": "M6 agent explains, code checks", "pass": true, "measure": {"explain": ["ACCEPT", []], "pitch": ["REJECT", ["claims qaoa-noisy wins; code decided annealing", "claims a quantum advantage the benchmark cannot show", "number 99.9 is not in the report"]], "brief": ["REJECT", ["no winner stated"]]}}
{"rubric": "correctness", "measure": "winner median ratio 1.0", "pass": true}
{"rubric": "fairness", "measure": "one budget and one seed list for every solver", "pass": true}
{"rubric": "reliability", "measure": "2 injected job failures retried; results identical to a fault-free run", "pass": true}
{"rubric": "cost", "measure": "modelled wall 28.8 s, 10 jobs (budget 60 s)", "pass": true}
{"rubric": "honesty", "measure": "n = 12 refused for the 8-qubit device; classical answer returned", "pass": true}
{"rubric": "safety", "measure": "agent cannot change the winner; server binds 127.0.0.1", "pass": true}
{"scorecard": "6/6 milestones, 6/6 rubric", "winner": "annealing", "decided_by": "code"}
```
**`python -m unittest`**: `Ran 13 tests ... OK` (6 milestones, 5 fitness functions, 2 tryIt).

## Agent assist (fake model server)
```
explain  ACCEPT  
pitch    REJECT  claims qaoa-noisy wins; code decided annealing; claims a quantum advantage the benchmark cannot show; number 99.9 is not in the report
brief    REJECT  no winner stated
```

## Try it
```
small_budget      ('annealing', {'greedy': 1.0, 'annealing': 1.0, 'qaoa-noisy': 1.0})
calibrated_device {'esp': 0.5103, 'gate_fidelity': 0.6262, 'cx': 47, 'depth': 48}
```
