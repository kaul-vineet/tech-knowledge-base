**Concept: an agent is a bounded loop around tool calls**

## Why it matters
"Compute 17×23 and (120−20)/4" needs two tool calls; another task needs ten. An unbounded loop with a confused model can call tools forever or repeat a harmful action. The loop must be flexible *and* bounded.

## Mental model
A thermostat with a safety cut-off: the model decides, tools act and report back, and your code owns the cut-off (`max_steps`), the allowed actions and the approval switch.

```
start ─► step += 1; step > max_steps? ─► STOP(budget)
         reply = model(messages, tools)
         no tool_calls? ─► STOP(final answer)
         each call: allowed? approved? run ─► append ─┐
         ▲────────────────────────────────────────────┘
```

## How it works
1. **State is the message list.** Each step appends the assistant reply and one tool message per call: 2 → 4 → 6 → 7 messages, ending in `Final answer: 17*23 = 391; (120-20)/4 = 25.0` (from `research/concept_examples.py`). → see lab step 2
2. **Two exits:** a reply without `tool_calls` is the final answer; hitting `max_steps` returns `stopped: max_steps` instead of hanging (`max_steps=1` stops after one tool step). → see lab step 2
3. **Gates and errors live in code:** an allow-list, an approval callback that defaults to deny, a safe AST calculator instead of `eval`, and tool errors returned as text so the model can recover. → see lab step 3

## Common mistakes
- `while True` with no step budget.
- Letting the model decide permissions instead of code.
- Raising on tool errors so one bad argument kills the run.
