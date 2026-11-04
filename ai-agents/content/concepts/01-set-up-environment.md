**Concept: one URL, many back ends – model, inference server, client, stand-in**

## Why it matters
You build an agent on a laptop with no GPU. Next week the same code runs in CI where nothing can be downloaded. Swapping "real model" for "test double" must be a configuration change, not a rewrite.

## Mental model
Like a database driver and a connection string: your code speaks the chat-completions JSON to `LOCAL_MODEL_URL`; whichever server answers is a detail.

```
script ──HTTP JSON──► LOCAL_MODEL_URL/chat/completions
                        ├─ Ollama / llama-server ─► GGUF weights (Metal/CUDA/CPU)
                        ├─ vLLM ─► GPU model
                        └─ fake_model_server.py (rules, no model) ← tests
```

## How it works
1. **The stand-in** answers the same two endpoints (`/v1/models`, `/v1/chat/completions`) with fixed rules, so tests are repeatable and need no download. It checks protocol shape, not intelligence. → see lab step 2
2. **The client** reads `LOCAL_MODEL_URL` and `LOCAL_MODEL` from the environment, lists models first, then sends one chat request. Example (from `research/concept_examples.py`): the smallest request is **103 bytes** and the fake replies with `usage` 6/11/17 – it counts words, a real server counts tokens. → see lab step 3
3. **The inference server** loads the weights (`qwen2.5:1.5b`, 986 MB, 4-bit) and serves the same URL shape; Ollama listens on `127.0.0.1:11434`, so `LOCAL_MODEL_URL=http://localhost:11434/v1`. → see lab step 5

## Common mistakes
- Forgetting `/v1` in `LOCAL_MODEL_URL` (404) or pointing this code at Ollama's native `/api/chat`.
- Asking for a model tag that was never pulled.
- Treating fake-server output as evidence that a prompt works on a real model.
