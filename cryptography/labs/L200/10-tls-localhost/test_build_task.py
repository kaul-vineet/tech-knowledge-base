"""Build task check. Default: tests solution_mtls.py.
Test YOUR version:  macOS  BUILD_IMPL=tls_localhost python -m unittest test_build_task
                    Windows  $env:BUILD_IMPL="tls_localhost"; python -m unittest test_build_task"""
import importlib
import os
import ssl
import tempfile
import time
import unittest
from pathlib import Path

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_mtls"))


class TestMTLS(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pki = impl.make_pki_with_client(Path(self.tmp.name) / "pki")

    def tearDown(self):
        self.tmp.cleanup()

    def test_client_with_cert_is_identified(self):
        seen = []
        port = impl.start_mtls_server(impl.mtls_server_context(self.pki), seen)
        self.assertEqual(impl.connect_mtls(port, self.pki), b"hello build-agent-7\n")
        self.assertEqual(seen, ["build-agent-7"])

    def test_client_without_cert_is_rejected(self):
        seen = []
        port = impl.start_mtls_server(impl.mtls_server_context(self.pki), seen)
        with self.assertRaises((ssl.SSLError, ConnectionError)):
            impl.connect_mtls(port, self.pki, with_cert=False)
        for _ in range(50):
            if seen:
                break
            time.sleep(0.05)
        self.assertTrue(seen and seen[0].startswith("rejected"))


if __name__ == "__main__":
    unittest.main()
