import io
import random
import threading
import unittest
from contextlib import redirect_stdout
from http.server import ThreadingHTTPServer

import idempotency as idem

KEY = "8e03978e-40d5-43e8-bc93-6894a57f9324"


class TestIdempotency(unittest.TestCase):
    def setUp(self):
        idem.PaymentB.enforce, idem.PaymentB.rng = True, random.Random(3)
        idem.PaymentB.ledger.clear(); idem.PaymentB.store.clear()
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), idem.PaymentB)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_port}/charges"

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close()

    def test_without_keys_retries_duplicate_charges(self):
        with redirect_stdout(io.StringIO()):
            idem.run(enforce=False)
        self.assertGreater(len(idem.PaymentB.ledger), 5)

    def test_with_keys_exactly_once_effect(self):
        with redirect_stdout(io.StringIO()):
            idem.run(enforce=True)
        self.assertEqual(idem.PaymentB.ledger, [10] * 5)

    def test_retry_replays_same_response(self):
        first = second = None
        for _ in range(10):  # keep sending until we get answers (some responses are "lost")
            status, body, _ = idem.pay(self.url, 10, KEY)
            first = first or (status, body)
            second = (status, body)
        self.assertEqual(first, second)
        self.assertEqual(len(idem.PaymentB.ledger), 1)

    def test_error_cases(self):
        idem.pay(self.url, 10, KEY)
        self.assertEqual(idem.pay(self.url, 99, KEY)[0], 422)   # same key, different payload
        self.assertEqual(idem.pay(self.url, 10)[0], 400)        # key missing
        idem.PaymentB.store["11111111-1111-4111-8111-111111111111"] = {
            "fp": __import__("hashlib").sha256(b'{"amount": 10}').hexdigest(), "state": "in-progress"}
        self.assertEqual(idem.pay(self.url, 10, "11111111-1111-4111-8111-111111111111")[0], 409)


if __name__ == "__main__":
    unittest.main()
