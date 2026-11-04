"""M1: signed tool manifests + verifying loader (+ MCP tools/list pinned to the manifests)."""
import json
import shutil
import unittest

import _lab
import manifest
import scenarios
from run_project import OUT, mcp_pin, tamper_cases, write


class TestSignedTools(unittest.TestCase):
    def test_publish_and_load_all_five(self):
        reg, rejected = scenarios.load_registry()
        self.assertEqual(sorted(reg), ["delete_file", "read_file", "save_memory", "search_docs", "send_email"])
        self.assertEqual(rejected, [])

    def test_each_tamper_case_is_rejected(self):
        OUT.mkdir(exist_ok=True)
        self.assertEqual(tamper_cases(scenarios.signed_pack(), set()),
                         {"modified implementation": 1, "edited manifest": 1, "unsigned manifest": 1})
        shutil.rmtree(OUT / "tampered_tools", ignore_errors=True)

    def test_signature_is_64_bytes_and_kid_16_hex(self):
        entry = scenarios.signed_pack()[0]
        self.assertEqual(len(entry["kid"]), 16)
        self.assertEqual(len(__import__("base64").b64decode(entry["sig"])), 64)

    def test_mcp_tools_list_matches_signed_manifests(self):
        OUT.mkdir(exist_ok=True)
        path = OUT / "toolpack.test.json"
        write(path, json.dumps(scenarios.signed_pack()))
        problems, text = mcp_pin(path, _lab.registry(), poison=False)
        self.assertEqual(problems, [])
        self.assertIn("vpn-setup.md", text)
        path.unlink()


if __name__ == "__main__":
    unittest.main()
