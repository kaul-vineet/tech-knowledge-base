# 05 · Agent-based modelling: Schelling's neighbourhood model

810 agents on a 30x30 grid want >= 30% similar neighbours; unhappy ones move. Similarity climbs from 50% to ~75%.

Read the concept note first: `../../../content/concepts/05-agent-based-schelling.md`.

## Run
```bash
python schelling.py
```

## Expected output (real run, Python 3.12.15, Linux, numpy 2.5.3; seeded, identical on every run)
```
step  1: moved 160  % similar  62.2  % unhappy   8.1
step  2: moved  66  % similar  67.9  % unhappy   4.2
step  3: moved  34  % similar  69.3  % unhappy   4.0
step  5: moved  16  % similar  73.9  % unhappy   1.0
step 10: moved   4  % similar  75.1  % unhappy   0.4
step 15: moved   1  % similar  75.4  % unhappy   0.1
step 17: moved   1  % similar  75.4  % unhappy   0.0
start: % similar 50.2 -> end: 75.4 (each agent only wanted 30%)
top-left 10x10 corner at the end (. empty, x / o agent types):
x x x x x x x x x x
. x x x x x x x x x
x x x x x x . . x x
x x x x x x x o o x
o o . x x . x x o o
o . . x x x x x o o
o o x x x x x x x x
o o x x x x . x x x
o o x x x . o x x x
o . x x x x o o x x
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 5 tests ... OK (skipped=1)` - Mesa test skipped locally (not installed); runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
want 30%: end % similar 75.4, % unhappy 0.0, steps 17
want 50%: end % similar 87.6, % unhappy 0.0, steps 13
seeds 1-5 end % similar: [72.3, 76.3, 75.1, 74.7, 73.1]
```

## Library equivalent (pending-ci)
`schelling_mesa.py` does the same with the library. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `schelling.py` - main lab code
- `schelling_mesa.py` - Mesa 3.5.1 equivalent (pending-ci)
- `test_schelling.py` - tests; Mesa test skipped locally
- `try_it.py` - tryIt script
