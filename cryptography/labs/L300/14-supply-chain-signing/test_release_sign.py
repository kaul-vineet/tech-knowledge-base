import json
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import release_sign as rs


class TestReleaseSign(unittest.TestCase):
    def setUp(self):
        self._tmp, self._out = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
        self.dist, self.out = Path(self._tmp.name), Path(self._out.name)
        self.key = Ed25519PrivateKey.generate()
        self.trusted = {rs.key_id(self.key.public_key()): self.key.public_key()}
        rs.build_artifacts(self.dist)
        rs.sign_release(self.dist, self.key, "1.0.0")

    def tearDown(self):
        self._tmp.cleanup()
        self._out.cleanup()

    def test_manifest_lists_digests_with_posix_paths(self):
        files = json.loads((self.dist / "MANIFEST.json").read_bytes())["files"]
        self.assertEqual(sorted(files), ["README.txt", "app/__init__.py", "app/core.py", "app/data.json"])
        self.assertEqual(files["app/core.py"]["sha256"], rs.digest(self.dist / "app" / "core.py"))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as other:
            rs.build_artifacts(Path(other))
            self.assertEqual(rs.digest(Path(other) / "app" / "core.py"), rs.digest(self.dist / "app" / "core.py"))

    def test_manifest_edit_and_unknown_signer_rejected(self):
        stranger = Ed25519PrivateKey.generate().public_key()
        with self.assertRaisesRegex(rs.Rejected, "unknown signer"):
            rs.install(self.dist, self.out, {rs.key_id(stranger): stranger})
        raw = (self.dist / "MANIFEST.json").read_bytes()
        (self.dist / "MANIFEST.json").write_bytes(raw.replace(b"1.0.0", b"1.0.1"))
        with self.assertRaisesRegex(rs.Rejected, "signature invalid"):
            rs.install(self.dist, self.out, self.trusted)

    def test_fault_naive_install_accepts_swapped_files(self):
        victim = rs.tamper(self.dist)
        self.assertEqual(victim, "README.txt")  # seeded: same victim every run
        installed = rs.install(self.dist, self.out, self.trusted)  # the bug: signature OK, files never checked
        self.assertIn("app/zz_extra.pth", installed)


if __name__ == "__main__":
    unittest.main()
