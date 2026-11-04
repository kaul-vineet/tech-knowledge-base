"""The promptfoo red-team config stays local-first: every model is Ollama, no remote-only plugin or strategy,
and the privacy switches are documented. (Text checks only - promptfoo itself is a manual run.)"""
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMOTE_ONLY = ["harmful:", "bias", "ssrf", "bola", "bfla", "indirect-prompt-injection", "ascii-smuggling", "competitors",
               "hijacking", "off-topic", "system-prompt-override", "jailbreak:composite", "jailbreak:meta", "goat", "gcg"]


class LocalFirstConfig(unittest.TestCase):
    def setUp(self):
        self.text = (HERE / "promptfoo-redteam-local.yaml").read_text(encoding="utf-8")
        self.body = "\n".join(line for line in self.text.splitlines() if not line.lstrip().startswith("#"))

    def test_all_models_are_local(self):
        models = re.findall(r"(?:- id|provider):\s*(\S+:\S+)", self.body)  # target + attacker/grader (plugin ids have no ':')
        self.assertEqual(models, ["ollama:chat:qwen2.5:1.5b"] * 2)

    def test_no_remote_only_plugins_or_strategies(self):
        for name in REMOTE_ONLY:
            self.assertNotIn(name, self.body)

    def test_privacy_switches_documented(self):
        for var in ("PROMPTFOO_DISABLE_TELEMETRY=1", "PROMPTFOO_DISABLE_REMOTE_GENERATION=true", "PROMPTFOO_DISABLE_UPDATE=1"):
            self.assertIn(var, self.text)


if __name__ == "__main__":
    unittest.main()
