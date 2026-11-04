"""Milestone 2 - what breaking real keys needs: PUBLISHED estimates only, each labelled with its source.

Rule (seam quantum -> risk model): this lab never extrapolates from its N = 15 / 21 simulation to RSA-2048. Every claim
about a real key size carries a published source; the simulator may only make claims about the toy N it ran.
"""
import _kb  # noqa: F401
import estimate_lab as l19  # quantum L400 #19: Gidney-Ekera abstract-circuit formulas

ASSUMPTIONS = "planar nearest-neighbour grid, physical gate error 1e-3, 1 us surface-code cycle, 10 us reaction time"
CITED = {
    "GE2019": {"source": "Gidney & Ekera, 'How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits',"
                         " Quantum 5, 433 (2021), arXiv:1905.09749", "target": "RSA-2048", "kind": "published estimate",
               "physical_qubits": "20 million noisy qubits", "runtime": "8 hours", "assumptions": ASSUMPTIONS},
    "G2025": {"source": "Gidney, 'How to factor 2048 bit RSA integers with less than a million noisy qubits',"
                        " arXiv:2505.15917 (2025)", "target": "RSA-2048", "kind": "published estimate",
              "physical_qubits": "less than a million noisy qubits", "runtime": "less than a week",
              "assumptions": ASSUMPTIONS + " (same as 2019, per the paper)"},
}
NIST_IR_8547 = {"source": "NIST IR 8547 (final, October 2026), Tables 2 and 4",
                "quantum_vulnerable": "RSA, ECDSA, EdDSA, finite-field and elliptic-curve DH/MQV",
                "timeline": "deprecated after 2030, disallowed after 2035",
                "hndl": "migrate key establishment first for data with long-term confidentiality needs"}


def ge_formula(bits=2048):
    """The GE2019 abstract-circuit formulas (3n + 0.002 n lg n logical qubits, 0.3 n^3 + 0.0005 n^3 lg n Toffolis),
    evaluated by quantum lesson 19's rsa_logical. Abstract circuit model: no distillation, routing or error correction."""
    row = l19.rsa_logical(bits)
    return {"source": "GE2019 abstract formulas", "target": f"RSA-{bits}", "kind": "published formula, evaluated",
            "logical_qubits": row["logical_qubits"], "toffoli": row["toffoli"]}


def claims(sim_results):
    """Every statement the report makes, tagged with where it comes from. Checked by the quantum->risk seam test."""
    out = [{"target": f"N={r['N']}", "source": "this-lab-simulator",
            "text": f"N = {r['N']}: {r['qubits']} simulated qubits, P(success per run) = {r['p_success_per_run']}"}
           for r in sim_results]
    out += [{"target": c["target"], "source": key, "text": f"{c['physical_qubits']}, {c['runtime']}"}
            for key, c in CITED.items()]
    f = ge_formula()
    out.append({"target": f["target"], "source": "GE2019",
                "text": f"{f['logical_qubits']} logical qubits, {f['toffoli']:.3g} Toffolis (abstract circuit)"})
    return out


def check_claims(items):
    """A real-key claim must cite a published source; the simulator may only speak about the N it ran."""
    bad = [c for c in items if c["source"] == "this-lab-simulator" and not c["target"].startswith("N=")]
    bad += [c for c in items if c["target"].startswith("RSA") and c["source"] not in CITED]
    return bad


if __name__ == "__main__":
    import json
    for key, c in CITED.items():
        print(json.dumps({"id": key, **c}))
    print(json.dumps(ge_formula()))
    print(json.dumps(NIST_IR_8547))
