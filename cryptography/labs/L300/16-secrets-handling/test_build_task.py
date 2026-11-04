"""Build task check (failureLab proof). Default: tests solution_redact.py.
Test YOUR version:  macOS  BUILD_IMPL=secrets_app python -m unittest -v test_build_task
                    Windows  $env:BUILD_IMPL="secrets_app"; python -m unittest -v test_build_task"""
import importlib
import io
import os
import random
import unittest

import secrets_app as app

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_redact"))


def make_logger(buf, known):
    try:
        return impl.json_logger(buf, name="t-" + str(id(buf)), known_secrets=known)
    except TypeError:  # the unfixed secrets_app.json_logger has no known_secrets parameter
        return impl.json_logger(buf, name="t-" + str(id(buf)))


class TestNoSecretsInLogs(unittest.TestCase):
    def test_seeded_request_mix_leaves_clean_logs(self):
        rng = random.Random(app.SEED)
        key = app.Secret("sk_test_" + "".join(rng.choice("abcdef0123456789") for _ in range(32)))
        buf = io.StringIO()
        log = make_logger(buf, [key.reveal()])
        for order in range(20):
            app.handle_request(log, key, order, debug=rng.random() < 0.5)
        self.assertIn('"msg": "upstream request"', buf.getvalue())  # the debug path really ran
        self.assertEqual(app.scan_log(buf.getvalue(), known=[key.reveal()]), [])

    def test_message_args_and_nested_fields(self):
        buf = io.StringIO()
        log = make_logger(buf, ["hunter2-very-secret"])
        log.warning("login failed for %s with %s", "alice", "hunter2-very-secret",
                    extra={"ctx": {"form": {"user": "alice", "password": "hunter2-very-secret"}}})
        self.assertEqual(app.scan_log(buf.getvalue(), known=["hunter2-very-secret"]), [])
        self.assertIn("alice", buf.getvalue())  # redaction keeps the useful parts


if __name__ == "__main__":
    unittest.main()
