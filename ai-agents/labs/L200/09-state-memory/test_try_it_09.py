"""Try it (lesson 9): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_09"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import memory_agent as ma  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TURNS = ["Remember that the staging database is on port 5433.", "Thanks. Now tell me a fun fact about otters.",
         "And one about penguins please, keep it short."]


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_bigger_budget(self):
        chat = ma.Chat(ma.MemoryStore(), budget=500, base_url=self.url, model="m")  # was 60
        for t in TURNS:
            chat.send(t)
        print("\nobserved: summaries =", chat.summaries, "| messages =", len(chat.messages),
              "| tokens =", ma.count_tokens(chat.messages))
        self.assertEqual((chat.summaries, len(chat.messages)), (0, 9))

    def test_2_new_database_file(self):
        chat = ma.Chat(ma.MemoryStore(), base_url=self.url, model="m")  # ":memory:" instead of memory_demo.db
        chat.send(TURNS[0])
        fresh = ma.Chat(ma.MemoryStore(), base_url=self.url, model="m")
        answer = fresh.send("What do you remember about staging?")
        print("\nobserved:", answer)
        self.assertEqual(answer, "Final answer: recall_memory(query=staging) = no matching notes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
