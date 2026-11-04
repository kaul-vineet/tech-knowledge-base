**Concept: the L100 toolchain – what each piece does**

## Why it matters
You clone the repo, run one command and get `OK` or a failure. Without that loop you cannot tell
whether a change broke the architecture rules that later lessons add.

## Mental model
A workshop: one workbench (Python 3.12), one gauge (`unittest`) and labelled drawers (lab folders).

```
cd labs/L100/NN-x && python -m unittest
   └─► discovers test*.py HERE ─► imports sibling lab modules (stdlib only)
CI (labs.yml): same command per lab; diagrams are rendered only in CI
```

## How it works
1. **Interpreter.** Python 3.12 gets security fixes until 2028-10, so it is a stable target.
   `check_env.py` exits 1 on an older one or a missing module → see lab step 2
2. **Discovery.** `python -m unittest` imports `test*.py` from the current folder and runs every
   `test*` method of each `TestCase`. That is why you `cd` into the lab first → see lab step 3
3. **One runner, fresh interpreters.** `run_all_labs.py` starts a new Python in each lab folder,
   so the two `app.py` files never clash → see lab step 4

**Worked example** (computed by `research/concept_examples.py`): the six labs run 6, 12, 8, 4, 9
and 16 tests, 55 in total.

## Common mistakes
- Running `python -m unittest` from the repo root: discovery finds nothing or imports the wrong `app.py`.
- Naming a test file `checks_test.py`: the default pattern `test*.py` skips it.
- Assuming mermaid-cli or Docker is required. Only CI needs them, to render the lesson 6 diagrams.
