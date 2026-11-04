"""Equivalent tool: minisign signs and verifies the lab's MANIFEST.json (skipped when minisign is not installed).
Flags from the minisign release notes (-G, -W unencrypted key, -S, -V, -p, -s, -m); see KNOWN-GAPS."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import release_sign as rs

MINISIGN = shutil.which("minisign")


@unittest.skipUnless(MINISIGN, "minisign not installed")
class TestMinisign(unittest.TestCase):
    def run_ms(self, *args, cwd):
        return subprocess.run([MINISIGN, *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60)

    def test_sign_verify_and_detect_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            rs.build_artifacts(d)
            rs.sign_release(d, Ed25519PrivateKey.generate(), "1.0.0")
            self.assertEqual(self.run_ms("-G", "-W", "-p", "ms.pub", "-s", "ms.key", cwd=d).returncode, 0)
            self.assertEqual(self.run_ms("-S", "-s", "ms.key", "-m", "MANIFEST.json", cwd=d).returncode, 0)
            self.assertEqual(self.run_ms("-V", "-p", "ms.pub", "-m", "MANIFEST.json", cwd=d).returncode, 0)
            raw = (d / "MANIFEST.json").read_bytes()
            (d / "MANIFEST.json").write_bytes(raw.replace(b"1.0.0", b"1.0.1"))
            self.assertNotEqual(self.run_ms("-V", "-p", "ms.pub", "-m", "MANIFEST.json", cwd=d).returncode, 0)


if __name__ == "__main__":
    unittest.main()
