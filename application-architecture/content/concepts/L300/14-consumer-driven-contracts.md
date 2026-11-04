**Concept: Consumer-driven contract testing**

## Why it matters
The catalogue team renames `title` to `name` and updates its own tests, which pass. Library Loans' unit
tests use a hand-written stub that still returns `title`, so they pass too. The first time the two real
services meet is in production: `KeyError: 'title'`. End-to-end tests would catch this, but they are
slow and need both services deployed together. Contract tests catch it in each team's own build.

## Mental model
The consumer writes a shopping list: "when I ask for book b1, I need `title` (a string) and `available`
(a boolean)". The provider's build checks the shelves against every list it has received. Extra items on
the shelf are fine. A missing item on someone's list breaks the provider's build, not production.

```
consumer test ─► mock provider (serves the examples) ─► contracts/loans-service--catalogue-service.json
                                                                   │ in the repo, versioned
provider build ─► set state "book b1 exists" ─► replay request ─► compare status + body (matchers)
```

## How it works
1. **Contract by example.** The consumer test declares interactions (state, request, expected response)
   and runs the REAL client against a mock that serves them. The mock fails if an interaction was never
   used, so the contract only holds what the client really does → see lab step 1
2. **Matchers, not values.** `like("Dune")` means "any string". The consumer pins what it relies on
   (`id` is exactly "b1") and stays loose on the rest → see lab step 1
3. **Provider states.** Before each interaction the verifier tells the provider which data to set up
   ("book b1 exists", "no books") through a test-only endpoint → see lab step 2
4. **Verification compares the body.** Required keys must exist and `like` fields must keep their JSON
   type. Extra keys are allowed (tolerant reader) → see lab step 4
5. **Versioned contracts.** The file records `consumerVersion` and lives in the repo. Pact adds a broker
   and `can-i-deploy`, which checks which consumer and provider versions were verified together
   → see lab step 5

**Worked example** (`research/L300_concept_examples.py`): with the rename, the provider unit test and the
consumer stub test both PASS, and the consumer in production fails with `KeyError: 'title'`. The
status-only verifier PASSES, because the status is still 200. The body verifier FAILS with
`a request for an existing book: $.title: missing (the consumer reads it)`. When the provider adds
`isbn` and returns another title, verification still passes.

## Failure modes
- **Stub drift:** hand-written stubs encode what the consumer believes, not what the provider does.
- **Over-specified contract:** exact values everywhere make every harmless provider change "break" the
  contract, so teams start ignoring it.
- **Verifier too weak:** checking status codes only, as in the base lab, passes renamed and retyped fields.
- **Unverified pact in the pipeline:** the provider deploys without checking the newest consumer
  contracts. In Pact, `can-i-deploy` gates this.

## Common mistakes
- Writing the contract by hand instead of generating it from the consumer's tests.
- Putting business rules into contracts. They check shape and protocol; the provider's own tests check
  behaviour.
- Testing only the happy path. Add the 404 interaction, because consumers depend on errors too.
