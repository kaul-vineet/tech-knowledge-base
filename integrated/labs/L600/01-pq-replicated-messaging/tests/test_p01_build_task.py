"""Build task check (failureLab proof). Default: tests solution/nonce_derived.py.
Test YOUR version (the shipped nonce_derived.py keeps a leader-local counter):
  macOS    BUILD_TARGET=mine python -m unittest -v test_p01_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_p01_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<path to a .py file> picks any other implementation."""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402
from harness import nonce_reuse  # noqa: E402

LAB = Path(__file__).resolve().parents[1]
PATH = LAB / "nonce_derived.py" if os.environ.get("BUILD_TARGET") == "mine" else Path(
    os.environ.get("BUILD_IMPL", LAB / "solution" / "nonce_derived.py"))
spec = importlib.util.spec_from_file_location("p01_build_target", PATH)
impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impl)


class TestDerivedNonce(unittest.TestCase):
    def test_twelve_bytes(self):
        self.assertEqual(len(impl.DerivedNonce().next(1)), 12)

    def test_new_leader_never_repeats_old_leader_nonces(self):
        old, new = impl.DerivedNonce(), impl.DerivedNonce()
        a = {old.next(3) for _ in range(50)}
        b = {new.next(4) for _ in range(50)}
        self.assertEqual((len(a), len(b), a & b), (50, 50, set()))

    def test_restarted_leader_in_a_later_term(self):
        first = impl.DerivedNonce()
        before = {first.next(5) for _ in range(20)}
        after = {impl.DerivedNonce().next(7) for _ in range(20)}  # volatile counter lost on restart
        self.assertFalse(before & after)

    def test_deposed_sealer_refused(self):
        n = impl.DerivedNonce()
        n.next(5)
        with self.assertRaises(ValueError):
            n.next(4)

    def test_end_to_end_no_reuse_with_failovers(self):
        svc, _ = sc.traffic(400, seed=11, chaos=0.03, nonce_factory=impl.DerivedNonce)
        self.assertGreater(svc.failovers, 0)
        self.assertEqual(nonce_reuse(svc.wire), {})


if __name__ == "__main__":
    unittest.main()
