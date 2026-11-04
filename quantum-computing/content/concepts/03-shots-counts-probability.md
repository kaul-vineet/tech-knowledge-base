# Concept: shots, counts and probability

## Why it matters
A test expects H to return `{'0': 500, '1': 500}`; CI gets 487/513. Nothing is broken: every quantum result is a **sample**, and samples vary.

## Mental model
Running a circuit is like **polling voters**. The statevector is the hidden true split; each shot asks one random voter. More shots tighten the poll; a seed replays the same voters.

```
true P('1') = 0.5 (hidden)
shots=100   ──▶ 40 … 60 ones   (~95% of runs)
shots=10000 ──▶ 4902 … 5098
```

## How it works
1. **Shots draw from a fixed distribution.** The statevector fixes the probabilities; each shot draws one outcome independently, and count ÷ shots estimates P → see lab step 1.
2. **Error shrinks like 1/√shots.** The standard error is √(p(1−p)/N): 0.0500 at 100 shots, 0.0050 at 10000. Lab 03's numpy check printed 487 ones for 1000 shots, inside the 95% range of 469–531 (from `research/concepts_worked_examples.py`) → see lab step 2.
3. **A seed replays draws.** The same seed and circuit give identical counts in one simulator; it fixes the sampling, not the accuracy → see lab step 3.

## Common mistakes
- Asserting exact counts without a seed instead of using a tolerance (this repo uses 5σ).
- Assuming seed 42 gives the same counts in Qiskit and Cirq; each simulator has its own random number generator.
- Using 10 shots and reading 6/4 as a bias. It is normal noise.
