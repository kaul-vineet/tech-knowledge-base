"""Try-it checks for lab 19. Run: python try_it.py   (stdlib + numpy)"""
import estimate_lab as lab
import solution_distance as sol


def better_hardware(p=1e-4):
    """Try 1: physical error 1e-4 instead of 1e-3. What happens to RSA-2048's distance, qubits and runtime?"""
    row = lab.physical(lab.rsa_logical(2048), p=p, choose=sol.choose_distance)
    return {k: row[k] for k in ("distance", "physical_qubits", "runtime_s")}


def near_threshold():
    """Try 2: QAOA n=100 p=4 at p = 0.001, 0.005, 0.009, then 0.011 (above the 1 % threshold)."""
    out = {}
    for p in (0.001, 0.005, 0.009, 0.011):
        try:
            row = lab.physical(lab.qaoa_logical(100, 4), p=p, choose=sol.choose_distance)
            out[p] = (row["distance"], row["physical_qubits"])
        except ValueError as e:
            out[p] = str(e).split(":")[0]
    return out


if __name__ == "__main__":
    print("better_hardware", better_hardware())
    print("near_threshold ", near_threshold())
