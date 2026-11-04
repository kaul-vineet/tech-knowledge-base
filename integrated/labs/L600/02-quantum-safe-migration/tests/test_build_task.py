"""Build task: make the inventory see crypto modules loaded by name.
    default                         -> solution/inventory_dynamic.py (reference)
    BUILD_TARGET=mine               -> my_inventory.py in the lab folder (yours)
    BUILD_TASK_MODULE=inventory     -> the shipped scanner (fails: the blind spot)"""
import importlib
import json
import os
import unittest

import _lab
import _kb
import fitness


def target():
    name = os.environ.get("BUILD_TASK_MODULE")
    if name:
        return importlib.import_module(name)
    if os.environ.get("BUILD_TARGET") == "mine":
        return importlib.import_module("my_inventory")
    return _kb.load_file(_lab.LAB / "solution" / "inventory_dynamic.py", "inventory_dynamic")


EXPECTED = json.loads((_lab.LAB / "EXPECTED_INVENTORY.json").read_text(encoding="utf-8"))


class TestBuildTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = target()

    def test_dynamic_load_is_found(self):
        found = self.mod.scan("after", messaging="faults/messaging_bypass")
        want = EXPECTED["bypass_dynamic"][0]
        got = [f for f in found if f["algorithm"].startswith("dynamic:")]
        self.assertEqual([(f["file"], f["line"], f["algorithm"], f["usage"]) for f in got],
                         [(want["file"], want["line"], want["algorithm"], want["usage"])])

    def test_f1_now_fails_statically_for_the_bypass(self):
        found = self.mod.scan("after", messaging="faults/messaging_bypass")
        self.assertFalse(fitness.f1_no_classical_kex_for_exposed_data(found)["ok"])

    def test_no_new_false_positives(self):
        import inventory
        self.assertEqual(inventory.score(self.mod.scan("before"), EXPECTED["before"])["precision"], 1.0)
        self.assertFalse(any(f["algorithm"].startswith("dynamic:") for f in self.mod.scan("after")))


if __name__ == "__main__":
    unittest.main()
