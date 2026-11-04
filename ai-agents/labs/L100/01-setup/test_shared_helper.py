"""Consistency check: other topics reuse kb/shared/local_agent/, which is this folder's fake server.

Run: python -m unittest -v test_shared_helper
The shared-folder tests skip when this topic is checked out on its own (no kb/shared next to it).
"""
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fake_model_server as fms  # noqa: E402

SHARED = HERE.parents[3] / "shared" / "local_agent"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtraRulesHook(unittest.TestCase):
    def test_hook_runs_before_echo(self):
        # topic hook: a marker string routes to a deterministic reply; everything else is unchanged
        fms.EXTRA_RULES.append(("[[PING]]", lambda text: "PONG"))
        try:
            self.assertEqual(fms._reply({"messages": [{"role": "user", "content": "[[PING]] hi"}]}),
                             ({"role": "assistant", "content": "PONG"}, "stop"))
            self.assertIn("Hello from fake-model", fms._reply({"messages": [{"role": "user", "content": "x"}]})[0]["content"])
        finally:
            fms.EXTRA_RULES.clear()


@unittest.skipUnless(SHARED.is_dir(), "kb/shared/local_agent not present next to this topic")
class SharedHelperConsistency(unittest.TestCase):
    def test_same_fake_server_source(self):
        mine = (HERE / "fake_model_server.py").read_text(encoding="utf-8").replace("\r\n", "\n")
        shared = (SHARED / "fake_model_server.py").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.assertEqual(mine, shared, "labs/L100/01-setup/fake_model_server.py and kb/shared/local_agent/ differ")

    def test_shared_client_talks_to_this_server(self):
        client = _load("shared_client", SHARED / "client.py")
        self.assertEqual(client.DEFAULT_URL, "http://localhost:11434/v1")  # same defaults as LOCAL_MODEL_URL/LOCAL_MODEL here
        self.assertEqual(client.DEFAULT_MODEL, "qwen2.5:1.5b")
        server, url = fms.start_in_thread()
        try:
            reply = client.chat([{"role": "user", "content": "Reply with the single word: ready"}], base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(reply, "Hello from fake-model! You said: 'Reply with the single word: ready'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
