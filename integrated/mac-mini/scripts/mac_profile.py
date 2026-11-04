"""Mac mini profile: what this machine is, and what fits in its memory - computed, never quoted from memory.

python mac_profile.py                    detect this machine (macOS: sysctl; Linux: sysconf; otherwise pass --ram)
python mac_profile.py --ram 24           simulate a 24 GB Mac mini (works anywhere; this is the sandbox "here" mode)
python mac_profile.py --table 16 24 32 64 --markdown     the by-RAM table used in integrated/mac-mini/README.md
python mac_profile.py --json             one JSON object (used by the projects' mac_mini scripts and nightly.sh)

Model maths (same rule as ai-agents L400 #19 cost_model.py, which this file imports, never copies):
  need(model) = weights (Ollama Q4_K_M download size) + KV cache
  KV cache    = 2 (K and V) x layers x kv_heads x head_dim x 2 bytes (f16, Ollama's default) x context x parallel
  usable      = RAM - reserved for macOS + apps (an ASSUMPTION, printed); a model is recommended if
                need <= usable x (1 - headroom) so the simulations running next to it still have room.
Statevector maths: one amplitude is complex128 = 16 bytes; a simulator holds the state plus one working copy, so
  bytes(n) = 16 x 2^n x copies  ->  max n = floor(log2(usable x (1 - headroom) / (16 x copies))).
Apple sells RAM in GiB ("16 GB" = 16 x 2^30 bytes); everything below is converted to decimal GB (1e9), the unit of the
Ollama download sizes.
"""
import argparse
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[3]
_COST = KB / "ai-agents" / "labs" / "L400" / "19-cost-latency-model-choice" / "cost_model.py"
_spec = importlib.util.spec_from_file_location("kb_ai19_cost_model", _COST)
cost_model = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cost_model)

# Added for this track (verified 2026-11-02, see integrated/research/mac-mini-evidence.md): ollama.com/library/qwen2.5/tags
# (3b 1.9 GB, 32b 20 GB, Q4_K_M) and the Qwen2.5-3B/32B-Instruct config.json (layers, KV heads, hidden/heads = 128).
EXTRA_MODELS = {
    "qwen2.5:3b": {"weights_gb": 1.9, "layers": 36, "kv_heads": 2, "head_dim": 128, "params_b": 3},
    "qwen2.5:32b": {"weights_gb": 20.0, "layers": 64, "kv_heads": 8, "head_dim": 128, "params_b": 32},
}
MODELS = dict(sorted({**cost_model.MODELS, **EXTRA_MODELS}.items(), key=lambda kv: kv[1]["params_b"]))
ASSUMPTIONS = {
    "reserved_gb": cost_model.ASSUMPTIONS["mac_reserved_gb"],  # macOS + apps (ai-agents L400 #19 assumption)
    "headroom": 0.10,           # keep 10 % of the usable memory free for the simulations next to the model
    "statevector_copies": 2,    # state + one working copy (numpy-style gate application)
    "ctx": 4096,                # Ollama default context (FAQ)
    "parallel": 1,              # OLLAMA_NUM_PARALLEL default
}
BYTES_PER_AMPLITUDE = {"complex128": 16, "complex64": 8}


def _sysctl(name):
    try:
        out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None
    except (OSError, subprocess.SubprocessError):
        return None


def detect():
    """Facts about THIS machine. Fields that cannot be read are None (never guessed)."""
    system, machine = platform.system(), platform.machine()
    info = {"system": system, "arch": machine, "macos": platform.mac_ver()[0] or None, "cores": os.cpu_count(),
            "perf_cores": None, "ram_bytes": None, "apple_silicon": system == "Darwin" and machine == "arm64"}
    if system == "Darwin":
        mem = _sysctl("hw.memsize")
        info["ram_bytes"] = int(mem) if mem and mem.isdigit() else None
        perf = _sysctl("hw.perflevel0.physicalcpu")  # performance cores on Apple silicon; absent on Intel Macs
        info["perf_cores"] = int(perf) if perf and perf.isdigit() else None
    elif hasattr(os, "sysconf") and "SC_PHYS_PAGES" in os.sysconf_names:
        info["ram_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    return info


def kv_gb(model, ctx, parallel):
    m = MODELS[model]
    return 2 * m["layers"] * m["kv_heads"] * m["head_dim"] * 2 * ctx * parallel / 1e9


def need_gb(model, ctx, parallel):
    return MODELS[model]["weights_gb"] + kv_gb(model, ctx, parallel)


def budget_gb(ram_gb, a=ASSUMPTIONS):
    usable = max(ram_gb - a["reserved_gb"], 0.0)
    return usable, usable * (1 - a["headroom"])


def recommend(ram_bytes, a=ASSUMPTIONS):
    """Everything derived from RAM: which models fit (largest first) and the statevector limit, with the maths."""
    ram_gb = ram_bytes / 1e9
    usable, budget = budget_gb(ram_gb, a)
    rows = [{"model": m, "weights_gb": MODELS[m]["weights_gb"], "kv_gb": round(kv_gb(m, a["ctx"], a["parallel"]), 3),
             "need_gb": round(need_gb(m, a["ctx"], a["parallel"]), 3),
             "fits": need_gb(m, a["ctx"], a["parallel"]) <= budget} for m in MODELS]
    fitting = [r["model"] for r in rows if r["fits"]]
    qubits = {}
    for dtype, b in BYTES_PER_AMPLITUDE.items():
        n = int(math.floor(math.log2(budget * 1e9 / (b * a["statevector_copies"])))) if budget > 0 else 0
        qubits[dtype] = {"max_qubits": n, "state_gb": round(b * 2 ** n / 1e9, 3),
                         "with_copies_gb": round(b * 2 ** n * a["statevector_copies"] / 1e9, 3),
                         "next_qubit_gb": round(b * 2 ** (n + 1) * a["statevector_copies"] / 1e9, 3)}
    return {"ram_gb": round(ram_gb, 2), "usable_gb": round(usable, 2), "budget_gb": round(budget, 2),
            "models": rows, "largest_model": fitting[-1] if fitting else None,
            "compare_models": fitting[-3:],  # up to 3 sizes for the model-comparison experiments (03, 05, 08)
            "statevector": qubits, "assumptions": dict(a)}


def ram_from_gib(gib):
    return int(gib * 2 ** 30)


def profile(ram_gib=None):
    info = detect()
    simulated = ram_gib is not None
    ram_bytes = ram_from_gib(ram_gib) if simulated else info["ram_bytes"]
    if ram_bytes is None:
        raise SystemExit("could not read the RAM size on this OS: pass --ram <GB>, e.g. --ram 16")
    out = {"machine": info, "simulated_ram_gib": ram_gib, **recommend(ram_bytes)}
    out["workers"] = info["perf_cores"] or info["cores"] or 1  # multiprocessing pool size for the overnight runs
    return out


def explain(p):
    a = p["assumptions"]
    m = p["machine"]
    lines = [f"machine: {m['system']} {m['arch']} macOS {m['macos'] or '-'} | cores {m['cores']} "
             f"(performance {m['perf_cores'] or '-'}) | apple silicon: {m['apple_silicon']}"
             + (f" | RAM SIMULATED: {p['simulated_ram_gib']} GiB" if p["simulated_ram_gib"] else ""),
             f"RAM {p['ram_gb']} GB - reserved {a['reserved_gb']} GB = usable {p['usable_gb']} GB; "
             f"x (1 - headroom {a['headroom']}) = budget {p['budget_gb']} GB",
             f"models at ctx {a['ctx']} x parallel {a['parallel']} (need = Q4_K_M weights + f16 KV cache):"]
    for r in p["models"]:
        lines.append(f"  {r['model']:<13} {r['weights_gb']:>5} + {r['kv_gb']:>5.3f} = {r['need_gb']:>6.3f} GB  "
                     f"{'fits' if r['fits'] else 'too big'}")
    lines.append(f"largest model: {p['largest_model']} | compare: {', '.join(p['compare_models']) or '-'}")
    for dtype, q in p["statevector"].items():
        b = BYTES_PER_AMPLITUDE[dtype]
        lines.append(f"statevector {dtype}: {b} B x 2^n x {a['statevector_copies']} copies <= {p['budget_gb']} GB -> "
                     f"n = {q['max_qubits']} ({q['with_copies_gb']} GB; n+1 would need {q['next_qubit_gb']} GB)")
    lines.append(f"overnight worker pool: {p['workers']} processes")
    return "\n".join(lines)


def table(gibs, markdown=False):
    rows = [(g, recommend(ram_from_gib(g))) for g in gibs]
    head = ["Mac mini RAM", "budget GB", "largest local model", "spare GB", "compare (03/05/08)", "max qubits c128",
            "max qubits c64"]
    spare = lambda r: f"{r['budget_gb'] - next(m['need_gb'] for m in r['models'] if m['model'] == r['largest_model']):.2f}" \
        if r["largest_model"] else "-"
    body = [[f"{g} GB", f"{r['budget_gb']}", r["largest_model"] or "-", spare(r), ", ".join(r["compare_models"]) or "-",
             str(r["statevector"]["complex128"]["max_qubits"]), str(r["statevector"]["complex64"]["max_qubits"])]
            for g, r in rows]
    if markdown:
        return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(b) + " |" for b in body])
    return "\n".join("  ".join(f"{c:<22}" for c in row) for row in [head] + body)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ram", type=float, help="simulate this much RAM in GB as Apple sells it (GiB)")
    ap.add_argument("--table", type=float, nargs="+", help="print the by-RAM table for these sizes")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.table:
        print(table([int(g) if g.is_integer() else g for g in args.table], args.markdown))
        return 0
    p = profile(args.ram)
    print(json.dumps(p) if args.json else explain(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
