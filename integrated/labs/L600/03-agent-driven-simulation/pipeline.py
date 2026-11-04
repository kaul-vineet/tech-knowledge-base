"""Job pipeline: proposal -> contract gate -> budget gate -> seeded runs (registry) -> statistics -> tool result.

The agent only proposes (tool arguments). Everything below is deterministic code: what may run, how many
replications, what it costs, which numbers exist. Each job keeps its state history (PROPOSED ... DONE/REJECTED).
"""
import importlib.util
import os
from pathlib import Path

import numpy as np

import _kb
import contract
import model
import registry as reg
import stats

HERE = Path(__file__).resolve().parent
sensitivity = _kb.load("sensitivity")
SCREEN_LOW = np.array([0.60, 0.95, 0.0, 0.0])    # lam, mu, backlog, warmup  (rho <= 0.85/0.95 = 0.895)
SCREEN_HIGH = np.array([0.85, 1.20, 60.0, 400.0])
SCREEN_NAMES = ["lam", "mu", "backlog", "warmup"]
SCREEN_CUSTOMERS, MAX_ROUNDS, DEFAULT_SEED = 1000, 6, 2026


class BudgetExceeded(Exception):
    pass


class SimBudget:
    """Session budget in simulated customers. reserve() is called BEFORE a batch runs, never after."""

    def __init__(self, limit, gate=True):
        self.limit, self.spent, self.gate, self.ledger = limit, 0, gate, []

    def affordable(self, amount):
        return not self.gate or self.spent + amount <= self.limit

    def reserve(self, amount, what):
        if not self.affordable(amount):
            raise BudgetExceeded(f"{what} needs {amount:,} customers > remaining {self.limit - self.spent:,}")
        self.spent += amount
        self.ledger.append((what, amount))


def load_policy(target=None):
    """required_replications(): solution by default; BUILD_TARGET=mine uses the learner's replications.py."""
    target = target or ("replications.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/replications.py")
    spec = importlib.util.spec_from_file_location(f"replications_{abs(hash(target))}", HERE / target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.required_replications


def naive_policy(requested, a, b, half_width):  # the failure lab: trust the agent's replication count
    return requested


class Pipeline:
    def __init__(self, registry, budget, half_width=0.5, policy=None, gate=True, seeded=True):
        self.registry, self.budget, self.half_width = registry, budget, half_width
        self.policy, self.gate, self.seeded, self.jobs = policy or load_policy(), gate, seeded, []

    def submit(self, name, args):
        job = {"job": f"job-{len(self.jobs) + 1}", "tool": name, "args": args, "states": ["PROPOSED"]}
        self.jobs.append(job)
        problems = contract.validate(name, args) if self.gate else []
        if problems:
            job["states"].append("REJECTED")
            return {"status": "rejected", "job": job["job"], "errors": problems}
        job["states"].append("VALIDATED")
        try:
            out = (self._experiment if name == "run_experiment" else self._screening)(job, args)
        except BudgetExceeded as exc:
            job["states"].append("REJECTED")
            return {"status": "rejected", "job": job["job"], "errors": [f"budget: {exc}"]}
        job["states"].append("DONE")
        return {"status": "ok", "job": job["job"], **out}

    def _run(self, params, seed, job):
        seed = seed if self.seeded else None  # fault 'unseeded': OS entropy, the record cannot reproduce it
        value = model.run_once(params, seed)
        return value, self.registry.record_run(params, seed, value, job)["run_id"]

    def _experiment(self, job, args):
        root, arms = args.get("seed", DEFAULT_SEED), [args["baseline"], args["candidate"]]
        requested, vals, ids = args.get("replications", 10), ([], []), ([], [])
        n, limited = requested, False
        self.budget.reserve(n * sum(map(model.cost, arms)), f"{job['job']} first {n} replications")
        job["states"].append("PLANNED")
        for _ in range(MAX_ROUNDS):
            for rep in range(len(vals[0]), n):
                for k, arm in enumerate(arms):
                    v, rid = self._run(arm, model.seed_for(root, k, rep), job["job"])
                    vals[k].append(v)
                    ids[k].append(rid)
            n_req = self.policy(requested, vals[0], vals[1], self.half_width)
            job["required"] = n_req
            if n_req <= n:
                break
            extra = (n_req - n) * sum(map(model.cost, arms))
            if not self.budget.affordable(extra):
                limited = True
                break
            self.budget.reserve(extra, f"{job['job']} extend to {n_req} replications")
            n = n_req
        job["states"].append("RAN")
        return self._analyse(job, args, arms, vals, ids, limited)

    def _analyse(self, job, args, arms, vals, ids, limited):
        a, b = vals
        (ma, ha), (mb, hb) = stats.mean_ci(a), stats.mean_ci(b)
        d, hw, df = stats.welch_ci(a, b)
        n = len(a)
        if n >= 10 and d + hw < 0:
            verdict = "significant decrease"
        elif n >= 10 and d - hw > 0:
            verdict = "significant increase"
        else:
            verdict = "inconclusive"
        every = ids[0] + ids[1]
        facts = {"baseline_mean": (ma, ids[0]), "baseline_half_width": (ha, ids[0]), "candidate_mean": (mb, ids[1]),
                 "candidate_half_width": (hb, ids[1]), "difference": (d, every), "difference_half_width": (hw, every),
                 "difference_low": (d - hw, every), "difference_high": (d + hw, every),
                 "percent_change": (100 * d / ma, every), "replications": (n, every),
                 "required_replications": (job.get("required", n), every), "confidence_level": (95, every),
                 "baseline_lam": (arms[0]["lam"], ids[0]), "baseline_mu": (arms[0]["mu"], ids[0]),
                 "candidate_lam": (arms[1]["lam"], ids[1]), "candidate_mu": (arms[1]["mu"], ids[1])}
        exp_id = "exp-" + reg.digest({"job": job["job"], "runs": every}, 8)
        self.registry.record_experiment(exp_id, job["job"], {k: {"value": v, "runs": r} for k, (v, r) in facts.items()}
                                        | {"verdict": {"value": verdict, "runs": every}})
        job["states"].append("ANALYSED")
        r3 = lambda x: round(float(x), 3)
        return {"experiment_id": exp_id, "replications": n, "requested": args.get("replications", 10),
                "required_replications": job.get("required", n),
                "budget_limited": limited, "baseline": {"mean": r3(ma), "ci_half_width": r3(ha)},
                "candidate": {"mean": r3(mb), "ci_half_width": r3(hb)},
                "difference": {"mean": r3(d), "half_width": r3(hw), "ci_low": r3(d - hw), "ci_high": r3(d + hw), "df": round(df, 1)},
                "percent_change": round(100 * d / ma, 1), "verdict": verdict}

    def _screening(self, job, args):
        size, root, d = args["size"], args.get("seed", DEFAULT_SEED), len(SCREEN_NAMES)
        runs = size * (d + 1) if args["method"] == "morris" else size * (d + 2)
        self.budget.reserve(runs * SCREEN_CUSTOMERS, f"{job['job']} {args['method']} {runs} runs")
        job["states"].append("PLANNED")
        ids, seed = [], model.seed_for(root, 99, 0)  # one stream for every point: CRN, effects are not noise

        def f(x):  # adapter: sensitivity.py works in its own physical units -> unit cube -> our ranges
            u = (x - sensitivity.LOW) / (sensitivity.HIGH - sensitivity.LOW)
            out = []
            for row in SCREEN_LOW + u * (SCREEN_HIGH - SCREEN_LOW):
                p = {"lam": float(row[0]), "mu": float(row[1]), "backlog": int(round(row[2])),
                     "warmup": int(round(row[3])), "customers": SCREEN_CUSTOMERS}
                v, rid = self._run(p, seed, job["job"])
                out.append(v)
                ids.append(rid)
            return np.array(out)

        if args["method"] == "morris":
            index, _ = sensitivity.morris(r=size, levels=4, f=f, seed=root)
        else:
            _, index = sensitivity.sobol(n=size, f=f, seed=root)
        ranking = [SCREEN_NAMES[i] for i in np.argsort(-index)]
        name = "mu_star" if args["method"] == "morris" else "ST"
        exp_id = "exp-" + reg.digest({"job": job["job"], "runs": ids}, 8)
        facts = {f"{name}_{k}": {"value": float(v), "runs": ids} for k, v in zip(SCREEN_NAMES, index)}
        facts["size"] = {"value": size, "runs": ids}
        self.registry.record_experiment(exp_id, job["job"], facts)
        job["states"].append("ANALYSED")
        return {"experiment_id": exp_id, "method": args["method"], "runs": runs, "ranking": ranking,
                name: {k: round(float(v), 3) for k, v in zip(SCREEN_NAMES, index)}}
