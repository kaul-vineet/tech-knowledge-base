"""Run every L100-L400 lab, the capstone and the L500 theorem checks the same way on macOS, Windows and Linux (used by CI; works locally too).

  python tools/run_labs.py              # numpy cross-checks, L300/L400 main labs, try_it, solutions, agent assist (fake model), unittest
  python tools/run_labs.py --sdk        # also each SDK lab script (Qiskit/Aer/scipy); saves observed-*.txt next to each lab
  python tools/run_labs.py --extras     # L300 only: also the Mitiq and PennyLane scripts (labs/L300/requirements-extras.txt)
  python tools/run_labs.py --qdk        # L400 only: also the QDK resource-estimator script (labs/L400/requirements-qdk.txt)
  python tools/run_labs.py --level L400 # only one level (L400 includes the capstone)
  python tools/run_labs.py --level L500 # L500 theorem checks + research/l500_checks.py, check_l500_qbank.py, qbank_checks.py
Run from the topic folder. Uses sys.executable and pathlib only, so no bash/PowerShell differences.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
SHARED = [LABS / "_shared" / "local_agent", LABS / "_shared" / "qsim", LABS / "_shared" / "qopt"]
MAIN = {
    "L100": {
        "01-setup-environment": "check_env.py",
        "02-qubits-and-gates": "gates_lab.py",
        "03-shots-counts-probability": "shots_lab.py",
        "04-bell-pair-entanglement": "bell_lab.py",
        "05-openqasm-portability": "qasm_lab.py",
        "06-same-circuit-two-frameworks": "two_frameworks_lab.py",
    },
    "L200": {
        "07-bernstein-vazirani": "bv_lab.py",
        "08-grover-search": "grover_lab.py",
        "09-qft-building-block": "qft_lab.py",
        "10-parameterized-circuits": "param_lab.py",
        "11-transpile-to-device": "transpile_lab.py",
    },
    "L300": {   # numpy main labs: they run everywhere; SDK scripts are listed in L300_SDK / L300_EXTRAS
        "12-noise-models": "noise_lab.py",
        "13-error-mitigation": "mitigation_lab.py",
        "14-qaoa-maxcut": "qaoa_lab.py",
        "15-hybrid-vqe-loop": "vqe_lab.py",
        "16-quantum-classifier": "classifier_lab.py",
    },
    "L400": {   # numpy (+ cryptography for 21) main labs; SDK scripts in L400_SDK / L400_QDK
        "17-hybrid-architecture": "orchestrator.py",
        "18-benchmark-vs-classical": "bench_lab.py",
        "19-resource-estimation": "estimate_lab.py",
        "20-error-aware-compilation": "compile_lab.py",
        "21-post-quantum-migration": "pqc_lab.py",
        "22-capstone": "run_capstone.py",
    },
    "L500": {   # numpy theorem checks (lessons 23-25); lessons 26-27 have no lab code
        "23-linear-algebra-for-qubits": "theorems.py",
        "24-quantum-information-basics": "theorems.py",
        "25-algorithms-and-complexity": "theorems.py",
    },
}
L500_CHECKS = ["l500_checks.py", "check_l500_qbank.py", "qbank_checks.py"]
L300_SDK = {"12-noise-models": ["noise_aer.py"], "14-qaoa-maxcut": ["qaoa_qiskit.py"], "15-hybrid-vqe-loop": ["vqe_qiskit.py"]}
L300_EXTRAS = {"13-error-mitigation": ["mitiq_zne.py"], "16-quantum-classifier": ["classifier_pennylane.py"]}
L400_SDK = {"17-hybrid-architecture": ["sampler_qiskit.py"], "18-benchmark-vs-classical": ["bench_qiskit.py"],
            "19-resource-estimation": ["count_qiskit.py"], "20-error-aware-compilation": ["compile_qiskit.py"]}
L400_QDK = {"19-resource-estimation": ["estimate_qdk.py"]}
ENV = {**os.environ, "PYTHONUTF8": "1"}   # Windows: UTF-8 stdout even when output is piped (circuit drawings)


def run(cwd, *args, save=None):
    print(f"\n$ ({cwd.relative_to(ROOT)}) python {' '.join(args)}", flush=True)
    proc = subprocess.run([sys.executable, *args], cwd=cwd, env=ENV, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    print(proc.stdout + proc.stderr, end="", flush=True)
    if save:
        (cwd / save).write_text(proc.stdout, encoding="utf-8")
    if proc.returncode:
        sys.exit(f"FAILED ({proc.returncode}): python {' '.join(args)} in {cwd}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", action="store_true", help="also run the SDK lab scripts (needs requirements.txt)")
    parser.add_argument("--extras", action="store_true", help="also the L300 Mitiq / PennyLane scripts")
    parser.add_argument("--qdk", action="store_true", help="also the L400 QDK resource-estimator script")
    parser.add_argument("--level", choices=sorted(MAIN), action="append", help="run only this level (repeatable)")
    args = parser.parse_args()
    sdk, levels = args.sdk, args.level or sorted(MAIN)
    for shared in SHARED:
        run(shared, "-m", "unittest", "-v")
    for level in levels:
        for lab in sorted(MAIN[level]):
            d = LABS / level / lab
            for f in sorted(d.glob("crosscheck*.py")):
                run(d, f.name)
            if sdk or level in ("L300", "L400", "L500"):
                run(d, MAIN[level][lab], save="observed-output.txt" if sdk else None)
            if level == "L300":
                for script in (L300_SDK.get(lab, []) if sdk else []) + (L300_EXTRAS.get(lab, []) if args.extras else []):
                    run(d, script, save=f"observed-{Path(script).stem}.txt")
            if level == "L400":
                for script in (L400_SDK.get(lab, []) if sdk else []) + (L400_QDK.get(lab, []) if args.qdk else []):
                    run(d, script, save=f"observed-{Path(script).stem}.txt")
            if (d / "try_it.py").exists():
                run(d, "try_it.py", save="observed-try-it.txt" if sdk else None)
            for f in sorted(d.glob("solution_*.py")):
                run(d, f.name)
            if (d / "agent_assist.py").exists():
                run(d, "agent_assist.py", "--fake", save="observed-agent-assist.txt" if sdk else None)
            run(d, "-m", "unittest", "-v")
    if "L500" in levels:
        for script in L500_CHECKS:
            run(ROOT / "research", script)
    if sdk and "L100" in levels:
        run(LABS / "L100" / "05-openqasm-portability", "crosscheck_qasm_numpy.py", "bell.qasm")
    print("\nall labs OK")


if __name__ == "__main__":
    main()
