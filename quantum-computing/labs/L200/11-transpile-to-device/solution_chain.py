"""Build-task solution for lab 11: rewrite the GHZ star as a nearest-neighbour chain.

Run: python solution_chain.py
Same state, but every CX is an edge of the line, so routing adds no SWAPs.
numpy part runs anywhere; compare_on_line needs qiskit.
"""
import crosscheck_numpy as cc

CHAIN = [(i, i + 1) for i in range(cc.N - 1)]


def chain_numpy():
    return {"same_state_as_star": cc.ghz_probabilities(CHAIN) == cc.ghz_probabilities(cc.STAR),
            "non_adjacent_on_line": cc.non_adjacent(CHAIN, cc.COUPLING["line"])}


def ghz_chain(n=5):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)                  # layout-aware rewrite: only neighbours on a line
    qc.measure_all()
    return qc


def compare_on_line():
    import transpile_lab
    line = transpile_lab.backends()["line"]
    out = {}
    for name, qc in (("star", transpile_lab.ghz_star()), ("chain", ghz_chain())):
        out[name] = [transpile_lab.two_qubit_count(transpile_lab.transpile_for(qc, line, lvl)) for lvl in range(4)]
    return out


if __name__ == "__main__":
    print("chain vs star (numpy):", chain_numpy())
