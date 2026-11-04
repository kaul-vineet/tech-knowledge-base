"""M3 (seam: idempotent retries vs duplicate ciphertexts): 400/201/200/422 like DS lesson 5; a crash after the
outbox write gives 503, the retry is re-sealed (2 ciphertexts in the log) but shown once."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestM3ApiOutbox(unittest.TestCase):
    def test_status_codes_and_outbox(self):
        r = sc.m3_api()
        self.assertEqual(r["status_codes"], {"no key": 400, "first": 201, "retry": 200, "same key, new text": 422})
        self.assertEqual((r["crash_after_outbox_write"], r["client_retry"]), (503, 201))
        self.assertEqual((r["sealed_ciphertexts_for_key"], r["messages_shown_for_key"]), (2, 1))

    def test_dedupe_must_be_replicated(self):
        self.assertFalse(sc.m3_api({"no-apply-dedupe"})["pass"])  # the same retry is shown twice without it


if __name__ == "__main__":
    unittest.main()
