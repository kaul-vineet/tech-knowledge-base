"""Try it (lesson 21): grow to 800 libraries with and without the cache; run without the spare instance.

Run: python try_it.py
"""
import l300_log
from app import HERE, load


def main():
    cap = load(HERE / "solution" / "capacity.py", "capacity_solution")
    records = l300_log.records()
    model = cap.load_model(records)
    grown_rates = {k: v for k, v in cap.load_model(records, libraries=800).items() if k.endswith("rps")}
    for label, m in [("async email", model), ("async email + cache", cap.with_cache(model, cap.lru_hit_ratio()))]:
        n = cap.instances_needed({**m, **grown_rates}, cap.benchmark(m)["capacity_rps"])
        print(f"[1] 800 libraries (peak {grown_rates['peak_rps']} req/s), {label}: {n} instances, "
              f"{cap.cost_per_million(n, grown_rates['avg_rps'])} USD per million requests")
    n = cap.instances_needed(model, cap.benchmark(model)["capacity_rps"]) - 1  # no spare
    one_down = cap.simulate(model["peak_rps"] / (n - 1), [ms for _, ms in model["requests"]])
    print(f"[2] {n} instances (no spare), one down at peak: {one_down['rate']:.0f} req/s on the survivor, "
          f"utilization {one_down['utilization']}, p99 {one_down['p99_ms']} ms")


if __name__ == "__main__":
    main()
