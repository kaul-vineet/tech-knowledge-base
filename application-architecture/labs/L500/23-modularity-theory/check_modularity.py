"""Numerical checks for the lesson 23 theorems. Run: python check_modularity.py  (exit 0 = every check holds)."""
import math
import random
import sys

import modularity as m

FAILURES = []


def check(label, ok):
    print(f"  [{'OK' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILURES.append(label)


def theorem_layering(rng, trials=2000):
    print("T1 strict layering <=> acyclic")
    strict_acyclic = sum(m.is_acyclic(*m.random_graph(rng, 12, 0.3, strict=True)[:2]) for _ in range(trials))
    check(f"{strict_acyclic}/{trials} random strictly layered graphs are acyclic", strict_acyclic == trials)
    loose_cyclic = sum(not m.is_acyclic(*m.random_graph(rng, 12, 0.3, strict=False)[:2]) for _ in range(trials))
    print(f"      (same-layer edges allowed: {loose_cyclic}/{trials} graphs have a cycle - strictness matters)")
    dags = violations = 0
    for _ in range(trials):
        order = list(range(12))
        rng.shuffle(order)
        pos = {v: k for k, v in enumerate(order)}
        edges = [(a, b) for a in order for b in order if pos[a] < pos[b] and rng.random() < 0.3]
        level = m.longest_path_layering(order, edges)
        dags += 1
        violations += len(m.strict_layering_violations(edges, level))
    check(f"converse: longest-path layering of {dags} random DAGs has {violations} violations", violations == 0)
    for name, lab in (("layered (L100 #2)", m.LAYERED), ("hexagonal (L200 #7)", m.HEXAGONAL)):
        nodes, edges, _ = m.module_graph(lab)
        level = m.longest_path_layering(nodes, edges)
        layers = {}
        for node, lv in sorted(level.items()):
            layers.setdefault(lv, []).append(node)
        check(f"{name}: {len(edges)} edges, acyclic, layers {dict(sorted(layers.items()))}",
              m.is_acyclic(nodes, edges) and not m.strict_layering_violations(edges, level))


def theorem_condensation(rng, trials=2000):
    print("T2 the condensation (SCC graph) of any directed graph is acyclic")
    ok = cyclic_inputs = 0
    for _ in range(trials):
        nodes = list(range(10))
        edges = [(a, b) for a in nodes for b in nodes if a != b and rng.random() < 0.15]
        cyclic_inputs += not m.is_acyclic(nodes, edges)
        cnodes, cedges, _ = m.condensation(nodes, edges)
        ok += m.is_acyclic(cnodes, cedges)
    check(f"{ok}/{trials} condensations acyclic ({cyclic_inputs} of the inputs had cycles)", ok == trials)
    nodes, with_main, _ = m.module_graph(m.HEXAGONAL, include_main=True)
    big = [sorted(c) for c in m.tarjan_scc(nodes, with_main) if len(c) > 1]
    check(f"hexagonal lab read WITH its __main__ blocks: cycle component {big} "
          f"(driving_cli's entry block imports app, app imports driving_cli)", big == [["app", "driving_cli"]])
    nodes, edges, _ = m.module_graph(m.HEXAGONAL)
    seeded = edges + [("domain", "driving_http")]  # seeded fault: the domain reaches out to an adapter
    big = [sorted(c) for c in m.tarjan_scc(nodes, seeded) if len(c) > 1]
    check(f"seeded edge domain -> driving_http creates the cycle component {big}",
          big == [["domain", "driving_http"]] and not m.is_acyclic(nodes, seeded))


def theorem_main_sequence():
    print("T3 Martin metrics on Library Loans (L200 #7 hexagonal): I, A in [0,1]; distance to A + I = 1 is Dn / sqrt(2)")
    nodes, edges, classes = m.module_graph(m.HEXAGONAL)
    rows = m.martin_metrics(nodes, edges, classes)
    print(f"      {'module':<14}{'Ca':>3}{'Ce':>3}{'I':>7}{'A':>6}{'Dn':>7}{'numeric d':>11}")
    worst = 0.0
    for name, r in rows.items():
        numeric = m.distance_to_main_sequence_numeric(r["A"], r["I"])
        worst = max(worst, abs(numeric - r["Dn"] / math.sqrt(2)))
        print(f"      {name:<14}{r['Ca']:>3}{r['Ce']:>3}{r['I']:>7.3f}{r['A']:>6.2f}{r['Dn']:>7.3f}{numeric:>11.4f}")
    check("all I and A in [0, 1]", all(0 <= r["I"] <= 1 and 0 <= r["A"] <= 1 for r in rows.values()))
    check(f"max |numeric distance - Dn/sqrt(2)| = {worst:.1e} (< 1e-5)", worst < 1e-5)
    mean_dn = sum(r["Dn"] for r in rows.values()) / len(rows)
    print(f"      mean Dn = {mean_dn:.3f}; furthest from the main sequence: "
          f"{max(rows, key=lambda n: rows[n]['Dn'])} (stable and concrete: the 'zone of pain' corner)")


def kwic_example():
    print("Worked example: Parnas KWIC change impact (modules that must change per design decision)")
    for label, knows in (("conventional", m.KWIC_CONVENTIONAL), ("information hiding", m.KWIC_HIDING)):
        impact = m.change_impact(knows)
        counts = [len(v) for v in impact.values()]
        print(f"      {label:<19} {counts} total {sum(counts)}, worst {max(counts)}")
    check("information hiding: every decision is known by exactly one module",
          all(len(v) == 1 for v in m.change_impact(m.KWIC_HIDING).values()))


if __name__ == "__main__":
    rng = random.Random(500)
    theorem_layering(rng)
    theorem_condensation(rng)
    theorem_main_sequence()
    kwic_example()
    print("ALL CHECKS OK" if not FAILURES else f"FAILED: {FAILURES}")
    sys.exit(1 if FAILURES else 0)
