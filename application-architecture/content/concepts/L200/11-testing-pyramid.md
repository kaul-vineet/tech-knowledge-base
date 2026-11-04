**Concept: The testing pyramid, measured**

## Why it matters
A suite made only of end-to-end tests is slow, flaky, and vague about what broke. A suite made only of
unit tests with fakes misses bugs in the adapters. The pyramid balances the two: many fast tests where
the rules live, fewer and slower tests at each boundary.

## Mental model
The pyramid is a building inspection. Inspectors check each brick quickly (unit), test every joint with
the real material (integration), and walk through the finished house once (end to end).

```
        /\        e2e: 1 journey over HTTP + SQLite file      slowest
       /  \
      /----\      integration: store contract vs real SQLite (PostgreSQL in CI)
     /      \
    /--------\    unit: 8 domain tests with an in-memory fake  fastest
```

## How it works
1. **Layers by name.** `test_unit*`, `test_integration*` and `test_e2e*` files form the layers, so
   `pyramid.py` can run and count each one → see lab step 1
2. **Measure, don't guess.** `TimedResult` times every test with `time.perf_counter()`, and
   `pyramid.py` checks that unit ≥ integration ≥ e2e ≥ 1 → see lab step 2
3. **One integration point at a time.** The same contract tests run against SQLite here and against
   PostgreSQL through Testcontainers in CI → see lab steps 3–4
4. **Each layer catches different bugs.** A type bug in the SQLite adapter fails only an integration
   test; a wrong HTTP status fails only the e2e test → see lab step 2

**Worked example** (`research/L200_concept_examples.py`, this host): unit 8 tests, mean 0.04 ms;
integration 4 tests, mean 201 ms; e2e 1 test, mean 1227 ms. The absolute numbers vary between runs,
but each layer's order of magnitude holds.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Rules are rich enough to unit test on their own | The code is mostly glue (then lean on integration tests) |
| You can run real dependencies locally or in containers | A shared test database makes tests depend on each other |
| CI time matters and feedback should take seconds | You would only count tests and ignore what each one covers |

## Common mistakes
- An "ice-cream cone": many UI/e2e tests and few unit tests.
- Integration tests against an in-memory stand-in for the database, which miss real type and SQL
  differences.
- Repeating the same rule check at every layer instead of once, at the lowest layer that can see it.
