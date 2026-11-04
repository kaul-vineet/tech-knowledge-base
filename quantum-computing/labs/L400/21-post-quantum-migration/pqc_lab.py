"""Lab 21 - quantum and post-quantum: inventory a codebase's crypto and plan the migration.

Run:  python pqc_lab.py      (stdlib + cryptography 50.0.2; ML-KEM-768 runs locally)
1. Shor in context: what breaking RSA-2048 / P-256 needs (lesson 19's model + published estimates).
2. Inventory toy_app/: every public-key use, its purpose, and the data's secrecy lifetime.
3. Plan: replacement per NIST IR 8547 (ML-KEM for key establishment, ML-DSA for signatures, keep AES-256),
   priority by Mosca's inequality X + Y > Z ("harvest now, decrypt later").
4. Crypto agility: X25519 vs ML-KEM-768 vs the hybrid, behind one interface (agility.py).
The FAULT: scan() below is a grep for "RSA". Fix it in the build task (solution_scanner.py).
"""
import json
import re
from pathlib import Path

import agility
import shor_context

HERE = Path(__file__).resolve().parent
APP = HERE / "toy_app"
MIGRATION_YEARS, YEARS_TO_CRQC = 3, 9          # Y and Z in Mosca's inequality: planning assumptions, not forecasts
REPLACEMENT = {"key-establishment": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition",
               "signature": "ML-DSA-65 (FIPS 204)", "symmetric": "keep (AES-256 / SHA-256 not broken by Shor)"}


def scan(root=APP):
    """NAIVE: grep every file for 'rsa'. Finds words, not uses: misses X25519/ECDH/ECDSA, flags a docstring."""
    found = []
    for path in sorted(p for p in root.rglob("*") if p.suffix in (".py", ".toml")):
        for no, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = re.search(r"rsa[-_]?(\d+)?", text, re.I)
            if m:
                found.append({"file": path.relative_to(HERE).as_posix(), "line": no,
                              "algorithm": f"RSA-{m.group(1)}" if m.group(1) else "RSA", "usage": "unknown"})
    return found


def plan(inventory, classification=None):
    """Code decides priority: P1 if key establishment protects data that must outlive Z - Y years (HNDL)."""
    classification = classification or json.loads((APP / "data_classification.json").read_text(encoding="utf-8"))
    steps = []
    for item in inventory:
        years = classification.get(item["file"], {}).get("secrecy_years", 0)
        if item["usage"] == "key-establishment" and years + MIGRATION_YEARS > YEARS_TO_CRQC:
            prio = "P1 now (harvest now, decrypt later)"
        elif item["usage"] in ("key-establishment", "signature", "unknown"):
            prio = "P2 before 2030 (deprecated after 2030, disallowed after 2035)"
        else:
            prio = "none"
        steps.append({**item, "secrecy_years": years, "priority": prio,
                      "replacement": REPLACEMENT.get(item["usage"], "review manually")})
    return sorted(steps, key=lambda s: (s["priority"], s["file"], s["line"]))


if __name__ == "__main__":
    print(json.dumps({"shor_model": shor_context.our_model(), "ecc": shor_context.ecc_logical(256)}))
    for cited in shor_context.CITED:
        print(json.dumps(cited))
    inventory = scan()
    print(json.dumps({"scanner": "grep", "findings": len(inventory)}))
    for step in plan(inventory):
        print(json.dumps(step))
    for name in agility.REGISTRY:
        print(json.dumps(agility.measure(name)))
