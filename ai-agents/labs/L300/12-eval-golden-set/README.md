# 12 – Evaluating agents with a golden set

A golden set is a frozen list of inputs with labelled answers; run it on every prompt or model change and gate the merge on the result, not on a few examples you happened to try.

Concept note: `../../../content/concepts/L300/12-eval-golden-set.md` · lesson object: `content/L300.json` #12

## Run (fake server – validated)
```bash
python ../fake_server_l300.py --port 8765   # terminal 1
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model   # terminal 2
python eval_gate.py; echo "exit code: $?"
python eval_gate.py --prompt prompts/v2.txt; echo "exit code: $?"
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\fake_server_l300.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"   # terminal 2
python eval_gate.py; "exit code: $LASTEXITCODE"
python eval_gate.py --prompt prompts\v2.txt; "exit code: $LASTEXITCODE"
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
v1.txt: 20/20 passed (100%)
GATE: PASS
exit code: 0
FAIL t07 (account): exact: category='other', expected 'account'
FAIL t15 (account): exact: category='other', expected 'account'
v2.txt: 18/20 passed (90%)
GATE: BLOCK - pass rate 90% < 95% | regressions vs baseline: ['t07', 't15']
exit code: 1
```
A spot check of the first three cases with v2 passes 3/3 (`test_failure_lab_spot_check_misses_the_regression`) – that is how the change would have merged.

Tests: `Ran 10 tests ... OK (skipped=1)` – the skipped test runs promptfoo (needs Node packages; CI job with `RUN_PROMPTFOO=1`).

## Failure lab
| | |
|---|---|
| Fault (seeded) | Prompt v2 ('cleanup') drops 'account' from the category list; the fake model (rule T) can then only answer 'other' for account tickets - deterministic. |
| Symptom | A three-example spot check passes 3/3; the change would merge. Full set: 18/20 (90%), t07 and t15 now 'other'. |
| Fix | Run the whole golden set in CI and gate on pass rate >= 95% AND no regressions vs the accepted baseline (exit code 1 blocks the merge). |
| Proof | test_eval_gate: test_failure_lab_spot_check_misses_the_regression (3/3 with v2) vs test_failure_lab_gate_blocks_v2 (gate names t07, t15); CLI v1 -> 0, v2 -> 1. |

## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| Exact / structural checks | Deterministic, free, fast, explainable failures | Only for answers with a single right value or shape | Classification, extraction, tool-call arguments |
| Rubric checklist in code | Partial credit without a second model; stable scores | Crude for open-ended prose; you write the criteria | Summaries and replies with checkable properties (length, mentions, forbidden words) |
| Judge model (llm-rubric) | Grades open-ended quality at scale | Cost, latency, judge bias and drift; needs calibration against humans | Free-text answers where code checks cannot express quality - pin the judge and spot-check it |

## Build task
Start from the shipped category_gate.py (unfixed: one overall pass rate, so v2 passes at 90%). Add a per-category gate: every labelled category must pass at >= 80%, so a small category cannot hide inside the overall average.

Hints:
- Group results by the labelled category (result['category']).
- Return one reason per failing category, like gate().
- Run it next to gate() in CI - it catches the collapse even without a baseline.

Your file: `category_gate.py` (shipped unfixed) · solution: `solution/category_gate.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28 – shipped file (fail-before) vs solution (pass-after):
```
BUILD_TARGET=mine  -> AssertionError: Lists differ: [] != ['account: 0/2 passed (0%) < 80%']
                      FAILED (failures=1)
solution           -> Ran 1 test ... OK
```

## Same gate with promptfoo (pending-ci)
`promptfooconfig.yaml` uses the same prompt files and the 20 cases (generated into `promptfoo_tests.jsonl` by `make_promptfoo_tests.py`); the `openai:chat:fake-model` provider points at `http://127.0.0.1:8765/v1` with `apiKeyRequired: false`.
```bash
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1                   # no usage telemetry / update check
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml --no-cache                    # expected exit 0
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml -p prompts/v2.txt --no-cache  # expected exit 100 (t07, t15)
```
In CI: one step that runs `python eval_gate.py --prompt <new prompt>` – a non-zero exit fails the job (see the topic's `.github/workflows/labs.yml`).

## Equivalents
- promptfoo (MIT): promptfooconfig.yaml with tests: file://... and assertions; `promptfoo eval` exits 100 on failures (promptfooconfig.yaml here)
- pytest/unittest parametrised over a JSONL file: the same idea without a framework (this lab)
- Hosted eval dashboards exist from model vendors; keep the golden set and the gate in your repo either way

## Optional steps (not run in the sandbox)
**the same gate with promptfoo (CI)** – make_promptfoo_tests.py turns golden.jsonl into promptfoo test cases; promptfooconfig.yaml points the openai:chat provider at the fake server (apiBaseUrl, no key). Needs Node 24 and network for npx.
```
python make_promptfoo_tests.py
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1   # no usage telemetry, no update check
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml --no-cache
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml -p prompts/v2.txt --no-cache; echo $?
```
PowerShell:
```powershell
python make_promptfoo_tests.py
$env:PROMPTFOO_DISABLE_TELEMETRY="1"; $env:PROMPTFOO_DISABLE_UPDATE="1"
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml --no-cache
npx promptfoo@0.125.1 eval -c promptfooconfig.yaml -p prompts\v2.txt --no-cache; $LASTEXITCODE
```
Expected: Pending CI: v1 exit 0; v2 exit 100 with t07 and t15 failing (the same two cases as eval_gate.py)

**real model** – Write a baseline for the real model first - a fake-server baseline means nothing for qwen2.5.
```
ollama pull qwen2.5:1.5b
python eval_gate.py --write-baseline --baseline baseline-qwen.json
python eval_gate.py --prompt prompts/v2.txt --baseline baseline-qwen.json
```
PowerShell:
```powershell
ollama pull qwen2.5:1.5b
python eval_gate.py --write-baseline --baseline baseline-qwen.json
python eval_gate.py --prompt prompts\v2.txt --baseline baseline-qwen.json
```
Expected: Scores differ from the fake; the gate compares the model against its own baseline


## Troubleshooting
| Symptom | Action |
|---|---|
| Gate fails on every run with a real model | The baseline came from the fake server; write a baseline with the real model (--write-baseline) and review it once. |
| Scores change between identical runs | Set temperature 0, pin the model tag, and keep model-graded checks out of the blocking gate until they are stable. |
| Everything passes but users still complain | Add the failing production inputs as new golden cases (with labels) - the set is stale. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_12` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Lower the bar: gate(report_v2, baseline, min_pass_rate=0.85). | ["regressions vs baseline: ['t07', 't15']"] - still blocked: the per-case regression rule does not care about the average. |
| 'Fix the test': drop the account cases from the golden set and run v2 again. | 18/18 [] - green. The gate is only as good as the set; deleting failing cases hides the bug (golden-set changes need review). |
