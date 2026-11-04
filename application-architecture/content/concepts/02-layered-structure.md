**Concept: layers – presentation, service, repository**

## Why it matters
The loan limit is checked inside the HTTP handler and the SQL is copied into three handlers. Then the
library wants SQLite, and every rule must be changed in several places.
Layers give each concern one home.

## Mental model
A restaurant: the waiter (presentation) never cooks, the chef (service) never talks to guests, and
the pantry (repository) can be swapped without retraining the chef.

```
HTTP ─► handler.py   JSON ⇄ calls, domain errors ⇄ 400/404/409
          ▼
        service.py   rules: one loan per book, max N per member
          ▼
        InMemoryLoanRepository | SqliteLoanRepository   (chosen once in app.py)
```

## How it works
1. **The repository hides storage.** Both repositories expose `add/get/active/mark_returned`, and
   `build_service()` is the only line that picks one → see lab step 3
2. **The service owns the rules.** It raises `LoanLimitReached`; only the handler maps that to 409, so
   the same rule tests run against both repositories without HTTP → see lab step 4
3. **Dependencies point down.** `service.py` imports neither `http.server` nor `sqlite3`, and a test
   fails if it does → see lab step 5

**Worked example** (SQLite, limit 3, computed by `research/concept_examples.py`): `m1` borrows b1–b3
(loan ids 1–3); b4 raises `LoanLimitReached`; after loan 2 is returned, b4 becomes loan 4.

## Common mistakes
- Putting "just one `if`" rule in the handler, where it cannot be tested without HTTP.
- Letting the service return HTTP status codes or SQL rows.
- Treating layers as separate servers: they are "logical layers not physical tiers" (Fowler).
