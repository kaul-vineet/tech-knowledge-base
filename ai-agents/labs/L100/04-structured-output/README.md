# 04 – Structured output

Ask for JSON matching `SCHEMA`, parse with `json.loads`, validate with plain code, and retry with the error message if invalid.
Second mode sends `response_format: {"type": "json_schema", ...}` so the server constrains the output.

## Run (fake server – validated)
```bash
python ../01-setup/fake_model_server.py --port 8765        # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python structured_output.py
# Windows PowerShell: $env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python structured_output.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
prompt-only (parse + validate + retry):
  attempt 1: ['not valid JSON (Expecting value)']
  attempt 2: OK
  result: ({'name': 'Maria', 'age': 34, 'city': 'Lisbon'}, 2)
with response_format json_schema:
  attempt 1: OK
  result: ({'name': 'Maria', 'age': 34, 'city': 'Lisbon'}, 1)
```
Attempt 1 fails on purpose: the fake wraps the JSON in prose and a ```` ```json ```` fence, a common real failure. Tests: `Ran 7 tests ... OK`.

## Optional manual run – real model
`python structured_output.py` against Ollama. Ollama documents structured outputs via its native `format` field
(`/api/chat`) and via `response_format` on its `/v1` chat-completions API. With `response_format` expect 1 attempt;
prompt-only may take 1–2. Keep the validator either way – a valid shape can still hold wrong values.

## Troubleshooting
| Symptom | Action |
|---|---|
| `ValueError: no valid JSON after 3 attempts` | Lower temperature, put the schema in the system message, or use `response_format`. |
| HTTP 400 mentioning `response_format` | That server lacks `json_schema`; try `{"type": "json_object"}` or prompt-only mode. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_04` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Call extract_person(text, max_attempts=1) in prompt-only mode. | ValueError: no valid JSON after 1 attempts - the fenced first reply is never retried. |
| Remove 'she is 34' from the input text. | attempt 1: ['not valid JSON (Expecting value)']; attempt 2: ['age must be an integer 0-150']; attempt 3: same -> ValueError. Nothing invents the missing value. |
