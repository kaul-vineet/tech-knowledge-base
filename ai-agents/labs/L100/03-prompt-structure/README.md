# 03 – Prompt structure

Same review, three message layouts: (A) user-only, (B) system rules + user data, (C) system + few-shot examples + `<review>` delimiters.

## Run (fake server – validated)
```bash
python ../01-setup/fake_model_server.py --port 8765        # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python prompt_structure.py
# Windows PowerShell: $env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python prompt_structure.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
[A user-only] -> Sure! Reading the review carefully, I would say the overall sentiment is negative. Let me know if you want a more detailed analysis.
[B system+user] -> negative
[C few-shot+delimiters] -> NEGATIVE
```
Tests: `Ran 5 tests ... OK`. The fake server *imitates* typical behaviour with fixed rules (see `simulatorVsReal`).

## Optional manual run – real model
`python prompt_structure.py` against Ollama. Expect A to be a sentence, B mostly a single label, C a label in the
examples' format (`NEGATIVE`). Small models do not always comply – run it 2–3 times and compare.

## Troubleshooting
| Symptom | Action |
|---|---|
| B/C return a sentence, not one word | Keep `temperature: 0`, add one more example, or validate the label in code (lesson 4). |
| Output changes between runs | Real models are sampled; use `temperature: 0` and a fixed `seed` where supported. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_03` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| In layout C, change the example answers to lowercase ('positive', 'negative'). | negative - the label follows the examples' casing. |
| Delete the system message from layout C, keep the examples. | Hello from fake-model! You said: '<review>The battery died after two days and support never answered my emails.</r' - the task lived only in the system message. |
