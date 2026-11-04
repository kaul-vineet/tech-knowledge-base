"""L600 #05 A robotic-observatory night scheduler: astronomy + simulation + ai-agents. Prints a JSON-lines scorecard.

M1 sky + typed time -> M2 greedy baseline -> M3 local search -> M4 Monte Carlo weather -> M5 agent proposes, code decides
python run_project.py                         (fake local model; exit 1 on any FAIL)
python run_project.py --inject local-as-utc   (failure lab: local wall clock relabelled as UTC before the sky maths)
python run_project.py --real                  (a real local model at LOCAL_MODEL_URL, e.g. Ollama; pendingCi)
"""
import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone

import _kb
import agent_plan
import scheduler
import sky
import validator
import weather
from timeutil import UtcInstant

RUNS, SEED, MARGIN = 1000, 7, 0.15  # fitness: optimised >= greedy x 1.15 over 1000 weather runs
CARD = []


def check(name, ok, **detail):
    CARD.append({"check": name, "pass": bool(ok), **detail})
    print(json.dumps(CARD[-1]))


def wblocks(r, key):
    return [(s, n, r["reqs"][i].priority) for s, n, i in r[key]]


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--inject", choices=["local-as-utc"])
    a.add_argument("--real", action="store_true")
    args = a.parse_args(argv)
    r = scheduler.build(seed=2026, fault=args.inject)
    reqs, slots = r["reqs"], r["slots"]
    viol = {k: validator.validate(validator.rows_from_blocks(r[k], reqs, slots), reqs, slots) for k in ("greedy", "local")}
    feasible = [q.name for q, row in zip(reqs, r["ok"]) if row.any()]
    check("M1 sky + typed time", len(slots) == 64 and slots[0].utc.iso() == "2026-11-19T13:20:00Z",
          dark_local=f"{slots[0].local:%H:%M}-{slots[-1].local:%H:%M}", slots=len(slots), feasible=len(feasible))
    check("M2 greedy baseline", not viol["greedy"], expected_value=round(r["greedy_value"], 3),
          plan=[x["target"] for x in r["greedy_rows"]], violations=viol["greedy"][:2])
    check("M3 local search", not viol["local"] and r["local_value"] >= r["greedy_value"],
          expected_value=round(r["local_value"], 3), plan=[x["target"] for x in r["local_rows"]], violations=viol["local"][:2])
    clear = weather.clear_matrix(RUNS, len(slots), SEED)
    g, lo = weather.realised(wblocks(r, "greedy"), clear), weather.realised(wblocks(r, "local"), clear)
    (gm, gh), (lm, lh), (dm, dh) = weather.summary(g), weather.summary(lo), weather.summary(lo - g)
    check("M4 Monte Carlo weather", abs(lm - r["local_value"]) <= lh and abs(gm - r["greedy_value"]) <= gh,
          runs=RUNS, greedy=f"{gm:.3f}+/-{gh:.3f}", local=f"{lm:.3f}+/-{lh:.3f}", greedy_better_nights=float((g > lo).mean()))
    server, url = (None, None) if args.real else _kb.fake_model_server.start_in_thread()
    try:
        proposal = agent_plan.ask(agent_plan.plan_prompt(reqs, slots), url)
        verdict = agent_plan.decide(proposal, r["local"], reqs, slots)
        ist = timezone(timedelta(hours=5, minutes=30))  # a VALID agent plan written in local time WITH its offset
        valid_text = "\n".join(f"PLAN {x['target']} {datetime.fromisoformat(x['start_utc'].replace('Z', '+00:00')).astimezone(ist).isoformat()}"
                               for x in r["local_rows"])
        verdict_ok = agent_plan.decide(valid_text, r["local"], reqs, slots)
        facts = agent_plan.explain_facts(r)
        shown, text = agent_plan.checked_explanation(agent_plan.ask(agent_plan.explain_prompt(facts), url), facts, reqs)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    check("M5 agent proposes, code decides", verdict_ok["adopted"] == "agent" and (args.real or verdict["adopted"] == "optimiser"),
          agent_reasons=verdict["reasons"][:3], valid_offset_plan=verdict_ok["adopted"], explanation_published=shown)
    # seams
    with_types = all(_raises(f) for f in (lambda: UtcInstant(datetime(2026, 11, 19, 18, 50)),
                                          lambda: UtcInstant(datetime(2026, 11, 19, 18, 50, tzinfo=ist)),
                                          lambda: sky.alt_deg(reqs[0], datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc))))
    route = max(abs(sky.alt_deg(q, s.utc) - validator.alt_deg_lst(q, s.utc)) for q in reqs for s in slots[::8])
    check("SEAM time astronomy<->scheduler", with_types and route < 0.02 and not viol["greedy"] and not viol["local"],
          types_enforced=with_types, max_route_diff_deg=round(route, 4))
    bad = agent_plan.decide("PLAN Vega 2026-11-19T18:50\nPLAN Sirius 2026-11-19T13:20:00Z", r["local"], reqs, slots)
    gate = agent_plan.checked_explanation("Expected value 12.0, guaranteed.", facts, reqs)[0]
    check("SEAM agent<->validator", not bad["agent_ok"] and any("ISO 8601" in x for x in bad["reasons"])
          and any("airmass" in x for x in bad["reasons"]) and not gate, rejected=bad["reasons"], invented_number_blocked=not gate)
    worst = max(abs(clear[:, s:s + n].all(1).mean() - weather.p_complete(n)) / math.sqrt(
        weather.p_complete(n) * (1 - weather.p_complete(n)) / RUNS) for s, n, _ in r["local"])
    check("SEAM weather<->promises", worst <= 3.0, worst_z=round(worst, 2),
          promises={x["target"]: x["p_complete"] for x in r["local_rows"]})
    transit = max(abs(validator.alt_from_hour_angle(0.0, q.dec_deg, sky.SITE["lat_deg"]) - (90 - abs(sky.SITE["lat_deg"] - q.dec_deg)))
                  for q in reqs)
    check("SEAM units deg/h/rad", transit < 1e-9 and route < 0.02, transit_identity_err=transit)
    # fitness functions
    worst_x = max([x["max_airmass"] for x in r["greedy_rows"] + r["local_rows"]] + [0])
    check("FF1 no observation above airmass 2.0", not viol["greedy"] and not viol["local"] and worst_x <= sky.MAX_AIRMASS,
          max_airmass=worst_x)
    check("FF2 value >= greedy x 1.15 (1000 runs)", lm >= (1 + MARGIN) * gm and dm - dh > 0,
          ratio=round(lm / gm, 3), paired_diff=f"{dm:.3f}+/-{dh:.3f}")
    r2 = scheduler.build(seed=2026, fault=args.inject)
    same = scheduler.plan_hash(r2["local_rows"]) == scheduler.plan_hash(r["local_rows"]) and \
        (weather.clear_matrix(RUNS, len(slots), SEED) == clear).all()
    check("FF3 deterministic for a seed", same, plan_hash=scheduler.plan_hash(r["local_rows"]))
    passed = sum(c["pass"] for c in CARD)
    print(json.dumps({"scorecard": "PASS" if passed == len(CARD) else "FAIL", "passed": passed, "total": len(CARD)}))
    return 0 if passed == len(CARD) else 1


def _raises(fn):
    try:
        fn()
    except TypeError:
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())
