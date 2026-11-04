**Concept: parse, validate, retry – trust only checked data**

## Why it matters
An extraction job writes model output into a database. One reply arrives as "Sure! Here is the JSON: ```json …```", another has `"age": "34"`. The first crashes the job; the second silently corrupts a column.

## Mental model
Treat model output like an untrusted web form: the schema is the form definition, your validator is the server-side check, a retry is "please correct the highlighted fields".

```
text ─► json.loads ─fail─► retry with the error ─┐ (max N)
           │ ok                                   │
           ▼                                      │
        validate ───────────fail──────────────────┘
           │ ok ─► use the dict
```

## How it works
1. **Parse strictly** with `json.loads`. Prose or fences fail at once: `Expecting value: line 1 column 1 (char 0)`. → see lab step 2
2. **Validate in code and retry with feedback.** Required keys, no extra keys, types, ranges; append the bad reply plus the exact error and ask again (max N). `validate({"age": "34", …})` → `['age must be an integer 0-150']`; note `isinstance(True, int)` is `True`, so the lab checks `type(age) is int` (values from `research/concept_examples.py`). → see lab step 2
3. **Constrain at the server when available:** `response_format` with a JSON Schema (Ollama, llama.cpp) makes attempt 1 succeed. Constraint reduces retries; it does not replace validation. → see lab step 2

## Common mistakes
- Stripping code fences with a regex and skipping validation.
- Retrying forever – cap attempts and surface the failure.
- Assuming schema-valid means correct: a valid `age` can still be the wrong person's age.
