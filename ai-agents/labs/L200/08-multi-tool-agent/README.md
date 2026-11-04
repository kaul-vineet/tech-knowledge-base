# 08 – Agents with several tools

The model chooses among tools by their descriptions; your code checks each call against a schema and turns every failure into a message the model can act on.

## Run (fake server – validated)
```bash
python ../../L100/01-setup/fake_model_server.py --port 8765   # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python multi_tool_agent.py
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\..\L100\01-setup\fake_model_server.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python multi_tool_agent.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
step 1: calculator({"expression": "12*7"}) -> 84
step 2: get_weather({"city": "Paris", "unit": "kelvin"}) -> error: invalid arguments: $.unit: 'kelvin' is not one of ['celsius', 'fahrenheit']
step 3: get_weather({"city": "Paris"}) -> 18 C
step 4: search_docs({"query": "context window", "top_k": 50}) -> error: invalid arguments: $.top_k: 50 is greater than the maximum of 5
step 5: search_docs({"query": "context window"}) -> The context window limits how many tokens one request can hold. | Embeddings turn text into vectors for similarity search.
step 6: final -> Final answer: 12*7 = 84; get_weather(city=Paris) = 18 C; search_docs(query=context window) = The context window limits how many tokens one request can hold. | Embeddings turn text into vectors for similarity search.
{'answer': 'Final answer: 12*7 = 84; get_weather(city=Paris) = 18 C; search_docs(query=context window) = The context window limits how many tokens one request can hold. | Embeddings turn text into vectors for similarity search.', 'steps': 6, 'stopped': 'final_answer'}
```
Tests: `Ran 12 tests ... OK (skipped=1)`.

## Agent assist (the model proposes, code decides)
The model drafts a JSON Schema for a new tool (convert_temperature) from a short spec.

Check: Code parses the JSON, requires type object + properties, forces additionalProperties: false, and runs 1 good and 4 bad example arguments through schema_check.validate; any wrong verdict rejects the draft.

### Observed with the fake server (2026-10-28)
```
draft: {"type": "object", "properties": {"value": {"type": "number"}, "to": {"type": "string", "enum": ["celsius", "fahrenheit"]}}, "required": ["value", "to"]}
accepted ['added additionalProperties: false']
```
Real model: A real model may add descriptions, use 'integer', or forget required fields; the example arguments decide, not the model's confidence.

## Build task
Add a 4th tool, get_time, that takes no arguments; the model must be able to choose it alongside the calculator.

Hints:
- Use agent.tool(fn, description, {}) - empty properties plus additionalProperties: false accepts only {}.
- The fake plans get_time when the user text contains the word 'time'.
- Check that {"tz": "UTC"} is rejected.

Solution: `solution/get_time_tool.py` · proof: `python -m unittest -v test_build_task`

## Equivalents
- python-jsonschema 4.26.0: Draft202012Validator(schema).is_valid(args) (test_jsonschema_equivalent.py, pending-ci); ajv in Node
- Pydantic: model_json_schema() generates the schema and model_validate() checks the arguments
- MCP: the same JSON Schema travels as a tool's inputSchema (lesson 10)
- Frameworks (LangGraph ToolNode, smolagents, LlamaIndex agents): registry + validation + error messages behind decorators

## Optional steps (not run in the sandbox)
**cross-check with python-jsonschema** – The full validator must give the same verdict as schema_check.py on 11 cases.
```bash
python -m pip install jsonschema==4.26.0
python -m unittest -v test_jsonschema_equivalent
```
```powershell
python -m pip install jsonschema==4.26.0
python -m unittest -v test_jsonschema_equivalent
```
Expected: test_same_verdicts ... ok

**run against the real local model** – ollama pull qwen2.5:1.5b && python multi_tool_agent.py (defaults: http://localhost:11434/v1)
Expected: Tool calls with model-chosen arguments; invalid ones come back as error messages

## Troubleshooting
| Symptom | Action |
|---|---|
| Model keeps sending the same invalid argument | Make the error text name the field and the allowed values; keep max_steps as the backstop. |
| Model picks the wrong tool | Rewrite descriptions so each tool's purpose is distinct; fewer, clearer tools beat many similar ones. |
| TypeError: unexpected keyword argument | A field reached the function without validation - add additionalProperties: false. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_08` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Ask for the weather 'in fahrenheit' instead of 'in kelvin'. | step 2: get_weather({"city": "Paris", "unit": "fahrenheit"}) -> 64 F / steps: 5 - one retry fewer. |
| Raise search_docs' top_k maximum from 5 to 50 and call it with top_k 50. | All 3 notes come back joined by ' | ' - with real data that is how a model pulls far more text (and tokens) than intended. |
