**Concept: Hexagonal architecture (ports and adapters)**

## Why it matters
Library Loans now needs a command-line tool for the front desk, next to the HTTP API. In a layered
design the rules sit between HTTP above and SQL below, so each new entry point copies a little logic.
Ports and adapters put the rules in the middle and treat every technology as a plug.

## Mental model
The hexagon is a games console. Ports are its sockets, and the console defines their shape. Adapters
are cables: a controller drives the console; a screen or a memory card is driven by it.

```
HTTP adapter ─┐                    ┌─► memory adapter
              ├─► ForManagingLoans │
CLI adapter  ─┘   [ LoanService ] ─┴─► ForStoringLoans ─► SQLite adapter
```

## How it works
1. **Ports belong to the hexagon.** `ports.py` declares `ForStoringLoans` and `ForManagingLoans` as
   `typing.Protocol` interfaces named after a purpose, not a technology → see lab step 1
2. **Driven adapters implement a port.** The memory and SQLite stores provide the same four methods,
   and `app.py` picks one in a single line → see lab step 2
3. **Driving adapters call a port.** HTTP and the CLI translate requests into `borrow`/`give_back`
   and translate rule errors into a status code (409) or an exit code (2) → see lab step 3
4. **A fitness test protects the direction.** `domain.py` may import ports and the standard library
   only; adapters never import each other → see lab step 4

**Worked example** (`research/L200_concept_examples.py`): `domain.py` imports only
`['dataclasses', 'ports']`. The same two CLI calls give exit codes 0 and then 2 ("book b1 is already
on loan") on both the memory and the SQLite adapter.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Two or more entry points or stores, now or soon | A small CRUD app with one UI and one database |
| You want fast domain tests with in-memory adapters | The "domain" is just data mapping with no rules |
| Infrastructure is likely to change (database, queue, API style) | Indirection would double the code of a throw-away tool |

## Common mistakes
- Naming ports after technologies (`SqlRepository`), which pulls the database into the hexagon.
- Letting the domain return HTTP status codes or SQL rows instead of domain objects and errors.
- Assuming Python checks a `Protocol` at runtime: a half-built adapter fails only when the missing
  method is called. Contract tests catch it earlier.
