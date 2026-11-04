"""Every seeded fault must turn the scorecard NO-GO, and exactly the expected criteria must fail."""
import contextlib
import io
import json
import unittest

import run_capstone

EXPECTED = {
    "fines-rounding": ["fines parallel run", "fines cut over"],
    "cross-tenant-policy": ["cross-library reads", "policy requirement cases", "cross-library probes denied"],
    "unscoped-query": ["tenant guard", "tenant-scoped SQL", "cross-library reads"],
    "duplicate-delivery": ["idempotent consumers"],
}


class FaultTest(unittest.TestCase):
    def test_each_fault_is_caught(self):
        for fault, failed in EXPECTED.items():
            with self.subTest(fault=fault):
                buffer = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()):
                    code = run_capstone.main(["--fault", fault], out=buffer)
                summary = json.loads(buffer.getvalue().splitlines()[-1])
                self.assertEqual((code, summary["verdict"], summary["failed"]), (1, "NO-GO", failed))


if __name__ == "__main__":
    unittest.main()
