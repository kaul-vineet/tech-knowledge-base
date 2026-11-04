import json
import unittest

from cryptography.exceptions import InvalidTag

import envelope as env


class TestEnvelope(unittest.TestCase):
    def setUp(self):
        self.ring = env.Keyring()
        self.rec = env.seal(self.ring, b"card=4111", "order-1")

    def test_roundtrip_and_header(self):
        self.assertEqual(env.open_(self.ring, self.rec), b"card=4111")
        self.assertEqual(self.rec["kid"], "orders-kek:v1")

    def test_rotation_keeps_old_records_readable(self):
        self.assertEqual(self.ring.rotate(), "orders-kek:v2")
        self.assertEqual(env.open_(self.ring, self.rec), b"card=4111")
        self.assertEqual(env.seal(self.ring, b"new", "o2")["kid"], "orders-kek:v2")

    def test_rewrap_changes_only_the_wrapped_dek(self):
        self.ring.rotate()
        new = env.rewrap(self.ring, self.rec)
        self.assertEqual((new["ct"], new["n"]), (self.rec["ct"], self.rec["n"]))
        self.assertNotEqual(new["wdek"], self.rec["wdek"])
        self.assertEqual(env.open_(self.ring, new), b"card=4111")

    def test_header_and_context_are_authenticated(self):
        self.ring.rotate()
        with self.assertRaises(InvalidTag):  # relabel v1 -> v2: kid is the wrap AAD
            env.open_(self.ring, {**self.rec, "kid": "orders-kek:v2"})
        with self.assertRaises(InvalidTag):  # move the record to another row: ctx is the data AAD
            env.open_(self.ring, {**self.rec, "ctx": "order-2"})

    def test_job_logs_json_lines_and_metric(self):
        lines = []
        store = {"a": self.rec, "b": env.seal(self.ring, b"x", "b")}
        self.ring.rotate()
        self.assertEqual(env.rewrap_job(self.ring, store, log=lines.append), 2)
        events = [json.loads(line) for line in lines]
        self.assertEqual(events[-1], {"metric": "records_by_kid", "orders-kek:v2": 2})
        self.assertEqual(env.rewrap_job(self.ring, store, log=lines.append), 0)  # idempotent rerun

    def test_fault_naive_retire_loses_data(self):
        store = {f"r{i}": env.seal(self.ring, b"x", f"r{i}") for i in range(4)}
        self.ring.rotate()
        with self.assertRaises(RuntimeError):
            env.rewrap_job(self.ring, store, log=lambda line: None, crash_after=1)
        env.retire(self.ring, store, 1)  # the bug: nothing stops this
        self.assertTrue(env.try_all(self.ring, store).startswith("1/4 decrypt; LOST"))


if __name__ == "__main__":
    unittest.main()
