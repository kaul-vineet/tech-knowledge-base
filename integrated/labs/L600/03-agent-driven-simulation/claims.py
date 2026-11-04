"""Claim checker: every sentence of the agent's summary against the registry.

A sentence passes only if (1) every number in it matches a fact of the experiment it cites ([exp-...]) at the
precision it is written with, and (2) its wording agrees with the computed verdict: "significant" needs a verdict
"significant ..." in the same direction; a direction word (cut, improved, faster...) needs "significant" or an
explicit "not significant"/"inconclusive". Rejected sentences are replaced by a code-written line from the facts.
"""
import re

CITE = re.compile(r"\[(exp-[0-9a-f]+)\]")
NUMBER = re.compile(r"(?<![\w.])[-\u2212]?\d+(?:\.\d+)?")
SIGNIFICANT = re.compile(r"\bsignifican", re.I)
NEGATED = re.compile(r"\b(not|no)\s+(statistically\s+)?significan|\binconclusive\b", re.I)
DOWN = re.compile(r"\b(cut|cuts|reduc\w*|lower\w*|faster|improv\w*|shorter|drop\w*|decreas\w*)\b", re.I)
UP = re.compile(r"\b(rais\w*|higher|slower|wors\w*|longer|increas\w*)\b", re.I)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def numbers(sentence):
    return [t.replace("\u2212", "-") for t in NUMBER.findall(CITE.sub("", sentence))]


def trace(token, facts):
    """Facts whose value, rounded to the token's decimals, equals the token (sign checked by wording)."""
    decimals = len(token.split(".")[1]) if "." in token else 0
    want = abs(float(token))
    return [k for k, f in facts.items() if isinstance(f["value"], (int, float))
            and abs(abs(f["value"]) - want) <= 0.5 * 10 ** -decimals + 1e-9]


def check_sentence(sentence, registry):
    cites, nums = CITE.findall(sentence), numbers(sentence)
    exps = [registry.experiment(c) for c in cites]
    if any(e is None for e in exps):
        return {"ok": False, "reason": f"cites an experiment that is not in the registry: {cites}", "traces": {}}
    facts = {k: v for e in exps for k, v in e["facts"].items()}
    if nums and not cites:
        return {"ok": False, "reason": f"untraced numbers {nums}: no experiment cited", "traces": {}}
    traces = {t: trace(t, facts) for t in nums}
    missing = [t for t, hits in traces.items() if not hits]
    if missing:
        return {"ok": False, "reason": f"numbers not in the cited results: {missing}", "traces": traces}
    verdict = facts.get("verdict", {}).get("value")
    if verdict is not None:
        negated, direction = NEGATED.search(sentence), "down" if DOWN.search(sentence) else "up" if UP.search(sentence) else None
        if SIGNIFICANT.search(sentence) and not negated:
            if verdict == "inconclusive":
                return {"ok": False, "reason": f"claims significance; computed verdict is inconclusive "
                                               f"(95% CI of the difference includes 0 or n < 10)", "traces": traces}
            if direction and verdict != {"down": "significant decrease", "up": "significant increase"}[direction]:
                return {"ok": False, "reason": f"direction contradicts verdict {verdict!r}", "traces": traces}
        elif negated and verdict != "inconclusive":
            return {"ok": False, "reason": f"says not significant; computed verdict is {verdict!r}", "traces": traces}
        elif direction and not negated:
            return {"ok": False, "reason": "claims a direction without saying whether it is significant", "traces": traces}
    return {"ok": True, "reason": "", "traces": traces}


def code_line(exp_id, registry):
    f = {k: v["value"] for k, v in registry.experiment(exp_id)["facts"].items()}
    if "verdict" not in f:
        ranked = sorted((k for k in f if k != "size"), key=lambda k: -f[k])
        return f"Code result [{exp_id}]: screening order " + ", ".join(f"{k} {f[k]:.2f}" for k in ranked) + "."
    return (f"Code result [{exp_id}]: mean wait {f['baseline_mean']:.2f} vs {f['candidate_mean']:.2f} min, "
            f"difference {f['difference']:.2f} min with 95% CI from {f['difference_low']:.2f} to "
            f"{f['difference_high']:.2f}, n = {f['replications']} per arm: {f['verdict']}.")


def review(summary, registry):
    """Returns (rows, published_text). rows: one per sentence with ok/reason/traces."""
    rows, out = [], []
    for s in sentences(summary):
        r = {"sentence": s, **check_sentence(s, registry)}
        rows.append(r)
        if r["ok"]:
            out.append(s)
        else:
            cited = [c for c in CITE.findall(s) if registry.experiment(c)]
            out += [code_line(c, registry) for c in cited]  # uncited invented numbers are simply dropped
    return rows, " ".join(dict.fromkeys(out))


def traced_runs(text, registry):
    """For the fitness function: (numbers found, numbers traced to >= 1 registered run)."""
    known, found, ok = registry.run_ids(), 0, 0
    for s in sentences(text):
        exps = [registry.experiment(c) for c in CITE.findall(s)]
        facts = {k: v for e in exps if e for k, v in e["facts"].items()}
        for t in numbers(s):
            found += 1
            ok += any(set(facts[k]["runs"]) and set(facts[k]["runs"]) <= known for k in trace(t, facts))
    return found, ok
