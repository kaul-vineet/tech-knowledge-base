"""Lesson 21 demo: load model -> Little's law -> benchmark per instance -> options -> decision + cost.

Run: python app.py [--solution]    writes out/capacity.jsonl (one JSON line per option)
"""
import argparse
import importlib.util
import json
import math
import pathlib

import capacity
import l300_log

HERE = pathlib.Path(__file__).resolve().parent
EMAIL_MS = 150.0  # stated in the brief: relay time per confirmation email


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan(cap):
    """Every number of the capacity plan, computed by code (the agent memo is checked against this)."""
    model = cap.load_model(l300_log.records())
    hit = cap.lru_hit_ratio()
    options = {"sync email": cap.with_sync_email(model, EMAIL_MS), "async email": model,
               "async email + cache": cap.with_cache(model, hit)}
    rows = []
    for name, m in options.items():
        bench = cap.benchmark(m)
        n = cap.instances_needed(m, bench["capacity_rps"])
        at_peak = cap.simulate(m["peak_rps"] / n, [ms for _, ms in m["requests"]])  # all instances up
        one_down = cap.simulate(m["peak_rps"] / max(n - 1, 1), [ms for _, ms in m["requests"]])
        rows.append({"option": name, "mean_service_ms": m["mean_service_ms"], "capacity_rps": bench["capacity_rps"],
                     "instances": n, "p99_at_peak_ms": at_peak["p99_ms"], "p99_one_down_ms": one_down["p99_ms"],
                     "cost_per_million_usd": cap.cost_per_million(n, m["avg_rps"])})
    in_flight_email = cap.littles_law(model["peak_rps"] * model["mix"]["POST /loans"], EMAIL_MS)
    return {"model": {k: v for k, v in model.items() if k != "requests"}, "cache_hit_ratio": hit,
            "in_flight_at_peak": round(cap.littles_law(model["peak_rps"], model["mean_service_ms"]), 1),
            "email_in_flight": round(in_flight_email, 1),
            "email_senders": math.ceil(in_flight_email / cap.HEADROOM), "options": rows}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", action="store_true")
    cap = load(HERE / "solution" / "capacity.py", "capacity_solution") if parser.parse_args(argv).solution else capacity
    p = plan(cap)
    print(f"load model : {p['model']}")
    print(f"Little's law: {p['model']['peak_rps']} req/s x {p['model']['mean_service_ms']} ms = "
          f"{p['in_flight_at_peak']} requests in flight at peak; emails {p['email_in_flight']} in flight -> "
          f"{p['email_senders']} sender slots")
    (HERE / "out").mkdir(exist_ok=True)
    with open(HERE / "out" / "capacity.jsonl", "w", encoding="utf-8") as f:
        for row in p["options"]:
            f.write(json.dumps(row) + "\n")
            print(json.dumps(row))
    return p


if __name__ == "__main__":
    main()
