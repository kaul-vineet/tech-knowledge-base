**Concept: API-first contracts with OpenAPI**

## Why it matters
The mobile team builds against "`POST /loans` returns the loan". The server team later returns 422
instead of 409 and renames `memberId`. Both sides pass their own tests and production breaks. A
shared, machine-checked contract catches this before release.

## Mental model
The contract is a menu with photos, printed before cooking starts. The contract test is the
inspector who compares each plate with its photo.

```
openapi.json ──► server.py (implements it)
     │                 │ real responses
     └──► contract_check.py ──► test_contract.py ──► pass / fail
```

## How it works
1. **The document.** `openapi` (spec version `3.1.2`), `info` (title, version) and `paths`. Each
   operation lists its `responses` by status code, with a schema per media type → see lab step 1
2. **Schemas.** `required` lists fields that must be present; `type` and `enum` constrain values
   (JSON Schema 2020-12). Each real response is checked → see lab step 3
3. **Contract test.** Call every operation, check that the status is declared and the body matches,
   and assert that every declared response was exercised. An undeclared 422 fails → see lab step 4

**Worked example** (computed by `research/concept_examples.py`): the 200 body
`{"id": "7", "bookId": "b1", "status": "lost"}` gives three problems: missing `memberId`, `id` is not
integer, and `'lost'` is not in the enum.

## Common mistakes
- Returning status codes that are not in `responses`, such as 500 or 422.
- Treating the spec as documentation that nobody tests, so it drifts.
- Confusing `openapi` (spec version) with `info.version` (your document's version).
