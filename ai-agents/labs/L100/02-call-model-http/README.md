# 02 – Call a model over HTTP

`call_model.py` (requests) and `call_model_urllib.py` (stdlib only) POST to `/v1/chat/completions` and read `choices[0].message.content`.

## Run (fake server – validated)
```bash
python ../01-setup/fake_model_server.py --port 8765        # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python call_model.py   # terminal 2
# Windows PowerShell: $env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python call_model.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
reply        : Hello from fake-model! You said: 'Say hello in one short sentence.'
finish_reason: stop
usage        : {"prompt_tokens": 6, "completion_tokens": 11, "total_tokens": 17}
top-level keys: ['choices', 'created', 'id', 'model', 'object', 'usage']
```
`call_model_urllib.py` prints `reply: Hello from fake-model! You said: 'Say hello in one short sentence.'`. Tests: `Ran 6 tests ... OK`.

## Optional manual run – real model
`python call_model.py` with Ollama running (defaults point at `http://localhost:11434/v1`, `qwen2.5:1.5b`).
The reply text differs; the keys and `finish_reason: stop` are the same. Token counts are real tokens, not words.

## Same call with curl (not run here – needs a running server)
```bash
curl $LOCAL_MODEL_URL/chat/completions -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:1.5b", "messages": [{"role": "user", "content": "Say hello"}]}'
```

## Troubleshooting
| Symptom | Action |
|---|---|
| `requests.exceptions.ReadTimeout` | First call loads the model on CPU; raise `timeout` or retry. |
| `HTTPError: 404` | `LOCAL_MODEL_URL` must end in `/v1`; the model name must exist (`ollama list`). |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_02` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Send 'What did I just say?' alone, then again after the 'Hi' turn and its reply; compare usage.prompt_tokens. | alone: prompt_tokens=5; with history (3 messages): prompt_tokens=12 - history is resent every call. |
| Change the only message's role from 'user' to 'system' and call chat(). | requests.HTTPError: HTTP 400 - at least one 'user' message is required. |
