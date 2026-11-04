# 05 – Your first tool call

Declare one tool (`get_time`) in the chat-completions `tools` format, detect `tool_calls` in the reply, run the function locally,
send the result back as a `role: "tool"` message with the matching `tool_call_id`, and get the final answer.

## Run (fake server – validated)
```bash
python ../01-setup/fake_model_server.py --port 8765        # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python first_tool_call.py
# Windows PowerShell: $env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python first_tool_call.py
python -m unittest -v
```

### Expected output (observed 2026-10-28; the timestamp is your current UTC time)
```
model requested: get_time({})
tool result    : 2026-10-28T05:43:10+00:00
final answer   : Final answer: get_time() = 2026-10-28T05:43:10+00:00
```
Tests: `Ran 9 tests ... OK`.

## Optional manual run – real model
`python first_tool_call.py` against Ollama with `qwen2.5:1.5b` (listed with the `tools` capability).
Expect the same first two lines; the final sentence is phrased by the model. If no `model requested` line appears,
the model answered without the tool (it cannot know the time, so the answer will be a guess).

## Troubleshooting
| Symptom | Action |
|---|---|
| HTTP 400 on the second call | The assistant message with `tool_calls` must be appended before the `tool` message, and `tool_call_id` must match. |
| `json.JSONDecodeError` in `run_tool` | Arguments are a JSON *string* on `/v1`; some native APIs send an object – the code handles both. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_05` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Call ask('What is the capital of France?'). | No 'model requested' line; the reply comes straight back: Hello from fake-model! You said: 'What is the capital of France?' |
| Delete messages.append(reply) so the tool result is sent without the assistant tool_calls turn. | requests.HTTPError: HTTP 400 - tool message has unknown or missing 'tool_call_id'. |
