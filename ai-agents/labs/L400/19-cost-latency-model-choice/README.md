# 19 – Cost, latency and model choice

Local cost is time and memory. Measure every lever - smaller model, cache-friendly prompts, batching, context budgets - against the golden set before you keep it.

Concept note: `../../../content/concepts/L400/19-cost-latency-model-choice.md` · lesson object: `content/L400.json` #19

## Design brief
Ticket triage (lesson 12's 20-case golden set) runs on a Mac mini or a Windows PC; a small (1.5B) and a larger (7B) local model are available.

Constraints:
- Golden-set accuracy must equal the large model's (20/20)
- Compute cost <= 60 % of large-only
- >= 60 % of prompt tokens served from the prefix cache
- Model + KV cache must fit the target machine at a 4k context

Question: Large only, small only, a validated cascade, or rules + cascade - and in which prompt order?

## Run (fake server – validated)

**Start the L400 fake server**
```bash
python ../fake_server_l400.py --port 8765
```
PowerShell:
```powershell
python ..\fake_server_l400.py --port 8765
```

**Measure the routes, the prompt order and batching**
```bash
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1; python route_cost.py
```
PowerShell:
```powershell
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; python route_cost.py
```

**Size your machine**
```bash
python sizing.py; python sizing.py --ctx 32768 --parallel 4
```
PowerShell:
```powershell
python sizing.py; python sizing.py --ctx 32768 --parallel 4
```

**Build task: budget.py**
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # drop BUILD_TARGET to check solution/
```
PowerShell:
```powershell
$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task   # Remove-Item Env:BUILD_TARGET to check solution/
```

**Real model on YOUR machine**
```bash
python real_model_probe.py qwen2.5:1.5b qwen2.5:7b
```
PowerShell:
```powershell
python real_model_probe.py qwen2.5:1.5b qwen2.5:7b
```

### Expected output (observed 2026-10-28)
```
assumptions: {"mac_reserved_gb": 6, "win_ram_reserved_gb": 6, "vram_reserved_gb": 1, "decode_efficiency": 0.5, "prefill_speedup": 8, "cached_prefill_cost": 0.1}
{"strategy": "large-only", "passed": 20, "cases": 20, "cost": 7000.0, "p50_ms": 867.8, "p95_ms": 883.2, "escalated": 0, "cache_ratio": 0.76}
{"strategy": "small-only", "passed": 13, "cases": 20, "cost": 1590.0, "p50_ms": 182.1, "p95_ms": 249.7, "escalated": 0, "cache_ratio": 0.76}
{"strategy": "cascade", "passed": 19, "cases": 20, "cost": 3807.6, "p50_ms": 182.1, "p95_ms": 1132.9, "escalated": 6, "cache_ratio": 0.75}
{"strategy": "rules+cascade", "passed": 20, "cases": 20, "cost": 3890.1, "p50_ms": 182.1, "p95_ms": 1123.6, "escalated": 4, "cache_ratio": 0.76}
prompt order instructions first: cached 76% of prompt tokens, cost 7000.0, p50 867.8 ms
prompt order ticket first      : cached 3% of prompt tokens, cost 14056.0, p50 1082.8 ms
batching: {"parallel": 1, "kv_gb": 0.23, "need_gb": 4.93, "wall_s_for_batch": 17.37}
batching: {"parallel": 4, "kv_gb": 0.94, "need_gb": 5.64, "wall_s_for_batch": 4.34}

$ python sizing.py   (first lines)
ctx 4096, parallel 1; assumptions: {'mac_reserved_gb': 6, 'win_ram_reserved_gb': 6, 'vram_reserved_gb': 1, 'decode_efficiency': 0.5, 'prefill_speedup': 8, 'cached_prefill_cost': 0.1}
qwen2.5:1.5b  weights 0.986 GB + KV 0.12 GB (28.7 kB per token, f16)
qwen2.5:7b    weights 4.7 GB + KV 0.23 GB (57.3 kB per token, f16)
qwen2.5:14b   weights 9.0 GB + KV 0.81 GB (196.6 kB per token, f16)
machine                        model         need GB usable  runs on            decode tok/s (estimate)
Mac mini M6 16GB               qwen2.5:1.5b      1.1     10  GPU (Metal)        78
Mac mini M6 16GB               qwen2.5:7b       4.93     10  GPU (Metal)        16
Mac mini M6 16GB               qwen2.5:14b      9.81     10  GPU (Metal)        8
```

Tests: `Ran 9 tests ... OK` (`python -m unittest -v` in this folder).

## Options measured
| Option | Evidence (this lab) | Verdict |
|---|---|---|
| One model for everything (large only or small only) | Large: 20/20, cost 7,000.0, p50 867.8 ms. Small: 13/20 (prose-wrapped JSON on long tickets, wrong priority on t03), cost 1,590.0, p50 182.1 ms. | Large is the quality bar; small alone fails it. |
| Validated cascade (small, then large on a rejected answer) | 19/20, cost 3,807.6, 6 escalations, p95 1,132.9 ms; t03 missed: valid JSON, wrong priority. | Rejected alone: validators cannot see valid-but-wrong answers. |
| Rules + cascade | 20/20, cost 3,890.1 (56 % of large), 4 escalations, p50 182.1 / p95 1,123.6 ms; 76 % of prompt tokens cached (3 % with the ticket first). | Chosen (ADR-0019); re-learn the rule when the golden set or model changes. |


## Decision and fitness function
Decision record: `ADR-0019-rules-plus-cascade.md` (Nygard: Title, Status, Context, Decision, Consequences).

Fitness function: `test_fitness_cost.py` – rules+cascade keeps large-only accuracy at <= 60 % of its cost, and the production prompt keeps its stable prefix first. Threshold: passed == large passed (20/20); cost <= 0.6 x large; cache ratio >= 0.6.


## Scaling limits
- New ticket types: the routing rule was learned on 20 cases -> golden-set regressions on the small route; re-run the eval per route.
- Longer contexts or more parallel slots: KV memory grows linearly -> `ollama ps` shows a CPU/GPU split and tokens/s collapses (14b at 32k x 4 = 34.77 GB).
- Mixed prompts per server slot: cache hit ratio drops when unrelated prompts share a slot -> raise parallel slots or pin one prompt family per server.


## Failure lab
| | |
|---|---|
| Fault | To cut cost, every ticket is routed to fake-small (stands in for qwen2.5:1.5b): it wraps long answers in prose and treats only 'outage' as high priority (rule S, deterministic). |
| Symptom | Golden set drops from 20/20 to 13/20 (t03, t04, t05, t10, t14, t18, t19); a validated cascade recovers to 19/20 but t03 stays wrong (valid JSON, priority normal instead of high). |
| Fix | Rules learned from the eval failures route hard tickets to the large model; the cascade catches the rest: 20/20 at 56 % of large-only cost. |
| Proof | test_failure_lab_small_only_and_the_silent_miss: small-only failures listed, cascade t03 fails with ['fake-small'], rules+cascade t03 passes with ['fake-large']. |


## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| Cascade (validate, escalate) | No labels needed; cheap on easy cases | Blind to valid-but-wrong; p95 grows for escalations | Errors are mostly structural |
| Router / rules up front | Hard cases skip the small model | Rules drift with the data; need eval evidence | Eval failures cluster on recognisable inputs |
| More parallel slots | Throughput (up to ~4x for 4 slots, memory-bound) | KV memory x slots; cache slots split | Many concurrent users and memory headroom |


## Build task
Make budget.fit() budget the prompt by priority, not position: keep system + question + the output reserve, then the best-scored documents that fit, then the newest history turns that fit.

Hints:
- budget = num_ctx - reserve - words(system) - words(question)
- Sort docs by score, add each one that still fits.
- Walk history from newest to oldest; stop at the first turn that does not fit.

Your file: `budget.py` (shipped unfixed) · solution: `solution/budget.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28: Before your change: FAILED: the last words are ['deploy', 'deploy', ...] != ['QUESTION:', 'why', 'is', 'checkout', 'slow?'] - the question was cut. After: OK, fit: 714 words; docs ['RB-3', 'RB-7']


## Try it
1. Run sizing for a 32k context with 4 parallel slots (cm.sizing_rows(ctx=32768, parallel=4)). Predict: Does qwen2.5:14b still fit a 24 GB Mac mini? A 48 GB one?
   Observed: 14b at 32k x 4 needs 34.77 GB -> M6 24GB: does not fit; M5 Pro 48GB: GPU (Metal)
2. Drop 'urgent' and 'down' from the routing rule (HARD = asap|immediately). Predict: Which ticket fails, and does the cascade catch it?
   Observed: 19/20, cost 3711.9, failed ['t03'] - cheaper, but the small model's valid-but-wrong answer passes the validator.


## Learning tools
- **Ollama (supporting runtime)** (CHECK, MIT (OSI: yes)): Run real_model_probe.py qwen2.5:1.5b qwen2.5:7b and `ollama ps`; put your measured decode_tok_s next to sizing.py's estimate for your Mac mini or GPU. Pending a manual run. Expect the second call's cached > 0 (shared prefix), 100% GPU in `ollama ps` for models that fit, and decode speeds below sizing.py's estimate (it assumes 50 % of the bandwidth bound: ~16 tok/s for 7b on an M6 16GB). Mac: `brew install ollama && brew services start ollama; ollama pull qwen2.5:1.5b && ollama pull qwen2.5:7b` · Windows: `irm https://ollama.com/install.ps1 | iex; ollama pull qwen2.5:1.5b; ollama pull qwen2.5:7b`


## Equivalents
- vLLM automatic prefix caching (enable_prefix_caching) and llama.cpp --cache-prompt / --parallel: the server-side levers this lesson models
- RouteLLM routers: learned routing between a strong and a weak model (this lab's rule is the hand-made version)
- Hosted APIs bill cached input tokens at a discount - one line of equivalence; local cost is time and memory


## Simulator vs real
Costs and latencies are a model (cost_model.py) driven by the fake's token counts: illustrative units, not dollars or measured milliseconds. Hardware numbers are official specs; reserves and efficiency are labelled assumptions until real_model_probe.py measures your machine.

**Caution:** Sizing tables are estimates: leave headroom for macOS/Windows and other apps, and verify with `ollama ps` before relying on a model size for production.

**Pending CI / manual:** real_model_probe.py on a Mac mini (Metal) and a Windows PC (CUDA/CPU) - manual; route_cost.py with SMALL_MODEL=qwen2.5:1.5b LARGE_MODEL=qwen2.5:7b (CI real_model job; CPU only); Ollama exercise (manual)
