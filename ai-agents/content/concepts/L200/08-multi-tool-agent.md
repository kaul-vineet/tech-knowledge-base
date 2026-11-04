**Concept: several tools – the model chooses, a schema decides what may run**

## Why it matters
With one tool the model only decides *whether* to call it. With three or four it must also pick *which* one and fill in arguments. Wrong picks and invented arguments are normal; code must reject bad calls and say why.

## Mental model
A help desk with forms: each tool is a form with required fields and allowed values. The model fills in a form; a clerk (your validator) checks it before anything happens and returns rejected forms with a note.

```
model ─► tool_call(name, JSON args)
           │ known name?  ── no ─► "error: unknown tool"
           │ JSON parses? ── no ─► "error: not valid JSON"
           │ schema ok?   ── no ─► "error: invalid arguments: $.field ..."
           ▼
        run tool ─► result or "error: ..." ─► back to the model
```

## How it works
1. **Describe each tool** with a name, a one-line description and a JSON Schema for its arguments; `additionalProperties: false` rejects invented fields. The model chooses from these descriptions. → see lab step 2
2. **Validate before running.** Types, `enum`, `minimum`/`maximum` and `maxLength` are checked in code. Worked example: `get_weather` with `unit: "kelvin"` returns `error: invalid arguments: $.unit: 'kelvin' is not one of ['celsius', 'fahrenheit']`; `top_k: 50` returns `... 50 is greater than the maximum of 5`. → see lab step 2
3. **Errors are results.** Every failure becomes a tool message, so the model can correct itself: the demo needs 6 steps – 3 tools, 2 rejected calls, 2 retries, 1 final answer. MCP agrees: input-validation errors belong in the tool result. → see lab step 3
4. **The registry is the allow-list.** Only registered names run, whatever the model writes. → see lab step 3
5. **Same rules everywhere.** A full validator (python-jsonschema, ajv) must agree with the small one. → see lab step 5

## Trade-offs
| Use when | Avoid when |
|---|---|
| Steps depend on the user's request | One fixed sequence always works – call functions directly |
| Tools have clear, distinct purposes | Many near-duplicate tools – the model confuses them |
| Arguments can be checked by a schema | Arguments are free text you cannot validate |

## Common mistakes
- Running the tool first and validating afterwards (or never).
- Raising exceptions on bad arguments instead of returning a message the model can act on.
- Vague, overlapping tool descriptions – the model's only guide to choosing.
