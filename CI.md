# CI for the knowledge base

GitHub only runs workflows in `<repo root>/.github/workflows/`, so topic `labs.yml` files never run as placed (F01). The root workflows are generated copies for `kb/` as root.

## Create the repository from kb/

```bash
cd kb
git init -b main
git add . && git commit -m "Knowledge base"
gh repo create <owner>/<name> --private --source . --push
```

Allow Actions under Settings → Actions.

## What runs

| Workflow | Triggers | Jobs |
|---|---|---|
| `<topic>.yml` (7) | push/PR touching `<topic>/**`, `shared/**` or the workflow; manual (except application-architecture) | Every job in the topic's `labs.yml` (L100–L300), inside `<topic>/`, on the ubuntu/macos/windows matrix. L300 adds promptfoo and OpenTelemetry (ai-agents), Pact and k6 (application-architecture), OpenBao and minisign (cryptography), OpenTelemetry (distributed-systems), Mosquitto, Rust firmware and Renode (microbit), Mitiq/PennyLane (quantum), SALib/FMPy (simulation). Container jobs run on Linux only. |
| `shared.yml` | `shared/**` | `shared/local_agent` tests on 3 OSes |

## Keeping root workflows in sync

Don't edit generated files. After changing a topic's `labs.yml` (e.g. a new level), run:

```bash
python tools/sync_root_ci.py           # regenerate + path check
python tools/sync_root_ci.py --check   # write nothing; fail if stale or a path is missing
```

The script adds `paths` filters and makes every working directory and artifact path relative to `kb/`. For ai-agents, it renames `BASE_URL`/`MODEL` to `LOCAL_MODEL_URL`/`LOCAL_MODEL`. Its path check expands matrices and confirms every referenced script, requirements file and directory exists.

## After a green run: flip `platforms`

1. Check that the macos-latest and windows-latest jobs passed without unexpected skips.
2. In `<topic>/content/L*.json`, set each covered lesson's `platforms` value to `"tested-ci"` for each OS that passed. Add the run URL to `validation.how`.
3. Paste real output from artifacts (quantum `observed-*.txt`, microbit traces) into the lab READMEs. For quantum, also update `validation.status`.
4. Otherwise keep `expected`.
