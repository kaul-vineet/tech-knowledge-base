**Concept: a chat completion is one stateless HTTP call**

## Why it matters
Your support bot answers the first question well, then says "I don't know what you are referring to" on the follow-up. Nothing crashed – the code did not resend the earlier messages.

## Mental model
The model is a pure function `reply = f(messages, settings)`. It keeps no session; the conversation is a list *you* own and resend every time.

```
call 1: [user:"Hi"]                              ──► assistant:"Hello!"
call 2: [user:"Hi", assistant:"Hello!", user:"What did I just say?"] ──► ...
         └──────────── you append and resend ────────────┘
```

## How it works
1. **Request:** `POST {LOCAL_MODEL_URL}/chat/completions` with `model`, `messages`, `temperature`, `max_tokens`; set a timeout and check the HTTP status. → see lab step 2
2. **Response:** text at `choices[0].message.content`; `finish_reason` says why it stopped (`stop`, `length`, `tool_calls`); `usage` counts tokens. → see lab step 2
3. **Temperature** rescales next-token scores before sampling. For logits `[2.0, 1.0, 0.1]` (computed by `research/concept_examples.py`) the top token gets **0.659** at T=1, **0.864** at T=0.5 and **0.993** at T=0.2 – so labs use `temperature: 0` for repeatable output. The same POST works from the stdlib alone. → see lab step 3

## Common mistakes
- Sending only the latest user message and expecting the model to remember.
- Reading `response.json()["content"]` instead of `["choices"][0]["message"]["content"]`.
- No timeout: the first CPU request loads the model and can take a minute.
- Ignoring `finish_reason: "length"` – the answer was cut off at `max_tokens`, so raise the limit or shorten the task.
