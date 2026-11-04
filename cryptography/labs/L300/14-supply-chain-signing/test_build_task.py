"""Build task check (failureLab proof). Default: tests solution_strict.py.
Test YOUR version:  macOS  BUILD_IMPL=release_sign python -m unittest -v test_build_task
                    Windows  $env:BUILD_IMPL="release_sign"; python -m unittest -v test_build_task"""
import importlib
import os
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import release_sign as rs

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_strict"))


class TestStrictInstall(unittest.TestCase):
    def setUp(self):
        self._tmp, self._out = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
        self.dist, self.out = Path(self._tmp.name), Path(self._out.name)
        key = Ed25519PrivateKey.generate()
        self.trusted = {rs.key_id(key.public_key()): key.public_key()}
        rs.build_artifacts(self.dist)
        rs.sign_release(self.dist, key, "1.0.0")

    def tearDown(self):
        self._tmp.cleanup()
        self._out.cleanup()

    def test_clean_release_installs(self):
        self.assertEqual(len(impl.install(self.dist, self.out, self.trusted)), 4)

    def test_swapped_file_rejected(self):
        (self.dist / "app" / "core.py").write_bytes(b"evil\n")
        with self.assertRaisesRegex(rs.Rejected, "digest mismatch: app/core.py"):
            impl.install(self.dist, self.out, self.trusted)
        self.assertEqual(list(self.out.rglob("*")), [])  # nothing copied

    def test_unknown_file_rejected(self):
        (self.dist / "app" / "zz_extra.pth").write_bytes(b"import os\n")
        with self.assertRaisesRegex(rs.Rejected, "unknown file"):
            impl.install(self.dist, self.out, self.trusted)

    def test_seeded_attack_rejected(self):
        rs.tamper(self.dist)
        with self.assertRaises(rs.Rejected):
            impl.install(self.dist, self.out, self.trusted)


if __name__ == "__main__":
    unittest.main()
