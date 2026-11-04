"""L600 #02 - Quantum-safe migration: from Shor in a simulator to a crypto inventory (end-to-end runner).

Run:  python run_project.py                    milestones, seams and fitness functions as JSON lines; exit 1 on any fail
      python run_project.py --inject bypass     failure lab: messaging's "fast path" skips the registry
      python run_project.py --inject downgrade  rollout fault: a compat shim re-adds X25519 when PQ is required
numpy + cryptography 50.0.2 + stdlib; Qiskit not needed (qsim statevector). Seeded; flags/baseline use a fake clock.
"""
import argparse
import json
import sys

import crypto_registry as registry
import estimates
import fitness
import fleet
import inventory
import migration_plan
import seams
import shor_sim
import wire

PHASES = [("all-v1", [1, 1, 1], False), ("mixed", [2, 2, 1], False), ("all-v2", [2, 2, 2], True),
          ("rollback-v1", [2, 2, 1], True)]          # last phase: one server rolled back while PQ is required


def collect(inject=None):
    sims = [shor_sim.shor(15, 7), shor_sim.shor(15, 7, gate_level=True), shor_sim.shor(21, 2)]
    expected = json.loads((registry.HERE / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))["before"]
    variant = inject or "migrated"
    folder = fleet.FOLDERS[variant]
    before, after = inventory.scan("before"), inventory.scan("after", messaging=folder)
    registry.reset()
    channel, phases, all_flights = fleet.load_channel(variant), {}, wire.Tap()
    for name, versions, required in PHASES:
        registry.AUDIT.clear()
        registry.FLAGS.set("pq_required.messaging", required)
        servers = fleet.make_fleet(versions)
        stats = fleet.run_traffic(channel, servers)
        stats.update(servers=servers, s3=seams.s3_agility_to_wire(stats["tap"]),
                     f3=fitness.f3_registry_only(registry.HERE / folder / "channel.py", stats["tap"]))
        all_flights.flights += stats["tap"].flights
        phases[name] = stats
    registry.reset()
    return {"sims": sims, "expected": expected, "before": before, "after": after, "phases": phases, "tap": all_flights}


def milestones(c):
    s15, s15g, s21 = c["sims"]
    score = inventory.score(c["before"], c["expected"])
    plan_b, plan_a = migration_plan.plan(c["before"]), migration_plan.plan(c["after"])
    msg_after = sorted({r["priority"] for r in plan_a if r["service"] == "messaging" and r["usage"] != "symmetric"})
    ph = c["phases"]
    sessions = {k: v["sessions"] for k, v in ph.items()}
    return [
        ("M1 Shor order finding on a statevector (N = 15, 21)",
         s15["factors"] == [3, 5] and s21["factors"] == [3, 7] and s15g["p_success_per_run"] == s15["p_success_per_run"]
         and all(shor_sim.matches_fft_shortcut(s) for s in c["sims"]),
         {f"N={s['N']}{' gate-level' if 'ccx' in s['gates'] else ''}": {"qubits": s["qubits"], "p_success": s["p_success_per_run"],
          "successes": f"{s['successes']}/{s['shots']}", "factors": s["factors"], "oracle_gates": {k: v for k, v in s["gates"].items()
          if k in ("cx", "ccx", "controlled_mult_permutations")}} for s in c["sims"]}),
        ("M2 published estimates, labelled", not estimates.check_claims(estimates.claims(c["sims"])),
         {"RSA-2048": {k: f"{v['physical_qubits']}, {v['runtime']}" for k, v in estimates.CITED.items()},
          "GE2019_formula_logical_qubits": estimates.ge_formula()["logical_qubits"],
          "NIST_IR_8547": estimates.NIST_IR_8547["timeline"]}),
        ("M3 crypto inventory (code + config)", score["recall"] == 1.0 and score["precision"] == 1.0,
         {"findings_before": len(c["before"]), "recall": score["recall"], "precision": score["precision"],
          "findings_after": len(c["after"])}),
        ("M4 Mosca risk + prioritised plan", migration_plan.summary(plan_b).get("P1") == 3 and msg_after == ["done"],
         {"z": migration_plan.HORIZON.z_years, "before": migration_plan.summary(plan_b), "after": migration_plan.summary(plan_a),
          "first_P1": f"{plan_b[0]['service']} {plan_b[0]['algorithm']} (x+y-z = {plan_b[0]['slack']})"}),
        ("M5 hybrid X25519MLKEM768 + ML-DSA-65 behind the registry, flag-driven rollout",
         ph["all-v2"]["sessions"] == {"X25519MLKEM768": 6} and ph["mixed"]["sessions"] == {"X25519MLKEM768": 4, "X25519": 2}
         and all(v["delivered"] + v["refused"] == 6 for v in ph.values()),
         {"sessions": sessions, "refused": {k: v["refused"] for k, v in ph.items()}}),
    ]


def seam_rows(c):
    ph = c["phases"]
    s3 = {k: v["s3"] for k, v in ph.items()}
    return [
        ("S1 quantum -> risk model: no extrapolation, z is a labelled assumption", seams.s1_quantum_to_risk(c["sims"])),
        ("S2 inventory -> plan: every finding owned and planned", seams.s2_inventory_to_plan(c["after"])),
        ("S3 agility layer <-> wire format: offers and sizes match the registry",
         {"ok": all(v["ok"] for v in s3.values()), **{k: v["problems"] or "ok" for k, v in s3.items()},
          "adapters_match_advertised": all(v["adapters_match_advertised"] for v in s3.values())}),
        ("S4 rollout flags <-> crypto policy: no downgrade when PQ is required",
         seams.s4_rollout_to_policy(ph["rollback-v1"], ph["rollback-v1"]["servers"])),
    ]


def fitness_rows(c):
    f3 = {k: v["f3"] for k, v in c["phases"].items()}
    return [
        ("F1 no classical-only key exchange for data with x + y > z (outside the dated baseline)",
         fitness.f1_no_classical_kex_for_exposed_data(c["after"])),
        ("F2 handshake byte budget", fitness.f2_handshake_budget(c["tap"])),
        ("F3 every service resolves algorithms via the registry",
         {"ok": all(v["ok"] for v in f3.values()), "static_violations": max(v["static_violations"] for v in f3.values()),
          "handshakes": sum(v["handshakes"] for v in f3.values()),
          "client_kex_resolutions": sum(v["client_kex_resolutions"] for v in f3.values())}),
        ("F4 feature flags owned and not expired", fitness.f4_flags_owned_and_live()),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inject", choices=["bypass", "downgrade"])
    args = ap.parse_args(argv)
    c = collect(args.inject)
    passed = {"milestones": 0, "seams": 0, "fitness": 0}
    totals = {"milestones": 0, "seams": 0, "fitness": 0}
    for kind, rows in (("milestones", milestones(c)), ("seams", seam_rows(c)), ("fitness", fitness_rows(c))):
        for row in rows:
            name, ok, measure = (row[0], row[1], row[2]) if len(row) == 3 else (row[0], row[1]["ok"], row[1])
            measure = {k: v for k, v in measure.items() if k != "ok"}
            print(json.dumps({kind[:-1] if kind != "fitness" else "fitness": name, "pass": bool(ok), "measure": measure}))
            passed[kind] += bool(ok)
            totals[kind] += 1
    ok = passed == totals
    print(json.dumps({"scorecard": {k: f"{passed[k]}/{totals[k]}" for k in totals}, "inject": args.inject,
                      "all_pass": ok, "decided_by": "code"}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
