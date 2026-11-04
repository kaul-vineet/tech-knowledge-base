"""Try-it checks for lab 20. Run: python try_it.py   (numpy only)"""
import compile_lab as lab
import device as D
import noisy_check as nc
import solution_layout as sol


def other_drift(edge=(5, 6), error=0.15):
    """Try 1: tomorrow a different edge drifts. Does the noise-aware layout move, and what does it keep?"""
    dev = D.make_device(drift={edge: error})
    layout = sol.choose_layout(dev)
    ops, final, m = lab.compile_circuit(dev, layout, weighted=True, optimise=True)
    used = {tuple(sorted(o[1])) for o in ops if o[0] == "cx"}
    return {"layout": layout, **m, "uses_drifted_edge": tuple(sorted(edge)) in used,
            "noisy_fidelity": nc.noisy_fidelity(ops, final, dev)}


def tight_budget(budget=17):
    """Try 2: demand the logical depth (17): no SWAP allowed. What does the search return?"""
    dev = D.make_device(drift=D.DRIFT)
    _, _, m = lab.compile_circuit(dev, sol.choose_layout(dev, budget), weighted=True, optimise=True)
    return {**m, "within_budget": m["depth"] <= budget}


if __name__ == "__main__":
    print("other_drift ", other_drift())
    print("tight_budget", tight_budget())
