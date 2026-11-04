"""Parity check (CI, pending here): OPA and rego_lite must give the same decision for every requirement case.

Needs the `opa` binary (OPA 1.21.4: brew install opa, or opa_windows_amd64.exe from the GitHub releases).
Run: python opa_parity.py [policy-folder]    exit 0 = same decisions; exit 2 = opa not installed (skipped)
"""
import json
import pathlib
import shutil
import subprocess
import sys

from rego_lite import DecisionPoint, load_policy

HERE = pathlib.Path(__file__).resolve().parent


def opa_allowed(opa, rego, inp):
    out = subprocess.run([opa, "eval", "--format=json", "-d", str(rego), "--stdin-input", "data.loans.authz.allowed"],
                         input=json.dumps(inp), capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)["result"][0]["expressions"][0]["value"]


def main(folder="solution"):
    opa = shutil.which("opa")
    if not opa:
        print("opa not found: parity check skipped (runs in the CI job 'opa')")
        return 2
    rego = HERE / folder / "loans.rego"
    pdp = DecisionPoint(load_policy(rego))
    cases = json.loads((HERE / "policy" / "cases.json").read_text(encoding="utf-8"))["cases"]
    diff = [c["id"] for c in cases if opa_allowed(opa, rego, c["input"]) != pdp.decide(c["input"])["allowed"]]
    print(f"opa vs rego_lite on {len(cases)} cases: {len(diff)} differences {diff}")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
