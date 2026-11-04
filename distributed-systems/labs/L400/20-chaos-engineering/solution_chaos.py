"""L400 lesson 20 BUILD-TASK REFERENCE (python solution_chaos.py): chaos.py + blast radius, control group, abort.
Original header: hypothesis-driven chaos experiments against the L300 labs.
Targets: the L300 saga (lesson 14) and Raft (lesson 12), each as shipped in L300 (unhardened) and as hardened by
its build task. Every experiment states a steady-state metric and a hypothesis, injects a seeded real-world fault and
tries to refute the hypothesis (Principles of Chaos). Results are JSON lines. The lesson's saga harness injects the
fault into EVERY order, keeps no control group and never aborts - watch how many customers the experiment hurts."""
import random

from harness import cohort, jsonl, load

SAGA = {"L300 lesson": load("14-sagas-compensation/saga.py", "l300_saga"),
        "L300 hardened": load("14-sagas-compensation/solution_saga.py", "l300_saga_hardened")}
RAFT = {"L300 lesson": load("12-raft-replicated-log/raft.py", "l300_raft"),
        "L300 hardened": load("12-raft-replicated-log/solution_raft.py", "l300_raft_hardened")}
N_ORDERS, BLAST_PCT, ABORT_AFTER = 60, 10.0, 1  # blast-radius limit and abort rule (used once you add them)


def harmed(mod, services, log, sagas):
    """Steady-state metric, from the services' own data: orders whose money/state is wrong or never finished."""
    bad = {line.split(":")[0] for line in mod.audit(*services)}
    unfinished = {s for s in sagas if not any(r["step"] == "saga" and r["status"] in ("completed", "compensated")
                                              for r in log.entries(s))}
    return sorted((bad | unfinished) & set(sagas))


def inject(mod, orch, shipping, fault, saga):
    """Real-world faults: the courier API is down for this order, or the orchestrator dies right after a charge."""
    if fault == "shipping-outage":
        shipping.outcome[saga] = "no courier slot"
    elif fault == "crash-after-charge":
        name, charge, comp = orch.steps[1]

        def dies_after(s, amount):
            charge(s, amount)
            if s == saga:
                raise mod.lab_helpers.Crash(f"orchestrator died after charge({s})")
        orch.steps[1] = (name, dies_after, comp)


def run_saga_experiment(target, fault, seed):
    """Bounded experiment: the fault hits only a stable cohort (BLAST_PCT of orders); every other order is the
    control group; injection stops after ABORT_AFTER harmed orders - the hypothesis is refuted, stop the damage."""
    mod = SAGA[target]
    services, log = (mod.Orders(), mod.Payments(), mod.Shipping(0.0, seed)), mod.lab_helpers.SagaLog()
    orch, sagas = mod.Orchestrator(*services, log), [f"o{i}" for i in range(1, N_ORDERS + 1)]
    group = cohort(sagas, BLAST_PCT, f"{fault}-{seed}")
    hurt_exp, aborted = [], False
    for i, saga in enumerate(sagas, start=1):
        steps, faulty = list(orch.steps), saga in group and not aborted
        if faulty:
            inject(mod, orch, services[2], fault, saga)
        try:
            orch.run(saga, 10 * i)
        except mod.lab_helpers.Crash:
            if hasattr(orch, "recover"):
                orch.recover()  # the supervisor restarts the orchestrator; it finishes from the saga log
        orch.steps = steps
        if faulty and harmed(mod, services, log, [saga]):
            hurt_exp.append(saga)
            aborted = len(hurt_exp) >= ABORT_AFTER  # automatic abort: no more faults in this run
    control = harmed(mod, services, log, [s for s in sagas if s not in group])
    return {"experiment": f"saga/{fault}", "target": target, "seed": seed,
            "blast_radius_pct": round(100 * len(group) / len(sagas), 1), "steady_state": "harmed orders = 0",
            "experiment_harmed": len(hurt_exp), "control_harmed": len(control), "held": not hurt_exp and not control,
            "aborted": aborted, "customers_hurt": len(harmed(mod, services, log, sagas))}


def run_raft_experiment(target, fault, seed, ticks=60, settle=(0, 4)):
    """Raft faults touch one node at a time (a minority): random crashes, or a fast rolling restart that waits
    only 0-4 ticks between nodes. Steady state: no committed entry lost, a leader again within 40 ticks."""
    mod, rng = RAFT[target], random.Random(f"{fault}-{seed}")
    c, t, gap, worst = mod.lab_helpers.Cluster(mod.Node, seed), 0, 0, 0
    c.run_until_leader()

    def step(n):
        nonlocal t, gap, worst
        for _ in range(n):
            if t % 2 == 0 and c.leader():
                c.leader().propose(f"x={t}")  # steady write load
            c.run(1)
            t, gap = t + 1, (gap + 1 if c.leader() is None else 0)
            worst = max(worst, gap)
    step(10)
    if fault == "rolling-restart":
        for name in sorted(c.nodes, key=lambda n: c.nodes[n].role == "leader"):  # followers first, leader last
            c.crash(name)
            step(12)
            c.restart(name)
            step(rng.randint(*settle))  # impatient rollout (0-4 ticks): does not wait for the node to catch up
    else:  # random-crash: 8 crashes of a random node (the leader 60% of the time), down 5-30 ticks each
        for _ in range(8):
            leader = c.leader()
            name = leader.name if leader and rng.random() < 0.6 else rng.choice(sorted(c.nodes))
            c.crash(name)
            step(rng.randint(5, 30))
            c.restart(name)
            step(rng.randint(5, 20))
    step(ticks)
    lost = len(c.checker.violations)
    return {"experiment": f"raft/{fault}", "target": target, "seed": seed, "blast_radius_pct": 33.3,
            "steady_state": "lost committed entries = 0, no-leader gap <= 40 ticks", "lost_entries": lost,
            "max_no_leader_ticks": worst, "held": lost == 0 and worst <= 40}


def campaign():
    rows = [run_saga_experiment(t, f, 14) for t in SAGA for f in ("shipping-outage", "crash-after-charge")]
    rows += [run_raft_experiment(t, f, s) for t in RAFT for f in ("random-crash", "rolling-restart") for s in range(1, 21)]
    return rows


def summary(rows):
    out = {}
    for r in rows:
        k = (r["experiment"], r["target"])
        held, runs, hurt = out.get(k, (0, 0, 0))
        out[k] = (held + r["held"], runs + 1, hurt + r.get("customers_hurt", 0))
    return out


if __name__ == "__main__":
    rows = campaign()
    print(*jsonl([r for r in rows if r["experiment"].startswith("saga")]), sep="\n")
    print("experiment              target          hypothesis held   customers hurt by the experiment")
    for (exp, target), (held, runs, hurt) in summary(rows).items():
        print(f"{exp:23} {target:15} {held:>3}/{runs:<3} runs {hurt:>12}")
