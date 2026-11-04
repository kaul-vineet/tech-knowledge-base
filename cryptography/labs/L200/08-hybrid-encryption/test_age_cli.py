"""Equivalent tool: the age CLI does the same job (X25519 recipient + HKDF + ChaCha20-Poly1305).
Skipped unless `age` and `age-keygen` are on PATH (CI installs them on ubuntu/macOS)."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which("age") and shutil.which("age-keygen"), "age CLI not installed")
class TestAgeCli(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            out = subprocess.run(["age-keygen", "-o", str(d / "key.txt")], capture_output=True, encoding="utf-8",
                                 errors="replace", timeout=60, check=True)
            recipient = next(w for w in (out.stderr + out.stdout).split() if w.startswith("age1"))
            (d / "msg.txt").write_text("hello age\n", encoding="utf-8")
            subprocess.run(["age", "-r", recipient, "-o", str(d / "msg.age"), str(d / "msg.txt")], check=True, timeout=60)
            head = (d / "msg.age").read_bytes()[:80]
            self.assertTrue(head.startswith(b"age-encryption.org/v1\n-> X25519 "))
            dec = subprocess.run(["age", "-d", "-i", str(d / "key.txt"), str(d / "msg.age")],
                                 capture_output=True, check=True, timeout=60)
            self.assertEqual(dec.stdout.replace(b"\r\n", b"\n"), b"hello age\n")


if __name__ == "__main__":
    unittest.main()
