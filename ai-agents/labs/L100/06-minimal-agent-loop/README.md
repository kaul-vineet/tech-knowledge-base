# 06 – A minimal agent loop

`run_agent()` repeats model → tool calls → results → model until the model answers without tool calls (stop condition)
or `max_steps` is used up (budget). Every step is logged. Tools live in a registry; a tool flagged "needs approval"
only runs if the `approve` callback returns True (default: deny).

## Run (fake server – validated)
```bash
python ../01-setup/fake_model_server.py --port 8765        # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python agent_loop.py
# Windows PowerShell: $env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python agent_loop.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
== budget 5 ==
step 1: tool  -> calculator({'expression': '17*23'}) = 391
step 2: tool  -> calculator({'expression': '(120-20)/4'}) = 25.0
step 3: final -> Final answer: 17*23 = 391; (120-20)/4 = 25.0
{'answer': 'Final answer: 17*23 = 391; (120-20)/4 = 25.0', 'steps': 3, 'stopped': 'final_answer'}
== budget 1 ==
step 1: tool  -> calculator({'expression': '17*23'}) = 391
stopped: max_steps=1 reached without a final answer
{'answer': None, 'steps': 1, 'stopped': 'max_steps'}
```
Tests: `Ran 8 tests ... OK` (incl. approval gate, unknown tool, tool error, unsafe expression rejected).

## Optional manual run – real model
`python agent_loop.py` against Ollama. A real model may request both calculations in one step (parallel tool calls),
so expect 2–3 steps; the numbers 391 and 25.0 come from the calculator, not the model.

## Troubleshooting
| Symptom | Action |
|---|---|
| Always `stopped: max_steps` | Model keeps calling tools – check tool results are sent back; raise the budget slightly; tighten the system prompt. |
| Model does maths itself (no tool step) | Small models skip tools sometimes; keep the "use the calculator" instruction and verify results in code. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_06` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Run run_agent(task, max_steps=2). | {'answer': None, 'steps': 2, 'stopped': 'max_steps'} - the final answer never arrived. |
| Set the calculator's 'needs approval' flag to True and keep the default approver. | step 3: final -> Final answer: 17*23 = error: action denied by human reviewer; (120-20)/4 = error: action denied by human reviewer - nothing ran; the loop still ended. |
