"""Recompute every calculation answer and execute every code-reading snippet in content/qbank/*.json (L100-L500).

Run from the topic folder or anywhere:  python research/qbank_checks.py   -> prints OK and exits 0.
Calculation answers come from the functions below (lesson code is imported where it is pure Python:
lesson 19's cost_model.py); code-reading answers are the snippet's stdout.
"""
import contextlib
import importlib.util
import io
import json
import math
import sys
from collections import Counter
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
LABS = TOPIC / "labs"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = load("cost_model", LABS / "L400/19-cost-latency-model-choice/cost_model.py")


def r(correct, *wrong):
    return {"correct": str(correct), "wrong": [str(w) for w in wrong]}


def chunk(text, max_words=40, overlap=10):  # lesson 7 rag.chunk, verbatim logic
    chunks = []
    for para in text.split("\n\n"):
        words = para.split()
        if not words or para.lstrip().startswith("#"):
            continue
        for start in range(0, len(words), max_words - overlap):
            chunks.append(" ".join(words[start:start + max_words]))
            if start + max_words >= len(words):
                break
    return chunks


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def chi_square(baseline_counts, window_counts):  # lesson 21 governance.chi_square on counts
    total, n = sum(baseline_counts.values()), sum(window_counts.values())
    keys = [k for k in baseline_counts if baseline_counts[k]]
    stat = sum((window_counts.get(k, 0) - n * baseline_counts[k] / total) ** 2 / (n * baseline_counts[k] / total) for k in keys)
    return stat, len(keys) - 1


CRITICAL_99 = {1: 6.635, 4: 13.277}  # lesson 21 table (alpha = 0.01)


# ---------------------------------------------------------------- L100
def history_tokens():
    user, reply, turn = 8, 20, 4
    history = (turn - 1) * (user + reply)
    return r(history + user, user, (user + reply) + user, turn * (user + reply))


def cumulative_prompt_tokens():
    user, reply, turns = 8, 20, 4
    per_call = [k * (user + reply) + user for k in range(turns)]
    return r(sum(per_call), per_call[-1], turns * user, turns * (user + reply))


def retry_messages():
    first, per_retry, attempt = 2, 2, 3
    return r(first + per_retry * (attempt - 1), first, first + (attempt - 1), first + per_retry * attempt)


def steps_sequential():
    tool_results, final = 3, 1  # one tool call per turn, then a turn with no tool_calls
    return r(tool_results + final, tool_results, 2 * tool_results, tool_results - 1)


def steps_parallel():
    return r(1 + 1, 3 + 1, 3, 1)


def usage_total():
    prompt, completion = 6, 11
    return r(prompt + completion, prompt, completion, prompt * completion)


# ---------------------------------------------------------------- L200
def cosine_34():
    a, b = (3, 4), (4, 3)
    dot = sum(x * y for x, y in zip(a, b))
    return r(f"{cosine(a, b):.2f}", f"{dot:.2f}", f"{dot / 50:.2f}", "1.00")


def dot_vs_cosine():
    q, a, b = (1, 1, 0), (1, 1, 0), (5, 0, 5)
    dot_a, dot_b = sum(x * y for x, y in zip(q, a)), sum(x * y for x, y in zip(q, b))
    cos_a, cos_b = cosine(q, a), cosine(q, b)
    assert dot_b > dot_a and cos_a > cos_b
    return r(f"Raw dot ranks B first ({dot_b} vs {dot_a}); cosine ranks A first ({cos_a:.1f} vs {cos_b:.1f})",
             f"Both rank B first ({dot_b} vs {dot_a} and {cos_b:.1f} vs {cos_a:.1f})",
             f"Both rank A first ({dot_a} vs {dot_b} and {cos_a:.1f} vs {cos_b:.1f})",
             f"Raw dot ranks A first ({dot_a} vs {dot_b}); cosine ranks B first ({cos_b:.1f} vs {cos_a:.1f})")


def words_budget():
    window, reserve, tokens_per_word = 4096, 512, 1.3
    return r(math.floor((window - reserve) / tokens_per_word), window - reserve,
             math.floor((window - reserve) * tokens_per_word), math.floor(window / tokens_per_word))


def bruteforce_ops():
    chunks, dims = 10_000, 768
    return r(f"{chunks * dims:,}", f"{dims:,}", f"{chunks:,}", f"{chunks * dims * 10:,}")


def overlap_chunk_count():
    text = " ".join(f"w{i}" for i in range(1000))
    n = len(chunk(text, 40, 10))
    return r(n, 1000 // 40, (1000 - 40) // 30, 1000 // 10)


def context_share():
    window, reply = 4096, 512
    return r(f"{(window - reply) / window:.1%}", f"{reply / window:.1%}", "100.0%", f"{(window - 2 * reply) / window:.1%}")


# ---------------------------------------------------------------- L300
def min_cases_for_bar():
    cases, bar = 20, 0.95
    need = math.ceil(bar * cases - 1e-9)
    return r(need, need - 1, cases, need - 2)


def span_share():
    root, tool = 640, 597
    return r(f"{tool / root:.0%}", f"{(root - tool) / root:.0%}", f"{tool / (root + tool):.0%}", "100%")


def model_vs_tool():
    chats, chat_ms, tool_ms = 4, 250, 600
    model = chats * chat_ms
    return r(f"Model calls, by {model - tool_ms} ms ({model} vs {tool_ms} ms)",
             f"The tool, by {tool_ms - chat_ms} ms ({tool_ms} vs {chat_ms} ms)",
             f"The tool, by {tool_ms - 2 * chat_ms} ms ({tool_ms} vs {2 * chat_ms} ms)",
             "Neither: both total the same time")


def backoff_range():
    base, cap, attempt = 0.05, 0.4, 2
    d = min(cap, base * 2 ** attempt)
    return r(f"{d * 0.5:.2f}-{d:.2f} s", f"{d:.2f}-{2 * d:.2f} s", f"{base * 0.5:.3f}-{base:.2f} s", f"0.00-{d:.2f} s")


def budget_binding():
    max_tokens, max_cost, price_per_1k = 1500, 0.01, 0.002
    tokens_for_cost = round(max_cost / price_per_1k * 1000)
    cost_at_token_cap = max_tokens / 1000 * price_per_1k
    assert max_tokens < tokens_for_cost
    return r(f"Tokens: the cap trips at {max_tokens:,} tokens, while ${max_cost} would need {tokens_for_cost:,}",
             f"Cost: ${max_cost} is reached at {max_tokens:,} tokens, before the token cap",
             f"Both: they trip together at {max_tokens:,} tokens",
             f"Neither: {max_tokens:,} tokens cost ${cost_at_token_cap * 10:.2f}, above the cap")


def timeout_worst_case():
    timeout, retries, endpoints = 0.5, 2, 2
    return r(f"{endpoints * (retries + 1) * timeout:.1f} s", f"{(retries + 1) * timeout:.1f} s",
             f"{endpoints * retries * timeout:.1f} s", f"{endpoints * (retries + 1) * 2.0:.1f} s")


def redteam_rate():
    return r(f"{3 / 8:.1%}", f"{5 / 8:.1%}", f"{1 / 8:.1%}", f"{8 / 8:.1%}")


# ---------------------------------------------------------------- L400
def hybrid_threshold():
    limit, estimate = 2000, 1178
    t = 0.9 * limit
    assert estimate <= t
    return r(f"{t:,.0f} tokens - t07 ({estimate:,}) stays on one agent",
             f"{0.9 * 1000:,.0f} tokens - t07 ({estimate:,}) is escalated",
             f"{limit:,} tokens - t07 ({estimate:,}) is escalated",
             f"{0.9 * limit:,.0f} tokens - t07 ({estimate:,}) is escalated")


def schema_tax():
    base, more, extra_tools, calls = 5925, 10293, 12, 26
    per = (more - base) / (extra_tools * calls)
    return r(f"{per:.0f}", f"{(more - base) / calls:.0f}", f"{(more - base) / extra_tools:.0f}", f"{more - base:,}")


def kv_7b_4k():
    kv = cm.kv_gb("qwen2.5:7b", 4096, 1)
    need = cm.need_gb("qwen2.5:7b", 4096, 1)
    return r(f"{need:.2f} GB", f"{cm.MODELS['qwen2.5:7b']['weights_gb']:.2f} GB", f"{kv / 2 + cm.MODELS['qwen2.5:7b']['weights_gb']:.2f} GB",
             f"{cm.MODELS['qwen2.5:7b']['weights_gb'] + kv * 8:.2f} GB")


def fit_7b_32k():
    need = cm.need_gb("qwen2.5:7b", 32768, 4)
    usable = 16 - cm.ASSUMPTIONS["mac_reserved_gb"]
    assert need > usable
    return r(f"No: it needs {need:.2f} GB but only {usable} GB is usable",
             f"Yes: the {cm.MODELS['qwen2.5:7b']['weights_gb']} GB of weights fit in {usable} GB",
             f"Yes: it needs {cm.need_gb('qwen2.5:7b', 32768, 1):.2f} GB, under the {usable} GB usable",
             f"No: it needs {cm.need_gb('qwen2.5:14b', 32768, 4):.2f} GB")




def call_cost():
    usage = {"prompt_tokens": 400, "completion_tokens": 20, "prompt_tokens_details": {"cached_tokens": 300}}
    c = cm.call_cost("fake-large", usage)
    return r(f"{c:,.0f}", f"{2 * 7 * 420:,.0f}", f"{2 * 7 * 120:,.0f}", f"{7 * 150:,.0f}")


def cost_ratio():
    large, rules = 7000.0, 3890.1
    ratio = rules / large
    assert ratio <= 0.6
    return r(f"{ratio:.1%} - within the 60 % limit", f"{1 - ratio:.1%} - within the 60 % limit",
             f"{large / rules:.1%} - over the 60 % limit", f"{3807.6 / large:.1%} - within the 60 % limit")


def chi_two_classes():
    stat, df = chi_square({"high": 50, "normal": 50}, {"high": 60, "normal": 40})
    alarm = stat > CRITICAL_99[df]
    assert not alarm
    return r(f"{stat:.2f} - no alarm ({stat:.2f} < {CRITICAL_99[df]})", f"{stat:.2f} - alarm ({stat:.2f} > {CRITICAL_99[df] / 2:.3f})",
             f"{stat / 2:.2f} - no alarm ({stat / 2:.2f} < {CRITICAL_99[df]})", f"{stat * 4:.2f} - alarm ({stat * 4:.2f} > {CRITICAL_99[df]})")


def burn_rate():
    budget_share, window_h, days = 0.05, 6, 30
    rate = budget_share * days * 24 / window_h
    return r(f"{rate:g}", f"{budget_share * days * 24:g}", f"{window_h / (budget_share * days * 24):.2f}", f"{0.02 * days * 24:g}")




# ---------------------------------------------------------------- L500 (lessons 23-27; numbers from the L500 lab modules)
st500 = load("eval_stats", LABS / "L500/24-evaluation-statistics/eval_stats.py")
dp500 = load("decision_planning", LABS / "L500/25-decision-planning/decision_planning.py")


def f4(x):
    return f"{x:.4f}"


def l500_softmax_top():
    e = [math.exp(z) for z in (2.0, 1.0, 0.0)]
    e_half = [math.exp(z / 0.5) for z in (2.0, 1.0, 0.0)]
    return r(f4(e[0] / sum(e)), f4(2 / 3), f4(e_half[0] / sum(e_half)), "0.5000")


def l500_wilson_20of20():
    return r(f4(st500.wilson(20, 20)[0]), f4(st500.wald(20, 20)[0]), f4(0.025 ** (1 / 20)), "0.9500")


def l500_fwer_10():
    return r(f4(st500.fwer_independent(0.05, 10)), "0.5000", "0.0500", f4(st500.fwer_independent(0.005, 10)))


def l500_sample_size_90_80():
    z2 = st500.Z.inv_cdf(0.975)
    zb = st500.Z.inv_cdf(0.8)
    two_sided = math.ceil(((z2 * math.sqrt(0.09) + zb * math.sqrt(0.16)) / 0.1) ** 2)
    half_power = math.ceil((st500.Z.inv_cdf(0.95) * math.sqrt(0.09) / 0.1) ** 2)
    return r(st500.sample_size(0.90, 0.80), two_sided, 100, half_power)


def l500_attempts_half_3():
    return r(f"{dp500.expected_attempts(0.5, 3):.2f}", f"{1 / 0.5:.2f}", "3.00", "1.50")


def l500_breakeven():
    # auto: +2 correct, -40 wrong; review: utility 0.5 always -> 2(1-e) - 40e = 0.5
    return r(f4(1.5 / 42), f4(2 / 40), f4(0.5 / 40), f4(1.5 / 40))


def l500_review_cost():
    n, err, harm, review, catch = 5000, 0.04, 100, 1.0, 0.8
    errors = n * err
    return r(f"{n * review + errors * (1 - catch) * harm:,.0f}", f"{n * review:,.0f}",
             f"{errors * (1 - catch) * harm:,.0f}", f"{catch * errors * harm:,.0f}")


def l500_dk_scale():
    return r(f4(1 / math.sqrt(512 / 8)), f4(1 / math.sqrt(512)), f4(1 / math.sqrt(8)), f4(1 / 64))


def l500_attention_ratio():
    n, d = 2048, 512
    return r(f"{(n * n * d) / (n * d * d):.2f}", f"{(n * d * d) / (n * n * d):.2f}", f"{(n / d) ** 2:.2f}", f"{math.sqrt(n / d):.2f}")


CALCS = {f.__name__: f for f in [
    history_tokens, cumulative_prompt_tokens, retry_messages, steps_sequential, steps_parallel, usage_total,
    cosine_34, dot_vs_cosine, words_budget, bruteforce_ops, overlap_chunk_count, context_share,
    min_cases_for_bar, span_share, model_vs_tool, backoff_range, budget_binding, timeout_worst_case, redteam_rate,
    hybrid_threshold, schema_tax, kv_7b_4k, fit_7b_32k, call_cost, cost_ratio, chi_two_classes,
    burn_rate,
    l500_softmax_top, l500_wilson_20of20, l500_fwer_10, l500_sample_size_90_80, l500_attempts_half_3,
    l500_breakeven, l500_review_cost, l500_dk_scale, l500_attention_ratio]}

# question id -> calculation function (written by the bank's build step; every calculation question must be here)
ID_MAP = {
    'ag-L100-010': 'usage_total',
    'ag-L100-011': 'history_tokens',
    'ag-L100-012': 'cumulative_prompt_tokens',
    'ag-L100-026': 'retry_messages',
    'ag-L100-040': 'steps_sequential',
    'ag-L100-041': 'steps_parallel',
    'ag-L200-004': 'cosine_34',
    'ag-L200-005': 'dot_vs_cosine',
    'ag-L200-006': 'bruteforce_ops',
    'ag-L200-007': 'overlap_chunk_count',
    'ag-L200-023': 'words_budget',
    'ag-L200-024': 'context_share',
    'ag-L300-004': 'min_cases_for_bar',
    'ag-L300-013': 'span_share',
    'ag-L300-014': 'model_vs_tool',
    'ag-L300-023': 'backoff_range',
    'ag-L300-024': 'budget_binding',
    'ag-L300-025': 'timeout_worst_case',
    'ag-L300-043': 'redteam_rate',
    'ag-L400-005': 'hybrid_threshold',
    'ag-L400-006': 'schema_tax',
    'ag-L400-021': 'kv_7b_4k',
    'ag-L400-022': 'fit_7b_32k',
    'ag-L400-023': 'call_cost',
    'ag-L400-024': 'cost_ratio',
    'ag-L400-036': 'chi_two_classes',
    'ag-L400-043': 'burn_rate',
    'ag-L500-002': 'l500_softmax_top',
    'ag-L500-010': 'l500_wilson_20of20',
    'ag-L500-012': 'l500_fwer_10',
    'ag-L500-015': 'l500_sample_size_90_80',
    'ag-L500-019': 'l500_attempts_half_3',
    'ag-L500-026': 'l500_breakeven',
    'ag-L500-032': 'l500_review_cost',
    'ag-L500-038': 'l500_dk_scale',
    'ag-L500-045': 'l500_attention_ratio',
}


def run_snippet(code):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
    return out.getvalue().strip()


def main():
    errors, n_calc, n_code = [], 0, 0
    for lv in ["L100", "L200", "L300", "L400", "L500"]:
        path = TOPIC / "content" / "qbank" / f"{lv}.json"
        if lv == "L500" and not path.exists():
            errors.append("missing content/qbank/L500.json")
            continue
        for q in json.loads(path.read_text(encoding="utf-8")):
            qid, opts, ans = q["id"], q["options"], q["answer"]
            if q["type"] == "calculation":
                n_calc += 1
                fn = CALCS.get(ID_MAP.get(qid, ""))
                if fn is None:
                    errors.append(f"{qid}: calculation without a check function")
                    continue
                res = fn()
                if opts[ans] != res["correct"]:
                    errors.append(f"{qid}: answer {opts[ans]!r} != computed {res['correct']!r}")
                if sum(o == res["correct"] for o in opts) != 1:
                    errors.append(f"{qid}: computed answer appears {sum(o == res['correct'] for o in opts)} times")
            if q.get("code"):
                try:
                    compile(q["code"], qid, "exec")
                except SyntaxError as exc:
                    errors.append(f"{qid}: snippet does not compile: {exc}")
                    continue
                if len(q["code"].splitlines()) > 15:
                    errors.append(f"{qid}: snippet longer than 15 lines")
            if q["type"] == "code-reading":
                n_code += 1
                if not q.get("code"):
                    errors.append(f"{qid}: code-reading without code")
                    continue
                got = run_snippet(q["code"])
                if got != opts[ans]:
                    errors.append(f"{qid}: snippet prints {got!r}, answer is {opts[ans]!r}")
                if sum(o == got for o in opts) != 1:
                    errors.append(f"{qid}: snippet output matches {sum(o == got for o in opts)} options")
    for e in errors:
        print("ERROR", e)
    print(f"checked {n_calc} calculation answers and executed {n_code} code-reading snippets")
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
