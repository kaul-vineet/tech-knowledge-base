"""Seam cryptography <-> ai-agents: what was signed is exactly what is loaded and what the model sees."""
import json
import unittest

import _lab
import manifest
import scenarios
from run_project import OUT, mcp_pin, write


class TestManifestLoaderSeam(unittest.TestCase):
    def test_edited_manifest_rejected_others_still_load(self):
        signed = scenarios.signed_pack()
        signed[3]["manifest"]["risk"] = "low"  # downgrade send_email's risk after signing
        reg, rejected = manifest.load_tools(signed, manifest.trusted_keys())
        self.assertEqual(rejected, ["send_email: manifest signature invalid"])
        self.assertEqual(len(reg), 4)

    def test_unknown_signer_rejected(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        rogue = manifest.publish(scenarios.DEFS[:1], Ed25519PrivateKey.generate())
        reg, rejected = manifest.load_tools(rogue, manifest.trusted_keys())
        self.assertEqual(reg, {})
        self.assertIn("unsigned or unknown signer", rejected[0])

    def test_impl_path_cannot_escape_tools_dir(self):
        signed = scenarios.signed_pack()
        signed[0]["manifest"]["impl"] = "../host.py"
        _, rejected = manifest.load_tools(signed, manifest.trusted_keys())
        self.assertEqual(len(rejected), 1)

    def test_poisoned_mcp_description_refused(self):
        OUT.mkdir(exist_ok=True)
        path = OUT / "toolpack.seam.json"
        write(path, json.dumps(scenarios.signed_pack()))
        problems, _ = mcp_pin(path, _lab.registry(), poison=True)
        self.assertEqual(problems, ["search_docs: definition differs from the signed manifest"])
        path.unlink()


if __name__ == "__main__":
    unittest.main()
