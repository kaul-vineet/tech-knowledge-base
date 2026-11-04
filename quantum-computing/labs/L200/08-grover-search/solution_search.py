"""Build-task solution for lab 08: search for every x that satisfies a Python predicate.

Run: python solution_search.py
grover_search_numpy runs anywhere; grover_search (Qiskit) needs qiskit.
"""
import crosscheck_numpy as cc


def marked_from_predicate(predicate, n_qubits):
    marked = [format(x, f"0{n_qubits}b") for x in range(2 ** n_qubits) if predicate(x)]
    if not marked or 2 * len(marked) >= 2 ** n_qubits:
        raise ValueError(f"{len(marked)} of {2 ** n_qubits} states marked: Grover needs 0 < M < N/2")
    return marked


def grover_search_numpy(predicate, n_qubits):
    marked = marked_from_predicate(predicate, n_qubits)
    k = cc.optimal_iterations(len(marked), n_qubits)
    return marked, k, cc.success(marked, k)


def grover_search(predicate, n_qubits, shots=1000, seed=5):
    import grover_lab
    marked = marked_from_predicate(predicate, n_qubits)
    k = grover_lab.optimal_iterations(len(marked), n_qubits)
    counts = grover_lab.counts(marked, k, shots, seed)
    return marked, k, grover_lab.success_probability(marked, k), max(counts, key=counts.get)


if __name__ == "__main__":
    print("x == 5:     ", grover_search_numpy(lambda x: x == 5, 3))
    print("x % 3 == 0: ", grover_search_numpy(lambda x: x % 3 == 0, 3))
