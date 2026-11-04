import unittest
import fake_model_server as fms
from client import chat


class SharedTest(unittest.TestCase):
    def test_extra_rule_and_echo(self):
        fms.EXTRA_RULES.append(("[[PING]]", lambda t: "PONG"))
        srv, url = fms.start_in_thread()
        try:
            self.assertEqual(chat([{"role": "user", "content": "[[PING]] hi"}], base_url=url, model="m"), "PONG")
            self.assertIn("Hello from", chat([{"role": "user", "content": "x"}], base_url=url, model="m"))
        finally:
            srv.shutdown()
            fms.EXTRA_RULES.clear()


if __name__ == "__main__":
    unittest.main()
