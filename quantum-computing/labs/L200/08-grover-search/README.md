# Lab 08 — Small Grover search

Mark one or more basis states with a phase oracle, amplify them with the Grover operator, and pick the number of iterations: too few or too many both lose.

## Run
```bash
python crosscheck_numpy.py
python grover_lab.py
python try_it.py
python solution_search.py
python agent_assist.py --fake
python -m unittest -v
```

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
marked ['11']: oracle diagonal [1, 1, 1, -1]
  optimal k=1  P by k {0: 0.25, 1: 1.0, 2: 0.25, 3: 0.25, 4: 1.0}  matches sin^2 formula: True
marked ['101']: oracle diagonal [1, 1, 1, 1, 1, -1, 1, 1]
  optimal k=2  P by k {0: 0.125, 1: 0.7812, 2: 0.9453, 3: 0.3301, 4: 0.0122}  matches sin^2 formula: True
marked ['011', '100']: oracle diagonal [1, 1, 1, -1, -1, 1, 1, 1]
  optimal k=1  P by k {0: 0.25, 1: 1.0, 2: 0.25, 3: 0.25, 4: 1.0}  matches sin^2 formula: True
```

**`python grover_lab.py`** — *pending CI*. Expected (exact probabilities from `Statevector`, same as numpy):
```
2 qubits, marked ['11']: optimal k=1; P(success) by k: {0: 0.25, 1: 1.0, 2: 0.25, 3: 0.25, 4: 1.0}
  counts at k=1 (1000 shots, seed 5): top '11' with 1000
3 qubits, marked ['101']: optimal k=2; P(success) by k: {0: 0.125, 1: 0.7812, 2: 0.9453, 3: 0.3301, 4: 0.0122}
  counts at k=2 (1000 shots, seed 5): top '101' with ~945
```

**`python -m unittest`** — observed locally without SDKs: `Ran 20 tests ... OK (skipped=6)` (includes try-it, build-task and agent-assist tests).

## Try it
**`python try_it.py`** — observed locally without SDKs:
```
overshoot      numpy {'k': 3, 'P': 0.3301, 'optimal_k': 2, 'P_at_optimal': 0.9453}
two_marked_k2  numpy {'k': 2, 'P': 0.25, 'optimal_k': 1, 'P_at_optimal': 1.0}
```

## Build task — search by predicate
Add `grover_search_numpy(predicate, n_qubits)` (and the Qiskit `grover_search`) that builds the marked list from a Python predicate, picks k with the formula and refuses M = 0 or M ≥ N/2. Check yours with `BUILD_TASK_MODULE=my_search python -m unittest test_build_task -v` (Windows: `$env:BUILD_TASK_MODULE = "my_search"`). Reference **`python solution_search.py`** observed locally:
```
x == 5:      (['101'], 2, 0.9453)
x % 3 == 0:  (['000', '011', '110'], 1, 0.8437)
```

## Agent assist — the model proposes, code decides
A local model proposes `{"marked": [...], "iterations": k}` for three plain-English searches. Code rebuilds the marked set from a Python predicate, computes P(success) in numpy and accepts, overrides k, or rejects.

**`python agent_assist.py --fake`** — observed locally (deterministic fake server, `fake_grover_rule.py`):
```
single REJECT  marks ['110'] but spec needs ['011']
pair   ACCEPT  oracle ok; k=2 gives P=0.25, code uses k=1: P=1.0
even   REJECT  oracle ok, but best P(success)=0.5 at k=0: no amplification (M/N=2/4)
```
With a real model: `python agent_assist.py --show` (Ollama at `http://localhost:11434/v1`; set `LOCAL_MODEL`). Not run here.
