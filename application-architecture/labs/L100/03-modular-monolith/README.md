# Lab 03 – Modular monolith boundaries

One deployable package `library` with two modules, `catalog` and `loans`. Each module's
public interface is its `__init__.py`; everything under `<module>/internal/` is private.
`check_boundaries.py` is a fitness function that fails when one module imports another
module's internals.

## Files
| File | Purpose |
|---|---|
| `library/catalog/__init__.py` | Catalog public interface: `is_available`, `set_on_loan` |
| `library/catalog/internal/store.py` | Catalog private data |
| `library/loans/__init__.py` | Loans public interface: `borrow`, `give_back` |
| `library/loans/internal/rules.py` | Loan rules; calls catalog only via `library.catalog` |
| `check_boundaries.py` | AST-based import rule check (exit 1 on violation) |
| `test_boundaries.py` | Rule check on real code + synthetic bad imports + modules working together |
| `try_it.py` | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |

## Run
```bash
cd labs/L100/03-modular-monolith        # Windows: cd labs\L100\03-modular-monolith
python check_boundaries.py
python -m unittest -v
```
See the rule fail (then remove the file again):
```bash
# Mac mini (zsh)
printf 'from library.catalog.internal.store import BOOKS\n' > library/loans/shortcut.py
python check_boundaries.py; echo "exit=$?"
rm library/loans/shortcut.py
```
```powershell
# Windows PC (PowerShell)
Set-Content library\loans\shortcut.py 'from library.catalog.internal.store import BOOKS'
python check_boundaries.py; "exit=$LASTEXITCODE"
Remove-Item library\loans\shortcut.py
```
**Path separators:** the checker builds module names from `Path.parts` and prints `relative.as_posix()`,
so it finds `library\loans\shortcut.py` on Windows and reports `library/loans/shortcut.py` on every OS
(`CrossPlatformPathTest` checks a `PureWindowsPath` on any machine).

## Expected output (observed 2026-10-28, Python 3.12.15)
```
checked 7 files: 0 boundary violation(s)
```
```
test_absolute_import_of_other_internals_is_caught (test_boundaries.BoundaryRuleTest.test_absolute_import_of_other_internals_is_caught) ... ok
test_importing_internal_as_name_is_caught (test_boundaries.BoundaryRuleTest.test_importing_internal_as_name_is_caught) ... ok
test_public_interface_and_own_internals_are_allowed (test_boundaries.BoundaryRuleTest.test_public_interface_and_own_internals_are_allowed) ... ok
test_real_code_has_no_violations (test_boundaries.BoundaryRuleTest.test_real_code_has_no_violations) ... ok
test_relative_import_of_other_internals_is_caught (test_boundaries.BoundaryRuleTest.test_relative_import_of_other_internals_is_caught) ... ok
test_reports_use_forward_slashes (test_boundaries.CrossPlatformPathTest.test_reports_use_forward_slashes) ... ok
test_windows_and_posix_paths_give_the_same_package (test_boundaries.CrossPlatformPathTest.test_windows_and_posix_paths_give_the_same_package) ... ok
test_borrow_and_return_through_public_interfaces (test_boundaries.ModulesWorkTogetherTest.test_borrow_and_return_through_public_interfaces) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.035s

OK
```
With the temporary `shortcut.py` (exit code 1):
```
VIOLATION library/loans/shortcut.py:1 'loans' imports internals of 'catalog' (library.catalog.internal.store)
checked 8 files: 1 boundary violation(s)
```

## Same idea in maintained tools
- Python: import-linter `forbidden` / `independence` / `layers` contracts (`lint-imports`).
- Java: ArchUnit rules in a unit test; Spring Modulith `ApplicationModules.of(...).verify()`.
- JavaScript/TypeScript: dependency-cruiser `forbidden` rules.

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] check_boundaries.py -> exit 1
    VIOLATION library/loans/shortcut.py:1 'loans' imports internals of 'catalog' (library.catalog.internal)
    checked 8 files: 1 boundary violation(s)
[1] python -m unittest -> exit 1; FAILED (failures=1)
    FAIL: test_real_code_has_no_violations (test_boundaries.BoundaryRuleTest.test_real_code_has_no_violations)
[2] importlib.import_module(...) -> exit 0; checked 8 files: 0 boundary violation(s)
```

## Troubleshooting
| Symptom | Action |
|---|---|
| `ModuleNotFoundError: library` in tests | Run from this lab folder so `library/` is on the import path. |
| Checker misses an import done inside a function or via `importlib` | AST scanning sees all `import` statements (including nested ones) but not dynamic `importlib.import_module("...")` strings; keep imports static. |
| Windows: package names like `library\loans`, or no violations found | Build module names from `Path.parts` and print `relative.as_posix()`; never split `str(path)` on `/`. `CrossPlatformPathTest` covers this. |
