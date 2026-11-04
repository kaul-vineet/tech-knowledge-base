"""L400 model governance: build the V&V evidence pack for a staffing model and check the model card against it.

Model under governance: the L200 lesson 8 clinic queue (M/M/3 DES), used to staff a reception desk.
Evidence = verification suite + validation against Erlang C over a utilisation grid + sensitivity + hashes.
python governance.py       (writes evidence.json; checks model_card.json and cards/draft_overclaiming.json)
"""
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MODEL_FILE = HERE.parents[1] / "L200" / "08-multi-server-queue" / "mmc_queue.py"
sys.path.append(str(MODEL_FILE.parent))
import mmc_queue as mq  # noqa: E402

DATA_FILE, CARD = HERE / "arrivals.csv", HERE / "model_card.json"
RHO_GRID, REPS, CUSTOMERS, TOL = (0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95), 10, 20_000, 0.10  # TOL set BEFORE the runs
REQUIRED = ("purpose", "intended_use", "assumptions", "validity_envelope", "verification", "validation",
            "sensitivity", "versions", "limitations", "review")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()  # CRLF-safe: same on Windows


def verify():
    """Verification: run the suite in verification.py and keep the counts (the code is right?)."""
    suite = unittest.defaultTestLoader.loadTestsFromName("verification")
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures) + len(result.errors)}


def validate():
    """Operational validity: simulated mean wait vs the exact Erlang C value at each utilisation."""
    rows = []
    for i, rho in enumerate(RHO_GRID):
        lam = 3 * rho
        runs = np.array([mq.simulate(CUSTOMERS, 3, lam, 1.0, seed=100 * i + r)["Wq"] for r in range(REPS)])
        exact = mq.erlang_c(3, lam, 1.0)["Wq"]
        half = 2.262 * runs.std(ddof=1) / np.sqrt(REPS)  # t(0.975, 9 df) = 2.262
        rel = abs(runs.mean() - exact) / exact
        rows.append({"rho": rho, "sim_Wq": round(float(runs.mean()), 4), "exact_Wq": round(exact, 4),
                     "rel_error": round(float(rel), 4), "rel_half_width": round(float(half / runs.mean()), 4),
                     "ok": bool(rel <= TOL and half / runs.mean() <= TOL)})
    envelope = 0.0
    for row in rows:  # the envelope ends at the first utilisation that fails the accuracy requirement
        if not row["ok"]:
            break
        envelope = row["rho"]
    return rows, envelope


def sensitivity(lam=2.4, mu=1.0, c=3, h=0.01):
    """Elasticities d ln Wq / d ln x at the nominal point (central differences on Erlang C)."""
    wq = lambda lam_, mu_: np.log(mq.erlang_c(c, lam_, mu_)["Wq"])
    return {"lam": round(float((wq(lam * (1 + h), mu) - wq(lam * (1 - h), mu)) / (2 * h)), 2),
            "mu": round(float((wq(lam, mu * (1 + h)) - wq(lam, mu * (1 - h))) / (2 * h)), 2)}


def peak_utilisation():
    """The busiest hour in the arrival data, as utilisation of 3 desks serving 1 patient/min each."""
    counts = [int(line.split(",")[1]) for line in DATA_FILE.read_text(encoding="utf-8").splitlines()[1:]]
    return round(max(counts) / 60 / 3, 3)


def evidence():
    rows, envelope = validate()
    elastic = sensitivity()
    return {"verification": verify(), "validation": rows, "envelope_rho_max": envelope,
            "max_rel_error_in_envelope": max(r["rel_error"] for r in rows if r["rho"] <= envelope),
            "sensitivity": elastic, "most_influential": max(elastic, key=lambda k: abs(elastic[k])),
            "peak_utilisation": peak_utilisation(), "code_sha256": sha256(MODEL_FILE), "data_sha256": sha256(DATA_FILE)}


def check_card(card, ev):
    """Review gate: returns a list of findings; an empty list means the card may be published."""
    return [f"missing section: {key}" for key in REQUIRED if key not in card]


def checklist(card, ev, findings):
    return [("verification suite passes", ev["verification"]["failures"] == 0),
            ("validated envelope covers the busiest hour in the data", ev["envelope_rho_max"] >= ev["peak_utilisation"]),
            ("sensitivity results recorded", "sensitivity" in card),
            ("model and data versions pinned by hash", "versions" in card),
            ("card claims match the evidence", not findings)]


def main():
    ev = evidence()
    (HERE / "evidence.json").write_text(json.dumps(ev, indent=1) + "\n", encoding="utf-8")
    v = ev["verification"]
    print(f"verification: {v['tests_run']} tests, {v['failures']} failures")
    print("validation vs Erlang C (10 reps x 20,000 patients):  rho  sim_Wq  exact  rel_err  rel_CI  ok")
    for r in ev["validation"]:
        print(f"  {r['rho']:4.2f} {r['sim_Wq']:7.3f} {r['exact_Wq']:6.3f} {r['rel_error']:7.1%} {r['rel_half_width']:6.1%}  {r['ok']}")
    print(f"validity envelope: utilisation <= {ev['envelope_rho_max']}; max error inside {ev['max_rel_error_in_envelope']:.1%}; "
          f"busiest hour in arrivals.csv needs {ev['peak_utilisation']}")
    print(f"sensitivity (elasticity of Wq): {ev['sensitivity']} -> most influential: {ev['most_influential']}")
    for path in (CARD, HERE / "cards" / "draft_overclaiming.json"):
        card = json.loads(path.read_text(encoding="utf-8"))
        findings = check_card(card, ev)
        print(f"{path.name}: {'PUBLISHABLE' if not findings else 'BLOCKED'}; findings {findings}")
        for item, ok in checklist(card, ev, findings):
            print(f"   [{'x' if ok else ' '}] {item}")


if __name__ == "__main__":
    main()
