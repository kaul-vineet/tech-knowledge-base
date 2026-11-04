"""Build task check (failureLab proof). Default: tests solution_strict.py.
Test YOUR version (the shipped pq_hybrid.py has the silent classical fallback):
  macOS    BUILD_TARGET=mine python -m unittest -v test_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<module> picks any other module."""
import contextlib
import importlib
import io
import os
import random
import unittest

import pq_hybrid as pq

MODULE = "pq_hybrid" if os.environ.get("BUILD_TARGET") == "mine" else os.environ.get("BUILD_IMPL", "solution_strict")
impl = importlib.import_module(MODULE)


class TestNoSilentFallback(unittest.TestCase):
    def finish(self, st, share):
        with contextlib.redirect_stdout(io.StringIO()):
            return impl.client_finish(st, share)

    def test_downgraded_share_is_refused(self):
        rng = random.Random(18)
        for _ in range(2):
            st, ch = pq.client_hello()
            sh, _ = pq.server_respond(ch)
            with self.assertRaises(pq.HandshakeError):
                self.finish(st, sh[-rng.choice([pq.X_LEN, pq.X_LEN + 1]):])

    def test_one_extra_byte_is_refused(self):
        st, ch = pq.client_hello()
        sh, _ = pq.server_respond(ch)
        with self.assertRaises(pq.HandshakeError):
            self.finish(st, sh + b"\x00")

    def test_normal_handshake_still_works(self):
        st, ch = pq.client_hello()
        sh, ks = pq.server_respond(ch)
        self.assertEqual(self.finish(st, sh), (ks, pq.GROUP))


if __name__ == "__main__":
    unittest.main()
