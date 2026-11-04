"""Equivalent tool: `openssl s_client` reaches the same verdicts as the Python client.
Skipped unless an `openssl` binary is on PATH (none in the sandbox; CI runners have one).
Only exit codes are checked: OpenSSL 3.x and LibreSSL (macOS /usr/bin/openssl) print different text."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import tls_localhost as lab

OPENSSL = shutil.which("openssl")


@unittest.skipUnless(OPENSSL, "openssl CLI not installed")
class TestOpenSSLClient(unittest.TestCase):
    def s_client(self, port, cafile, *extra):
        cmd = [OPENSSL, "s_client", "-connect", f"127.0.0.1:{port}", "-servername", "localhost",
               "-CAfile", str(cafile), "-verify_return_error", *extra]
        return subprocess.run(cmd, input=b"", capture_output=True, timeout=30)

    def test_trusted_and_untrusted(self):
        with tempfile.TemporaryDirectory() as tmp:
            pki, other = lab.make_pki(Path(tmp) / "pki"), lab.make_pki(Path(tmp) / "other")
            port = lab.start_server(lab.server_context(pki), connections=2)
            ok = self.s_client(port, pki / "ca.pem")
            self.assertEqual(ok.returncode, 0, ok.stdout.decode(errors="replace")[-500:])
            self.assertNotEqual(self.s_client(port, other / "ca.pem").returncode, 0)


if __name__ == "__main__":
    unittest.main()
