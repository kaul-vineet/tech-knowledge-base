"""Fitness function for ADR-018 (cart = OR-Set, counters = PN-Counter, single fields = LWW-Register with tie-break).
Keeps the decision true: on 3 seeds x 500 random histories every type obeys the merge laws and converges, and a
reference cart session ships at most 4096 bytes per sync. Default target = solution_crdts.py; BUILD_TARGET=mine."""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from helpers import check_laws, converge, size  # noqa: E402

FILE = "crdts.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_crdts.py"
spec = importlib.util.spec_from_file_location("fitness_crdts", HERE / FILE)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
SYNC_BUDGET_BYTES = 4096


class CRDTFitness(unittest.TestCase):
    def test_every_chosen_type_is_a_join(self):
        for cls in (cm.ORSet, cm.PNCounter, cm.LWWRegister):
            for seed in (18, 19, 20):
                with self.subTest(cls=cls.__name__, seed=seed):
                    self.assertEqual(set(check_laws(cls, seed)["counts"].values()), {"500/500"})
                    self.assertEqual(converge(cls, seed)["converged"], "500/500")

    def test_reference_cart_session_fits_the_sync_budget(self):
        cart = cm.ORSet()  # 60 adds over 20 products, 5 removes: a busy shopping session (1,311 bytes here)
        for k in range(60):
            cart.add(f"sku-{k % 20}", ("phone", k))
            if k % 12 == 5:
                cart.remove(f"sku-{k % 20}")
        self.assertLessEqual(size(cart), SYNC_BUDGET_BYTES)


if __name__ == "__main__":
    unittest.main()
