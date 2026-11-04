**Concept: tool calling – the model asks, your code acts**

## Why it matters
A user asks "What time is it?" The model has no clock, so it guesses. Tool calling lets it say "I need `get_time`" while your program supplies the real value – and decides whether to run it.

## Mental model
A colleague on the phone who cannot touch your computer: they ask you to run `get_time`; you check, run it and read back the result, quoting which request it answers (`tool_call_id`).

```
you ──messages + tools──────────────► model
you ◄── tool_calls[id=call_1, get_time, "{}"]
you: allowed? → run → "2026-10-28T06:00:00+00:00"
you ──… + assistant turn + tool(call_1) ──► model
you ◄── final answer (finish_reason: stop)
```

## How it works
1. **Declare tools** as `{"type": "function", "function": {name, description, parameters}}`; `parameters` is a JSON Schema. → see lab step 2
2. **The model replies with `tool_calls`:** each has an `id`, `function.name` and `function.arguments` – a JSON *string* on `/v1` (`"{}"` here; Ollama's native API sends an object). `finish_reason` becomes `tool_calls`. → see lab step 2
3. **Your code dispatches and replies:** check an allow-list, run, then append the assistant turn and one `{"role": "tool", "tool_call_id": …}` per call. The second request carries **3** messages; a wrong id gets **HTTP 400** from the fake (from `research/concept_examples.py`). → see lab step 2

## Common mistakes
- Executing whatever name the model returns (`globals()[name]`) instead of an allow-list.
- Forgetting to append the assistant `tool_calls` turn before the tool result.
- Giving a read-only assistant a tool that can delete or send.
