"""Try-it checks for lab 12. Run: python try_it.py   (numpy only; the Aer variant runs when qiskit-aer is installed)"""
import importlib.util

import noise_lab as lab

HAVE_AER = importlib.util.find_spec("qiskit_aer") is not None


def symmetric_noise():
    """Try 1: damp = 0 and p01 = p10 = 0.03. Does the 00/11 imbalance survive?"""
    m = lab.metrics(3, {**lab.NOISE, "damp": 0.0, "p01": 0.03, "p10": 0.03})
    return {"p_all0": m["p_all0"], "p_all1": m["p_all1"]}


def readout_vs_gate_noise():
    """Try 2: GHZ-4 with ONLY 5% readout flips vs ONLY p2 = 0.05 on each CX. Which costs more success?"""
    zero = {k: 0.0 for k in lab.NOISE}
    return {"readout_only": lab.metrics(4, {**zero, "p01": 0.05, "p10": 0.05})["success"],
            "cx_only": lab.metrics(4, {**zero, "p2": 0.05})["success"]}


def sdk_results():
    import noise_aer
    zero = {k: 0.0 for k in lab.NOISE}
    return {"readout_only": noise_aer.aer_success(4, {**zero, "p01": 0.05, "p10": 0.05}),
            "cx_only": noise_aer.aer_success(4, {**zero, "p2": 0.05})}


if __name__ == "__main__":
    print("symmetric_noise      ", symmetric_noise())
    print("readout_vs_gate_noise", readout_vs_gate_noise())
    if HAVE_AER:
        print("aer readout_vs_gate_noise", sdk_results())
