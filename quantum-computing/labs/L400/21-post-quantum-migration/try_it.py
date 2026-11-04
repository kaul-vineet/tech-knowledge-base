"""Try-it checks for lab 21. Run: python try_it.py   (stdlib + cryptography)"""
import json

import agility
import pqc_lab as lab
import solution_scanner as scanner


def longer_secrecy(file="toy_app/api_client.py", years=8):
    """Try 1: legal says partner API traffic must now stay secret 8 years. Which items become P1?"""
    classification = json.loads((lab.APP / "data_classification.json").read_text(encoding="utf-8"))
    classification[file]["secrecy_years"] = years
    return sorted(f"{s['file']}:{s['line']}" for s in lab.plan(scanner.scan(), classification) if s["priority"].startswith("P1"))


def old_receiver():
    """Try 2: the sender switched to the hybrid KEM, but a receiver still only knows X25519. What happens?"""
    sk, pk = agility.REGISTRY["x25519+ml-kem-768"].keygen()
    _, envelope = agility.establish(pk)                         # CONFIG says hybrid
    old_registry = {"x25519": agility.REGISTRY["x25519"]}
    try:
        old_registry[json.loads(envelope)["kem"]]
    except KeyError as e:
        return f"receiver rejects envelope: unknown kem {e}"
    return "accepted"


if __name__ == "__main__":
    print("longer_secrecy", longer_secrecy())
    print("old_receiver  ", old_receiver())
