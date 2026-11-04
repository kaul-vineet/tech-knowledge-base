"""Try-it checks for the capstone. Run: python try_it.py   (numpy; each request runs the full pipeline)"""
import pipeline


def small_budget():
    """Try 1: the same 8-node request with a 400-sample budget. Who wins now, and how often is the optimum found?"""
    rep = pipeline.solve({"budget": 400})
    return rep["winner"], {r["solver"]: r["success"] for r in rep["benchmark"]}


def calibrated_device():
    """Try 2: no drift on edge (1, 2). How much do compile ESP and gate fidelity change?"""
    rep = pipeline.solve({"drift": False, "seeds": 3})
    return {k: rep["compile"][k] for k in ("esp", "gate_fidelity", "cx", "depth")}


if __name__ == "__main__":
    print("small_budget     ", small_budget())
    print("calibrated_device", calibrated_device())
