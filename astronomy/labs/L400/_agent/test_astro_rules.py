import unittest

import fake_model_server as fms
from client import chat


class AstroRulesTest(unittest.TestCase):
    def test_rules_are_registered_and_deterministic(self):
        markers = [m for m, _ in fms.EXTRA_RULES]
        self.assertIn("[[ASTRO-ALERT]]", markers)
        self.assertIn("[[ASTRO-CANDIDATE]]", markers)
        srv, url = fms.start_in_thread()
        try:
            text = chat([{"role": "user", "content": "[[ASTRO-ALERT]] <facts>\nclass: known_variable\nmagpsf: 17.2\n</facts>"}],
                        base_url=url, model="m")
        finally:
            srv.shutdown()
            srv.server_close()
        self.assertIn("a new transient", text)
        self.assertIn("2.5 magnitudes", text)


if __name__ == "__main__":
    unittest.main()
