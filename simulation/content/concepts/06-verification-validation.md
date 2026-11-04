**Concept: verification vs validation**

## Why it matters
Your queue simulation says the new checkout needs two baristas. Before money is spent, someone will ask: "Is the code correct, and is the model right for this shop?" Those are two different questions.

## Mental model
Verification: did we build the model right? Validation: did we build the right model for the question?

```
real system ──(model)──> conceptual model ──(code)──> program
     ▲                        verification: unit tests, traces, seeds
     └── validation: compare outputs with data or a trusted formula
```

## How it works
1. **Verify the rules and reproducibility:** unit-test the model rule with hand-computed cases (next_wait(0, 3, 1) = 2) and check that the same seed gives the same output → see lab step 5.
2. **Validate against a reference with replications:** 10 independent seeds, warm-up dropped, 95% t-interval. 4.046 ± 0.195 min contains the M/M/1 value 4.000 → see lab step 3.
3. **Sensitivity to one parameter:** sweep the arrival rate. Waits go 1.0 → 9.0 min as utilisation goes 0.5 → 0.9, matching the formula's steep curve → see lab step 4.

## Common mistakes
- Calling a model "validated" because its tests pass; tests only verify.
- Comparing one long, autocorrelated run to a formula instead of using replications.
- Validating at one load level, then using the model at another.
