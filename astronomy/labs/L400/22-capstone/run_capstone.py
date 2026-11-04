"""L400 capstone: an exoplanet transit search - synthetic TESS-like light curves to a vetted, fitted report.

M1 load + detrend -> M2 BLS-lite search -> M3 vetting -> M4 MCMC fit (lesson 15) -> M5 provenance and
reproducibility (lesson 16) -> M6 agent explanation (agent explains, code decides). Prints a JSON-lines scorecard.
python run_capstone.py            (fake model for M6; --real-model uses LOCAL_MODEL_URL / LOCAL_MODEL)
"""
import argparse
import functools
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import agent_explain
import make_data
import pipeline

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


@functools.lru_cache(maxsize=1)
def analyse_all():
    """Run the whole search once per process (tests share it). Returns {star: result} and provenance records."""
    if not (DATA / "S12.csv").exists():
        make_data.write(DATA)
    results, prov = {}, []
    for star in sorted(make_data.STARS):
        path = DATA / f"{star}.csv"
        t, f, _ = pipeline.load(path)
        flat = pipeline.detrend(t, f)
        _, cand = pipeline.bls(t, flat)
        flat = pipeline.detrend(t, f, mask=pipeline.in_transit(t, cand))  # re-detrend with the transit masked
        verdict, reasons = pipeline.vet(t, flat, cand)
        rms = 1.4826 * np.median(np.abs(flat - np.median(flat))) * 1e6
        res = {"star": star, "period_d": round(cand["period_d"], 4), "depth_ppm": round(cand["depth"] * 1e6),
               "snr": cand["snr"], "sde": cand["sde"], "verdict": verdict, "reasons": reasons, "rms_ppm": round(rms)}
        if verdict == "planet_candidate":
            res["fit"] = pipeline.fit(t, flat, cand)
        results[star] = res
        prov.append({"activity": "search", "used": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()[:12],
                     "params": {"window_d": pipeline.WINDOW_D, "snr_min": pipeline.SNR_MIN, "sde_min": pipeline.SDE_MIN},
                     "generated": hashlib.sha256(json.dumps(res, sort_keys=True).encode()).hexdigest()[:12]})
    return results, prov


def score(name, passed, **measures):
    line = {"milestone": name, "pass": bool(passed), **measures}
    print(json.dumps(line))
    return line


def main(real_model=False):
    results, prov = analyse_all()
    truth = json.loads((DATA / "truth.json").read_text(encoding="utf-8"))
    planets = [s for s, v in truth.items() if v["kind"] == "planet"]
    lines = []
    quiet = {s: results[s]["rms_ppm"] / truth[s]["noise_ppm"] for s, v in truth.items() if v["kind"] in ("quiet", "ramp")}
    lines.append(score("M1 load + detrend", all(0.85 <= r <= 1.15 for r in quiet.values()),
                       rms_over_noise={k: round(v, 3) for k, v in quiet.items()}))
    perr = {s: round(abs(results[s]["period_d"] / truth[s]["period_d"] - 1) * 100, 3) for s in planets + ["S04", "S05"]}
    lines.append(score("M2 BLS search", all(v < 0.1 for v in perr.values()), period_error_percent=perr))
    found = sorted(s for s, r in results.items() if r["verdict"] == "planet_candidate")
    lines.append(score("M3 vetting", found == planets, candidates=found,
                       rejected={s: r["reasons"][0] for s, r in results.items() if r["verdict"] == "rejected"
                                 and truth[s]["kind"].startswith("eb")}))
    sig = {s: round((results[s]["fit"]["depth_ppm"] - truth[s]["depth"] * 1e6) / results[s]["fit"]["depth_err_ppm"], 2)
           for s in found if "fit" in results[s]}
    acc = [results[s]["fit"]["acceptance"] for s in sig]
    lines.append(score("M4 MCMC fit", sig and all(abs(v) <= 3 for v in sig.values()) and all(0.2 <= a <= 0.5 for a in acc),
                       depth_minus_truth_in_sigma=sig, fits={s: results[s]["fit"] for s in sig}))
    t, f, _ = pipeline.load(DATA / "S01.csv")
    again = pipeline.bls(t, pipeline.detrend(t, f))[1]["period_d"]
    lines.append(score("M5 provenance + reproducibility", len(prov) == 12 and round(again, 4) == results["S01"]["period_d"],
                       inputs_hashed=len(prov), s01_sha256=prov[0]["sha256"], rerun_period_d=round(again, 4)))
    server, url = None, None
    if not real_model:
        sys.path.insert(0, str(HERE.parent / "_agent"))
        import fake_model_server
        server, url = fake_model_server.start_in_thread()
    try:
        exps = [agent_explain.explain({"star": s, "period_d": r["period_d"], "depth_ppm": r["depth_ppm"],
                                       "verdict": r["verdict"], "reasons": "; ".join(r["reasons"]) or "none"},
                                      base_url=url) for s, r in results.items() if r["snr"] >= pipeline.SNR_MIN]
    finally:
        if server:
            server.shutdown()
            server.server_close()
    blocked = all(not e["publish"] for e in exps if e["unverified"] or e["overclaim"])
    lines.append(score("M6 agent explanation", blocked and sorted(s for s, r in results.items()
                                                                  if r["verdict"] == "planet_candidate") == planets,
                       explained=len(exps), published=[e["star"] for e in exps if e["publish"]],
                       overclaims_blocked=[e["star"] for e in exps if e["overclaim"]],
                       unverified_numbers=sorted({n for e in exps for n in e["unverified"]})))
    passed = sum(x["pass"] for x in lines)
    final = {"scorecard": "PASS" if passed == len(lines) else "FAIL", "passed": passed, "total": len(lines)}
    print(json.dumps(final))
    (HERE / "scorecard.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines + [final]), encoding="utf-8")
    (HERE / "prov.jsonl").write_text("".join(json.dumps(x) + "\n" for x in prov), encoding="utf-8")
    return lines, final


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--real-model", action="store_true")
    main(ap.parse_args().real_model)
