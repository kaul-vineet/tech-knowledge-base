"""Helper for lesson 19: official hardware/model numbers + the cost/latency model (every assumption is named).

Official (retrieved 2026-10-28): Mac mini specs (apple.com/mac-mini/specs), Ollama library Q4_K_M download sizes,
Qwen2.5 config.json (layers, KV heads, head dim), Ollama FAQ (default context 4096, f16 KV cache, RAM scales with
OLLAMA_NUM_PARALLEL x OLLAMA_CONTEXT_LENGTH), Ollama GPU docs (NVIDIA compute capability 5.0+, driver 550+; Metal).
"""
MODELS = {  # weights_gb = Ollama download (Q4_K_M); kv from config.json: 2 (K,V) x layers x kv_heads x head_dim x 2 bytes
    "qwen2.5:1.5b": {"weights_gb": 0.986, "layers": 28, "kv_heads": 2, "head_dim": 128, "params_b": 1.5},
    "qwen2.5:7b": {"weights_gb": 4.7, "layers": 28, "kv_heads": 4, "head_dim": 128, "params_b": 7},
    "qwen2.5:14b": {"weights_gb": 9.0, "layers": 48, "kv_heads": 8, "head_dim": 128, "params_b": 14},
}
MAC_MINI = [("M6 16GB", 16, 153), ("M6 24GB", 24, 170), ("M6 32GB", 32, 170),  # (config, unified GB, GB/s)
            ("M5 Pro 24GB", 24, 307), ("M5 Pro 48GB", 48, 307), ("M5 Pro 64GB", 64, 307)]
WINDOWS = [("CPU only, 16GB RAM", 16, "ram"), ("CPU only, 32GB RAM", 32, "ram"), ("NVIDIA 8GB VRAM", 8, "vram"),
           ("NVIDIA 12GB VRAM", 12, "vram"), ("NVIDIA 16GB VRAM", 16, "vram"), ("NVIDIA 24GB VRAM", 24, "vram")]
ASSUMPTIONS = {  # NOT from a spec: replace with your own measurements (real_model_probe.py prints them)
    "mac_reserved_gb": 6,       # macOS + apps; the GPU cannot use all unified memory
    "win_ram_reserved_gb": 6,   # Windows + apps when the model runs on the CPU
    "vram_reserved_gb": 1,      # driver + display
    "decode_efficiency": 0.5,   # achieved / bandwidth-bound decode speed
    "prefill_speedup": 8,       # prefill tokens/s relative to decode tokens/s (prefill is compute-bound, batched)
    "cached_prefill_cost": 0.1,  # a cached prompt token costs 10 % of an uncached one
}
FAKE = {"fake-small": "qwen2.5:1.5b", "fake-large": "qwen2.5:7b"}  # what the fake models stand in for
MAC_FOR_LATENCY = 153  # GB/s of the base Mac mini, used for the latency estimates


def kv_gb(model, ctx=4096, parallel=1):
    m = MODELS[model]
    return 2 * m["layers"] * m["kv_heads"] * m["head_dim"] * 2 * ctx * parallel / 1e9  # f16 = 2 bytes


def need_gb(model, ctx=4096, parallel=1):
    return MODELS[model]["weights_gb"] + kv_gb(model, ctx, parallel)


def decode_tps(model, bandwidth_gbs=MAC_FOR_LATENCY):
    """Memory-bound decode: each new token reads every weight once -> bandwidth / weights is an upper bound."""
    return bandwidth_gbs / MODELS[model]["weights_gb"] * ASSUMPTIONS["decode_efficiency"]


def call_cost(fake_model, usage):
    """Relative compute units: ~2 x params FLOPs per token, cached prompt tokens at a discount."""
    m = MODELS[FAKE[fake_model]]
    cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    tokens = usage["prompt_tokens"] - cached + cached * ASSUMPTIONS["cached_prefill_cost"] + usage["completion_tokens"]
    return 2 * m["params_b"] * tokens


def call_latency_ms(fake_model, usage):
    tps = decode_tps(FAKE[fake_model])
    cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    prefill = (usage["prompt_tokens"] - cached) / (tps * ASSUMPTIONS["prefill_speedup"])
    return round((prefill + usage["completion_tokens"] / tps) * 1000, 1)


def sizing_rows(ctx=4096, parallel=1):
    rows = []
    for name, gb, bw in MAC_MINI:
        usable = gb - ASSUMPTIONS["mac_reserved_gb"]
        for model in MODELS:
            fits = need_gb(model, ctx, parallel) <= usable
            rows.append(("Mac mini " + name, model, round(need_gb(model, ctx, parallel), 2), usable,
                         "GPU (Metal)" if fits else "does not fit", round(decode_tps(model, bw)) if fits else None))
    for name, gb, kind in WINDOWS:
        usable = gb - ASSUMPTIONS["vram_reserved_gb" if kind == "vram" else "win_ram_reserved_gb"]
        for model in MODELS:
            fits = need_gb(model, ctx, parallel) <= usable
            where = ("GPU (CUDA)" if kind == "vram" else "CPU") if fits else ("partial GPU + CPU" if kind == "vram" else "does not fit")
            rows.append(("Windows " + name, model, round(need_gb(model, ctx, parallel), 2), usable, where, None))
    return rows
