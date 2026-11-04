"""Try-it checks for lab 15. Run: python try_it.py   (numpy only)"""
import json

import vqe_lab as lab
import solution_spsa as sol


def more_shots_same_optimizer():
    """Try 1: keep finite differences (h = 1e-3) but raise shots per term from 1000 to 1e5 and 1e6. Fixed? At what cost?"""
    evals = 9 * 100                                   # 100 iterations x (8 gradient + 1 logged) evaluations
    return {shots: {"error": lab.vqe(shots)[1], "total_shots": 2 * shots * evals} for shots in (1000, 100000, 1000000)}


def spsa_cost():
    return {"error": sol.vqe(1000)[1], "total_shots": 2 * 1000 * 3 * 150}


def below_the_ground_energy():
    """Try 2: in the SPSA log, how many logged estimates are BELOW the exact ground energy E0?"""
    path = lab.HERE / "logs" / "vqe_spsa_1000.jsonl"
    sol.vqe(1000, log_path=path)
    rows = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines()]
    return {"E0": round(lab.E0, 4), "best_energy_est": min(r["energy_est"] for r in rows),
            "rows_below_E0": sum(r["energy_est"] < lab.E0 for r in rows), "rows": len(rows)}


if __name__ == "__main__":
    print("more_shots_same_optimizer", more_shots_same_optimizer())
    print("spsa_cost (for comparison)", spsa_cost())
    print("below_the_ground_energy  ", below_the_ground_energy())
