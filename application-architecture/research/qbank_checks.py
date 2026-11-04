"""Recompute every calculation answer and execute every code-reading snippet in content/qbank/*.json (L100-L500).

Run from anywhere: python research/qbank_checks.py   -> prints OK and exits 0, or lists problems and exits 1.
Each calculation is recomputed here from the lesson's numbers (independently of how the bank was written);
each code-reading snippet is executed and its printed output must equal the keyed answer and no distractor.
"""
import base64
import contextlib
import hashlib
import io
import json
import math
import pathlib
import secrets
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

QBANK = pathlib.Path(__file__).resolve().parent.parent / "content" / "qbank"
LEVELS = ["L100", "L200", "L300", "L400", "L500"]


def nearest_rank(values, p):  # same definition as labs/L300/15-slo-error-budgets/slo.py
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * p / 100) - 1)]


def burn_rate(bad_ratio, slo):
    return bad_ratio / (1 - slo)


def budget_share(burn, window_h, period_h=30 * 24):
    return burn * window_h / period_h


def instances_n_plus_1(peak_rps, capacity_rps, headroom=0.8):
    return math.ceil(peak_rps / (capacity_rps * headroom)) + 1


def usd_per_million(instances, avg_rps, usd_per_hour=0.10):
    return round(instances * usd_per_hour / (avg_rps * 3600) * 1_000_000, 2)


# ---------- lesson-specific recomputations ----------
def l100_limit():
    active, failed = [], None
    for book in ["b1", "b2", "b3", "b4"]:
        if failed is None and len(active) >= 3:
            failed = book
            continue
        if failed is None:
            active.append(book)
    return f"{failed} fails; m1 has {len(active)} active loans"


def l100_post_ids():
    store, replies = [], []
    for book in ["b1", "b1", "b2"]:
        if book in store:
            replies.append("409")
        else:
            store.append(book)
            replies.append(f"201 id={len(store)}")
    return ", ".join(replies)


def l100_config_errors():
    env = {"LOANS_PORT": "0", "LOANS_MAX_ACTIVE_LOANS": "51", "LOANS_LOG_LEVEL": "info", "LOANS_DB_PATH": " "}
    errors = 0
    errors += not 1 <= int(env["LOANS_PORT"]) <= 65535
    errors += not 1 <= int(env["LOANS_MAX_ACTIVE_LOANS"]) <= 50
    errors += env["LOANS_LOG_LEVEL"].upper() not in ("DEBUG", "INFO", "WARNING", "ERROR")
    errors += env["LOANS_DB_PATH"].strip() == ""
    return str(errors)


def l200_first_overdue():
    borrowed, day = date(2026, 10, 1), date(2026, 10, 1)
    while (day - borrowed).days <= 14:
        day += timedelta(days=1)
    return day.isoformat()


def l200_relay_attempts():
    attempts = 0
    for _run in range(5):
        if attempts < 3:  # dead-lettered rows (attempts >= 3) are skipped
            attempts += 1
    return str(attempts)


def l200_s256():
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode().rstrip("=")


def l200_pyramid():
    ratio = 613 / 0.03
    return f"about 10^{round(math.log10(ratio))} ({ratio:,.0f})"


def l200_budgets():
    budgets, means = {"unit": 10, "integration": 1000, "e2e": 10000}, {"unit": 42, "integration": 830, "e2e": 12500}
    return ", ".join(layer for layer in budgets if means[layer] > budgets[layer])


def l300_lag():
    lags = [4, 9, 11, 12, 15, 18, 22, 35, 53, 58]
    return f"p50 {nearest_rank(lags, 50)} ms, p90 {nearest_rank(lags, 90)} ms"


def l300_tail():
    ms = [80] * 96 + [2800] * 4
    return f"mean {sum(ms) / len(ms):.1f}, p95 {nearest_rank(ms, 95)}, p99 {nearest_rank(ms, 99)} ms"


def l300_detection_minutes():
    # SRE Workbook: time to fire = (1 - SLO) / error_ratio * window * threshold
    return f"{(1 - 0.99) / 0.197 * 60 * 14.4:.1f} minutes"


def l300_overdue():
    return f"{(11 - 1) // 2} and {(337 - 1) // 2}"


def l400_cutover():
    comparisons, mismatches, errors = 2000, 108, 0
    rate = mismatches / comparisons
    ready = comparisons >= 1000 and rate <= 0.001 and errors == 0
    return f"ready {ready}: mismatch rate {rate:.2%} > 0.10%"


def l400_mismatch_days():
    def legacy(days):
        fine = Decimal("0.25") * max(0, days - 2) / 2
        return str(min(fine, Decimal("10.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def service(days):
        return f"{round(min(0.25 * max(0, days - 2) * 0.5, 10.0), 2):.2f}"

    return " and ".join(str(d) for d in range(3, 11) if legacy(d) != service(d))


def l400_leak():
    libraries, overdue_each = 20, 14
    rows = libraries * overdue_each
    return f"{rows} rows, {rows - overdue_each} from other libraries"


def l400_base_sizing():
    raw_capacity = 4 / (45.2 / 1000)  # c / S
    return f"{math.ceil(40 / raw_capacity)} instance, utilization {120 / raw_capacity:.2f}"


def l400_email():
    in_flight = 120 * 0.20 * (150 / 1000)
    return f"{in_flight:.1f} in flight, {math.ceil(in_flight / 0.8)} slots"


def l400_availability():
    sli = (615 - 1) / 615
    return f"{'Yes' if sli >= 0.999 else 'No'}: {sli:.4%} is {'above' if sli >= 0.999 else 'below'} 99.9%"



# ---------- L500 (theory) recomputations ----------
def l500_martin_dn(ca, ce, classes, abstract):
    i, a = ce / (ca + ce), abstract / classes
    return f"{abs(a + i - 1):.2f}"


def l500_series(*avails):
    return math.prod(avails)


def l500_parallel(*avails):
    return 1 - math.prod(1 - a for a in avails)


def l500_fixed_states(n):  # at most one holder; everyone else idle or checked (lesson 25, P25-6)
    return str(2 ** n + n * 2 ** (n - 1))


CALC = {
    "aa-L100-009": ("third repository", lambda: str(5 * 3 + 1 + 1)),
    "aa-L100-011": ("max_active_per_member=3", l100_limit),
    "aa-L100-027": ("every declared response", lambda: str(len([200, 201, 400, 409, 200, 404]))),
    "aa-L100-028": ("len(LOANS) + 1", l100_post_ids),
    "aa-L100-031": ("How many errors", l100_config_errors),
    "aa-L200-006": ("StoreContract", lambda: str(4 * 3)),
    "aa-L200-012": ("first overdue", l200_first_overdue),
    "aa-L200-024": ("dead-letters", l200_relay_attempts),
    "aa-L200-028": ("code_challenge", l200_s256),
    "aa-L200-029": ("token_urlsafe(32)", lambda: str(len(secrets.token_urlsafe(32)))),
    "aa-L200-038": ("power of ten", l200_pyramid),
    "aa-L200-041": ("--budget", l200_budgets),
    "aa-L300-005": ("lag_ms values", l300_lag),
    "aa-L300-013": ("Little's law", lambda: f"{(8 / 0.25) * 1.0:.0f}"),
    "aa-L300-029": ("2 server errors", lambda: f"{burn_rate(2 / 1000, 0.999):.1f}"),
    "aa-L300-030": ("burns at rate 14.4", lambda: f"{budget_share(14.4, 1):.0%}"),
    "aa-L300-031": ("burn rate 6 over 6 hours", lambda: f"{budget_share(6, 6):.0%}"),
    "aa-L300-032": ("latency burn rate", lambda: f"{burn_rate(0.197, 0.99):.1f}"),
    "aa-L300-033": ("SRE Workbook formula", l300_detection_minutes),
    "aa-L300-034": ("96 take 80 ms", l300_tail),
    "aa-L300-041": ("{10: 11, 500: 337}", l300_overdue),
    "aa-L400-001": ("108 mismatches", l400_cutover),
    "aa-L400-003": ("0.125 per chargeable day", l400_mismatch_days),
    "aa-L400-009": ("20 libraries", l400_leak),
    "aa-L400-032": ("Little's law", lambda: f"{120 * 45.2 / 1000:.1f}"),
    "aa-L400-033": ("up to 75 req/s", lambda: str(instances_n_plus_1(120, 75))),
    "aa-L400-034": ("35 req/s", lambda: str(instances_n_plus_1(120, 35))),
    "aa-L400-035": ("0.10 USD per hour",
                    lambda: f"{usd_per_million(3, 40):.2f} and {usd_per_million(6, 40):.2f} USD"),
    "aa-L400-036": ("800 libraries", lambda: f"{instances_n_plus_1(240, 75)} without cache, "
                                             f"{instances_n_plus_1(240, 105)} with cache"),
    "aa-L400-037": ("offered utilization", l400_base_sizing),
    "aa-L400-038": ("sender slots", l400_email),
    "aa-L400-045": ("615 requests", l400_availability),
    "aa-L500-004": ("Ca = 6, Ce = 2", lambda: l500_martin_dn(6, 2, 5, 2)),
    "aa-L500-005": ("Ca = 5, Ce = 1", lambda: f"{abs(0 + 1 / 6 - 1) / math.sqrt(2):.3f}"),
    "aa-L500-011": ("99.9 %, 99.95 % and 99.99 %", lambda: f"{l500_series(0.999, 0.9995, 0.9999):.2%}"),
    "aa-L500-013": ("99.9 % availability SLO over 30 days", lambda: f"{(1 - 0.999) * 30 * 24 * 60:.1f} min"),
    "aa-L500-014": ("MTTF of 500 h", lambda: f"{500 / (500 + 2):.2%}"),
    "aa-L500-016": ("shared configuration store", lambda: f"{l500_series(0.999, l500_parallel(0.995, 0.995)):.3%}"),
    "aa-L500-024": ("three members", lambda: str(3 ** 3)),
    "aa-L500-025": ("four members", lambda: l500_fixed_states(4)),
}


def run_snippet(code):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__qbank_snippet__"})
    return out.getvalue().strip()


def main():
    problems, calc_ok, run_ok, compiled = [], 0, 0, 0
    seen_calc = set()
    for level in LEVELS:
        for q in json.loads((QBANK / f"{level}.json").read_text(encoding="utf-8")):
            qid, keyed = q["id"], q["options"][q["answer"]]
            others = [o for i, o in enumerate(q["options"]) if i != q["answer"]]
            if q["type"] == "calculation":
                if qid not in CALC:
                    problems.append(f"{qid}: calculation without a recomputation in CALC")
                    continue
                needle, compute = CALC[qid]
                seen_calc.add(qid)
                expected = compute()
                if needle not in q["question"]:
                    problems.append(f"{qid}: CALC entry does not match the question (missing {needle!r})")
                elif keyed != expected:
                    problems.append(f"{qid}: keyed {keyed!r}, recomputed {expected!r}")
                elif expected in others:
                    problems.append(f"{qid}: a distractor equals the computed answer")
                else:
                    calc_ok += 1
            if q["type"] == "code-reading" or (q.get("code") and "print" in q["question"].lower()):
                try:
                    printed = run_snippet(q["code"])
                except Exception as exc:  # a snippet that crashes cannot have a printed answer
                    problems.append(f"{qid}: snippet raised {exc!r}")
                    continue
                if printed != keyed:
                    problems.append(f"{qid}: snippet prints {printed!r}, keyed {keyed!r}")
                elif printed in others:
                    problems.append(f"{qid}: a distractor equals the printed output")
                else:
                    run_ok += 1
            elif q.get("code"):
                try:  # debugging snippets are not run (they show a fragment), but must be valid Python
                    compile(q["code"], qid, "exec")
                    compiled += 1
                except SyntaxError as exc:
                    problems.append(f"{qid}: snippet does not compile: {exc}")
    for qid in sorted(set(CALC) - seen_calc):
        problems.append(f"{qid}: CALC entry has no calculation question")
    print(f"calculations recomputed: {calc_ok}; code-reading snippets executed: {run_ok}; "
          f"other snippets compiled: {compiled}")
    for problem in problems:
        print("PROBLEM", problem)
    print("OK" if not problems else f"FAILED ({len(problems)} problems)")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
