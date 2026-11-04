**Concept: module boundaries and fitness functions**

## Why it matters
Loans needs to know whether a book is on the shelf, so someone imports the catalog's private `BOOKS`
dict "just this once". A month later the catalog team renames it and loans breaks. Without an
enforced boundary, a module is only a folder name.

## Mental model
Two shops in one mall. Each has a counter (its public `__init__.py`) and a stockroom (`internal/`).
A guard (the fitness function) raises the alarm when anyone walks into another shop's stockroom.

```
library/catalog/__init__.py       counter: is_available(), set_on_loan()
library/catalog/internal/         stockroom (private)
library/loans/internal/rules.py ─► from library import catalog              ✔
                                ─╳ from library.catalog.internal import …    ✘ exit 1
```

## How it works
1. **One deployable, many modules.** Everything ships together, but loans talks to catalog only
   through its public interface → see lab step 5
2. **Python will not stop you, so a check must.** `check_boundaries.py` parses each file with `ast`,
   resolves relative imports (`ImportFrom.level` counts the dots) and flags any import of
   `library.<other>.internal` → see lab step 3
3. **Automate it.** The check runs in `unittest` and CI and exits 1 on a violation. That makes it a
   *fitness function*: an objective, automated check of an architectural characteristic → see lab step 2

## Common mistakes
- Making everything public "for convenience", so nothing internal is left to protect.
- Checking only absolute imports, so `from ..catalog.internal import store` slips through.
- Sharing one database table between modules: the code is separated, the data is still coupled.
