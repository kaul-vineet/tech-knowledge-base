"""Sizing table: which Qwen2.5 tag fits where (Mac mini via Metal, Windows via CUDA or CPU).

Official inputs in cost_model.py (Apple specs, Ollama sizes, Qwen2.5 config.json, Ollama FAQ/GPU docs); the
reserves and the decode efficiency are ASSUMPTIONS printed below. Run: python sizing.py [--ctx 8192] [--parallel 4]
"""
import argparse

import cost_model as cm

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ctx", type=int, default=4096)  # Ollama default context (FAQ)
    p.add_argument("--parallel", type=int, default=1)  # OLLAMA_NUM_PARALLEL
    a = p.parse_args()
    print(f"ctx {a.ctx}, parallel {a.parallel}; assumptions: {cm.ASSUMPTIONS}")
    for m in cm.MODELS:
        print(f"{m:<13} weights {cm.MODELS[m]['weights_gb']} GB + KV {cm.kv_gb(m, a.ctx, a.parallel):.2f} GB "
              f"({cm.kv_gb(m, 1, 1) * 1e6:.1f} kB per token, f16)")
    print(f"{'machine':<30} {'model':<13} {'need GB':>7} {'usable':>6}  {'runs on':<18} decode tok/s (estimate)")
    for machine, model, need, usable, where, tps in cm.sizing_rows(a.ctx, a.parallel):
        print(f"{machine:<30} {model:<13} {need:>7} {usable:>6}  {where:<18} {tps if tps else '-'}")
