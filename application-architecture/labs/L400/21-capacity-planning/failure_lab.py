"""Lesson 21 failureLab: size on the average rate at 100 % utilization, then meet the daily peak.

Run: python failure_lab.py
"""
import capacity as base
import l300_log
from app import HERE, load


def main():
    solution = load(HERE / "solution" / "capacity.py", "capacity_solution")
    model = base.load_model(l300_log.records())
    service = [ms for _, ms in model["requests"]]
    bench = base.benchmark(model)
    print(f"demand: avg {model['avg_rps']} req/s, peak {model['peak_rps']} req/s; one instance meets the SLO up to "
          f"{bench['capacity_rps']} req/s; raw c/S = {base.WORKERS / (model['mean_service_ms'] / 1000):.1f} req/s")
    for label, cap in [("base    ", base), ("solution", solution)]:
        n = cap.instances_needed(model, bench["capacity_rps"])
        peak = base.simulate(model["peak_rps"] / n, service)
        down = base.simulate(model["peak_rps"] / max(n - 1, 1), service) if n > 1 else peak
        print(f"{label}: {n} instance(s) -> at peak {peak['rate']:.0f} req/s each, utilization {peak['utilization']}, "
              f"p99 {peak['p99_ms']} ms; one instance down: p99 {down['p99_ms']} ms (SLO {base.SLO_P99_MS} ms)")


if __name__ == "__main__":
    main()
