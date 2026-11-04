import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import hash_and_hmac as lab


class TestHashing(unittest.TestCase):
    def test_nist_and_empty_vectors(self):
        self.assertEqual(lab.sha256_text("abc"), lab.NIST_ABC)
        self.assertEqual(lab.sha256_text(""), lab.EMPTY)

    def test_file_streaming_matches_oneshot_and_tamper_detected(self):
        data = os.urandom(300_000)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.bin"
            p.write_bytes(data)
            digest = lab.sha256_file(p, chunk_size=4096)
            self.assertEqual(digest, hashlib.sha256(data).hexdigest())
            tool, cli = lab.os_sha256(p)
            if tool is not None:  # sha256sum / shasum / certutil, whichever this OS has
                self.assertEqual(cli, digest)
            with open(p, "r+b") as f:
                f.write(b"\x00" if data[0] != 0 else b"\x01")
            self.assertNotEqual(lab.sha256_file(p), digest)

    def test_os_tool_output_layouts_parse(self):
        d = lab.NIST_ABC
        layouts = {"sha256sum": f"\\{d}  C:\\\\tmp\\\\f.bin\n",  # Git Bash escapes backslash paths
                   "shasum": f"{d}  /tmp/f.bin\n",
                   "certutil": f"SHA256 hash of f.bin:\n{d.upper()}\nCertUtil: -hashfile command completed successfully.\n"}
        for tool, out in layouts.items():
            with mock.patch.object(lab.shutil, "which", side_effect=lambda t, tool=tool: t == tool), \
                    mock.patch.object(lab.subprocess, "run", return_value=mock.Mock(stdout=out)):
                self.assertEqual(lab.os_sha256("f.bin"), (tool, d), tool)

    def test_hmac_rfc4231_and_verify(self):
        self.assertEqual(lab.hmac_sha256(b"Jefe", b"what do ya want for nothing?"), lab.RFC4231_TC2)
        key = os.urandom(32)
        tag = lab.hmac_sha256(key, b"m")
        self.assertTrue(lab.verify_hmac(key, b"m", tag))
        self.assertFalse(lab.verify_hmac(key, b"n", tag))


if __name__ == "__main__":
    unittest.main()
