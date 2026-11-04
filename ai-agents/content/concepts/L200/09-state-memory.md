**Concept: state and memory – what the agent carries, and what it stores**

## Why it matters
The model is stateless: every call re-sends the conversation, and the context window caps how much fits (Ollama's default is 4096 tokens). Long chats fail or get silently truncated, and nothing survives a restart.

## Mental model
A notebook and a filing cabinet. The message list is the notebook you hand over on every call – when pages run out, you replace old pages with a one-line summary. Facts the user explicitly wants kept go into the cabinet (SQLite), which outlives the conversation.

```
send(text): history + text ──► count tokens ──► over budget? ──yes─► summarise old turns
                                                     │no                 (model call)
                                                     ▼
                                    model ─► save_memory / recall_memory ─► SQLite file
```

## How it works
1. **Conversation state is a list.** Each turn appends user, assistant and tool messages. → see lab step 2
2. **Budget before every call.** Count tokens of what you are about to send and reserve room for the reply. The lab counts words; the fake server does too, so they match `usage.prompt_tokens`, but real tokenizers differ – compare against `usage`. → see lab step 4
3. **Summarise to fit.** Over budget, the oldest turns become one summary written by the model; the last turns stay verbatim. Worked example (budget 60): token counts before each call are 18, 43, then 65 → one summary, 4 messages, 62 tokens. The summary kept "staging database is on port" but lost "5433". → see lab step 2
4. **Long-term memory is explicit.** `save_memory` and `recall_memory` are ordinary tools backed by SQLite with `?` placeholders. A new conversation with an empty history recalls `1: the staging database is on port 5433` from the file. → see lab step 3
5. **Keep memory bounded.** Cap rows and recall only a few matches (build task). → see lab step 4

## Trade-offs
| Use when | Avoid when |
|---|---|
| Summaries: long chats where gist is enough | Exact values matter – store them as facts instead |
| Explicit memory: user-requested, reviewable facts | Saving everything automatically (privacy, noise) |
| SQLite: one user, one machine | Many users – add access control per user |

## Common mistakes
- Assuming the server will tell you when the context overflowed.
- Summarising the system prompt or the latest turn away.
- Building SQL with string formatting instead of placeholders.
