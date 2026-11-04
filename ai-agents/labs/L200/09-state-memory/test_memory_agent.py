import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import memory_agent as ma  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

DB = os.path.join(HERE, "_test_memory.db")  # inside the lab folder; removed after each test


class MemoryAgentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def tearDown(self):
        if os.path.exists(DB):
            os.remove(DB)

    def test_store_uses_placeholders(self):
        store = ma.MemoryStore()
        store.save("deploys happen on Tuesday")
        self.assertEqual(store.recall("tuesday"), "1: deploys happen on Tuesday")
        self.assertEqual(store.recall("x' OR '1'='1"), "no matching notes")  # injection text is just data
        store.close()

    def test_memory_survives_a_new_conversation(self):
        first = ma.Chat(ma.MemoryStore(DB), base_url=self.url, model="m")
        self.assertIn("saved note 1", first.send("Remember that the staging database is on port 5433."))
        first.memory.close()
        second = ma.Chat(ma.MemoryStore(DB), base_url=self.url, model="m")
        self.assertEqual(len(second.messages), 1)  # empty conversation state...
        self.assertIn("1: the staging database is on port 5433", second.send("What do you remember about staging?"))
        second.memory.close()  # ...but the SQLite file remembered

    def test_summarise_to_fit_budget(self):
        chat = ma.Chat(ma.MemoryStore(), budget=40, keep_last=2, base_url=self.url, model="m")
        for text in ["first question about otters and rivers", "second question about penguins and ice",
                     "third question about owls"]:
            chat.send(text)
        self.assertEqual(chat.summaries, 1)
        self.assertIn("Earlier: Summary: first question about otters and rivers", chat.messages[0]["content"])
        self.assertEqual(chat.messages[-2]["content"], "third question about owls")  # recent turns kept verbatim
        chat.memory.close()

    def test_count_matches_server_usage(self):
        import requests
        msgs = [{"role": "user", "content": "one two three four"}]
        usage = requests.post(f"{self.url}/chat/completions", json={"model": "m", "messages": msgs}, timeout=5).json()["usage"]
        self.assertEqual(ma.count_tokens(msgs), usage["prompt_tokens"])  # true for the fake (words), not for real models

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "memory_agent.py"], cwd=HERE, env=env, capture_output=True,
                             encoding="utf-8", check=True).stdout
        self.assertIn("summaries=1", out)
        self.assertIn("recall_memory(query=staging) = 1: the staging database is on port 5433", out)
        os.remove(os.path.join(HERE, "memory_demo.db"))


if __name__ == "__main__":
    unittest.main()
