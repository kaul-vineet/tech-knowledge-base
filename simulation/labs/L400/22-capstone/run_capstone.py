"""L400 capstone: a digital twin of a service centre - from call logs to a governed staffing decision.

M1 input modelling -> M2 DES core verified -> M3 calibration + holdout validation -> M4 sensitivity + staffing
optimisation under the SLA -> M5 parallel replications + live-demand twin -> M6 governance pack + agent explanation.
Deterministic code decides every step; the optional local model only explains. Prints a JSON-lines scorecard.
python run_capstone.py            (agent assist with the fake model; add --real-model to use LOCAL_MODEL_URL)
"""
import argparse
import json
import math
import tempfile
from pathlib import Path

import numpy as np

import agent_explain
import centre
import demand_twin
import governance_pack
import make_data
import pipeline
import runner

HERE = Path(__file__).resolve().parent
REPS_DAY = 24  # full-day replications for plan validation (parallel, checkpointed)


def score(milestone, passed, **measures):
    line = {"milestone": milestone, "pass": bool(passed), **measures}
    print(json.dumps(line))
    return line


def verify_des():
    """M2: degenerate case = M/M/3 with no abandonment, where Erlang C is exact."""
    runs = [centre.simulate([2.0] * 100, [3] * 100, 1.0, None, 1e9, seed=s) for s in range(4)]
    sim_sl = np.mean([h["sl"] for run in runs for h in run[1:]])  # 100-hour runs: queue waits are autocorrelated
    r = pipeline.mmc_queue.erlang_c(3, 2.0, 1.0)
    exact_sl = 1 - r["P_wait"] * math.exp(-(3 - 2.0) * centre.SL_MIN)
    same = centre.simulate([3.0], [10], 4.0, 0.8, 3.0, seed=7) == centre.simulate([3.0], [10], 4.0, 0.8, 3.0, seed=7)
    return round(float(sim_sl), 4), round(exact_sl, 4), same


def validate_day(rates, staff, inp, patience, workers, tmp):
    """M5a: the hour-by-hour plan simulated as ONE day with carry-over, 24 reps, parallel; then crash + resume."""
    tasks = [((rep,), rates, staff, inp["mean_service"], inp["cv"], patience) for rep in range(REPS_DAY)]
    clean, resumed = tmp / "clean.db", tmp / "resumed.db"
    runner.run(clean, tasks, workers=workers)
    try:
        runner.run(resumed, tasks, workers=1, crash_after=10)
    except runner.Crash:
        runner.run(resumed, tasks, workers=1)
    return runner.hourly_summary(clean), runner.checksum(clean) == runner.checksum(resumed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--real-model", action="store_true")
    args, card = ap.parse_args(), governance_pack.load_card()
    lines = []
    inp = pipeline.model_inputs(pipeline.history())
    rate_err = max(abs(a - b) / b for a, b in zip(inp["rates"], make_data.TRUE_RATES))
    lines.append(score("M1 input modelling", inp["service_dist"] == "lognormal" and rate_err < 0.10,
                       service=inp["service_dist"], ks=inp["ks_all"], max_rate_error=round(rate_err, 3)))
    sim_sl, exact_sl, same = verify_des()
    lines.append(score("M2 DES core verified", abs(sim_sl - exact_sl) < 0.01 and same,
                       sl_sim=sim_sl, sl_erlang_c=exact_sl, reproducible=same))
    patience, sse = pipeline.calibrate(inp)
    val = pipeline.validate(inp, patience)
    flat = [p for p, v in sse.items() if v <= 1.2 * min(sse.values())]
    lines.append(score("M3 calibration + holdout validation", val["sl_mae_pp"] <= 3 and val["abandon_mae_pp"] <= 2,
                       patience_min=patience, patience_plausible=[min(flat), max(flat)], **val))
    staff = pipeline.plan(inp["rates"], inp, patience)
    erlang = [pipeline.erlang_c_agents(r, inp["mean_service"]) for r in inp["rates"]]
    elastic = pipeline.sensitivity(inp, patience, staff)
    erlang_day = pipeline.day_kpis(inp, patience, erlang, seed0=700)  # option B judged by the same simulation
    with tempfile.TemporaryDirectory() as tmp:
        (sl, low, ab), resumable = validate_day(inp["rates"], staff, inp, patience, args.workers, Path(tmp))
    lines.append(score("M4 sensitivity + staffing under SLA", min(low) >= pipeline.SL_TARGET
                       and max(ab) <= pipeline.ABANDON_MAX,
                       plan=staff, agent_hours=sum(staff), erlang_c_hours=sum(erlang), flat_hours=12 * max(erlang),
                       erlang_c_day_abandon_max=round(float(max(erlang_day["abandon"])), 3),
                       elasticity_peak_sl=elastic, day_sl_min_low=round(float(min(low)), 3),
                       day_abandon_max=round(float(max(ab)), 3)))
    tw, alarms = demand_twin.replay(inp["rates"])
    alarm = alarms[0] if alarms else None
    from_h = math.ceil((alarm["t_min"] + 1) / 60) if alarm else 12
    surged = [r * alarm["m"] if h >= from_h else r for h, r in enumerate(inp["rates"])] if alarm else inp["rates"]
    replan = staff[:from_h] + pipeline.plan(surged[from_h:], inp, patience)
    truth = [r * (make_data.SURGE if h >= make_data.SURGE_FROM_H else 1) for h, r in enumerate(make_data.TRUE_RATES)]
    static_sl = pipeline.day_kpis(dict(inp, rates=truth), patience, staff)["sl"]
    twin_sl = pipeline.day_kpis(dict(inp, rates=truth), patience, replan)["sl"]
    delay = alarm["t_min"] - 60 * make_data.SURGE_FROM_H if alarm else None
    lines.append(score("M5 parallel replications + live twin", resumable and delay is not None and delay <= 90
                       and min(twin_sl[from_h:]) >= 0.75,
                       resume_identical=resumable, alarm_delay_min=delay, m_at_alarm=alarm and alarm["m"],
                       replan_from=f"{8 + from_h}:00", extra_agent_hours=sum(replan) - sum(staff),
                       static_sl_after=round(float(min(static_sl[from_h:])), 3),
                       twin_sl_after=round(float(min(twin_sl[from_h:])), 3)))
    ev = {"inputs": inp, "validation": val}
    findings, flags = governance_pack.check(card, ev), governance_pack.review_flags(card, surged)
    facts = {"plan_agent_hours": sum(staff), "erlang_c_agent_hours": sum(erlang), "peak_agents": max(staff),
             "peak_hour": "11:00", "alarm_clock": f"{8 + alarm['t_min'] // 60}:{alarm['t_min'] % 60:02d}" if alarm else "none",
             "extra_agent_hours": sum(replan) - sum(staff), "saving_percent": round(100 * (1 - sum(staff) / sum(erlang)), 1)}
    server, url = (None, None)
    if not args.real_model:
        import fake_model_server
        agent_explain.use_fake_rule(fake_model_server)
        server, url = fake_model_server.start_in_thread()
    try:
        exp = agent_explain.explain(facts, base_url=url)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    lines.append(score("M6 governance pack + agent explanation", not findings, card_findings=findings,
                       review_flags=flags, agent_unverified=exp["unverified"], agent_publish=exp["publish"],
                       decision=f"{sum(replan)} agent-hours: plan {replan}"))
    passed = sum(line["pass"] for line in lines)
    final = {"scorecard": "PASS" if passed == len(lines) else "FAIL", "passed": passed, "total": len(lines)}
    print(json.dumps(final))
    (HERE / "scorecard.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines + [final]), encoding="utf-8")


if __name__ == "__main__":  # required with 'spawn' (runner uses a process pool)
    main()
