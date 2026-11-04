"""Fitness functions for lab 21 (docs/adr/0001-crypto-agility.md). Run: python -m unittest test_fitness -v
(same BUILD_TARGET / BUILD_TASK_MODULE switch as test_build_task)

Thresholds: inventory recall = precision = 1.0 against EXPECTED_INVENTORY.json · ratchet: no quantum-vulnerable
use outside migration_baseline.json (the list may only shrink) · the configured KEM is hybrid or post-quantum.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import agility
import buildtarget
import pqc_lab as lab

mod = buildtarget.load("solution_scanner", "my_scanner")
HERE = Path(__file__).resolve().parent
EXPECTED = json.loads((HERE / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))
BASELINE = {(b["file"], b["algorithm"]) for b in json.loads((HERE / "migration_baseline.json").read_text(encoding="utf-8"))}


def new_vulnerable(findings):
    return [f for f in findings if f["usage"] != "symmetric" and (f["file"], f["algorithm"]) not in BASELINE]


class MigrationFitness(unittest.TestCase):
    def test_recall_and_precision(self):
        found = {tuple(sorted(f.items())) for f in mod.scan()}
        truth = {tuple(sorted(f.items())) for f in EXPECTED}
        self.assertEqual((len(found & truth) / len(truth), len(found & truth) / max(len(found), 1)), (1.0, 1.0))

    def test_ratchet_blocks_new_quantum_vulnerable_code(self):
        self.assertEqual(new_vulnerable(mod.scan()), [])
        with tempfile.TemporaryDirectory(dir=HERE, ignore_cleanup_errors=True) as tmp:          # a copy of the app plus one new ECDH use
            app = Path(tmp) / "toy_app"
            shutil.copytree(lab.APP, app)
            (app / "chat.py").write_text("from cryptography.hazmat.primitives.asymmetric import ec\n"
                                         "def k(p):\n    return ec.ECDH()\n", encoding="utf-8")
            added = [f for f in new_vulnerable(mod.scan(app)) if f["file"].endswith("chat.py")]
            self.assertEqual(len(added), 1)

    def test_configured_kem_is_quantum_safe(self):
        self.assertIn(agility.CONFIG["kem"], {"x25519+ml-kem-768", "ml-kem-768"})


if __name__ == "__main__":
    unittest.main()
