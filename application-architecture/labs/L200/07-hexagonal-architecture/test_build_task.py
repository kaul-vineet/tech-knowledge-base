"""Build task check: a JSON-file driven adapter passes the SAME port contract, domain untouched.

By default this checks solution/driven_jsonfile.py. To check your own file in the lab folder:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import ast
import importlib.util
import os
import pathlib
import tempfile
import unittest

from domain import LoanService
from test_hexagon import ADAPTERS, StoreContract

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("driven_jsonfile.py" if os.environ.get("CHECK_MINE") else "solution/driven_jsonfile.py")


def load_target():
    spec = importlib.util.spec_from_file_location("driven_jsonfile_under_test", TARGET)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class JsonFileStoreContractTest(StoreContract, unittest.TestCase):
    def make_store(self):
        tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(tmp.cleanup)
        return load_target().JsonFileLoanStore(pathlib.Path(tmp.name) / "loans.json")

    def test_domain_rules_run_on_the_new_adapter(self):
        loans = LoanService(self.store, max_active_per_member=1)
        loans.borrow("b1", "m1")
        self.assertEqual(loans.give_back(1).returned, True)
        self.assertEqual(loans.borrow("b1", "m2").id, 2)

    def test_adapter_depends_only_on_the_hexagon(self):
        tree = ast.parse(TARGET.read_text(encoding="utf-8"))
        names = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(names & ADAPTERS, set())


if __name__ == "__main__":
    unittest.main()
