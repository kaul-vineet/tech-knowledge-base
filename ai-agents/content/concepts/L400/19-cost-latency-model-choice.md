**Concept: cost, latency and model choice – routing, prompt caching, batching, context budgets, hardware sizing**

## Why it matters
On a Mac mini or a Windows PC, "cost" is mostly time and memory: how many tickets per minute, whether the model fits next to everything else, and how long a user waits. The cheapest lever is often not a smaller model. It is not re-processing the same prompt prefix, not sending tokens that never help, and sending only the hard cases to the big model. Every lever has a quality risk, so each one is measured against the golden set from lesson 12.

## Mental model
A request costs prefill (reading the prompt) plus decode (writing tokens). Decode on a local GPU is memory-bound: every new token reads all the weights once, so tokens/s ≤ memory bandwidth ÷ model size. The KV cache grows with context length × parallel slots.

```
cost ≈ uncached_prompt + 0.1·cached_prompt + output        (× model size)
latency ≈ prefill/prefill_speed + output/decode_speed     decode_speed ≲ bandwidth / weights
memory ≈ weights + 2·layers·kv_heads·head_dim·2 B · ctx · parallel
```

## Design space
- **Model routing.** Small model only (cheap, risky), large only (safe, slow), a *cascade* (small first; escalate when code rejects the answer, as in FrugalGPT), or a *router* that predicts difficulty up front (RouteLLM). A cascade only catches what your validator can see.
- **Prompt caching.** llama.cpp (`cache_prompt`, on by default) and vLLM automatic prefix caching reuse the KV cache of a shared prefix. Ollama reports `prompt_eval_cached_count`. It only works when the stable part (instructions, tool schemas, runbooks) comes first and the variable part comes last.
- **Batching.** Parallel slots (`OLLAMA_NUM_PARALLEL`, llama.cpp `--parallel`, continuous batching) let one weight read serve several sequences. The price is memory: Ollama's FAQ says RAM scales with parallel × context length.
- **Context budgeting.** Ollama's default window is 4,096 tokens. Reserve room for the output, then fill by priority: system, question, best evidence, newest history. Never fill by position.

## How to decide
Criteria in order: golden-set quality must not drop; then cost; then p95 latency; then memory headroom on the target machine. Measure each option on the fake server with the cost model, then confirm the speeds on real hardware (`real_model_probe.py`).

Worked example (20 golden tickets, warmed cache → see lab step 2; units ≈ 2 × parameters per token):

| strategy | passed | cost | p50 / p95 ms | escalated |
|---|---|---|---|---|
| large only | 20 | 7,000.0 | 867.8 / 883.2 | – |
| small only | 13 | 1,590.0 | 182.1 / 249.7 | – |
| cascade | 19 | 3,807.6 | 182.1 / 1,132.9 | 6 |
| rules + cascade | 20 | 3,890.1 | 182.1 / 1,123.6 | 4 |

The cascade missed t03. The small model returned *valid* JSON with the wrong priority, and no validator can see that. Adding a rule learned from eval failures (urgent, asap, immediately, down → large) restores 20/20 at 56 % of the large-only cost. Putting instructions first made 76 % of prompt tokens cacheable; putting the ticket first made it 3 % and doubled the cost (14,056).

Sizing from official numbers (Apple specs, Ollama sizes, Qwen2.5 `config.json`, f16 KV): qwen2.5:7b needs 4.7 GB of weights + 57.3 kB of KV per token, 4.93 GB at 4k. On an M6 Mac mini (153 GB/s) decode is estimated at ≈16 tok/s, ≈33 on an M5 Pro (307 GB/s), with an assumed 50 % efficiency. A 14b model at 32k × 4 slots needs 34.77 GB and does not fit a 24 GB Mac (try it 1). On Windows the same table says CUDA (compute capability 5.0+, driver 550+) or CPU; measure bandwidth there, because the card decides.

## Failure modes at scale
- **Silent quality loss** from routing: valid-looking wrong answers. Watch golden-set regressions per route, not only the escalation rate.
- **Cache misses after a prompt edit:** one timestamp at the top of the prompt drops cached tokens to ≈0. Watch the cached/prompt ratio.
- **Memory cliff:** raising context or parallel slots pushes the model partly onto the CPU (`ollama ps` shows a CPU/GPU split), and throughput collapses.

## Common mistakes
- Pricing local models at zero: time, memory and queueing are the cost.
- Truncating the prompt from the end, which drops the question first (build task).
- Trusting the sizing estimates without measuring tokens/s on your own machine.
