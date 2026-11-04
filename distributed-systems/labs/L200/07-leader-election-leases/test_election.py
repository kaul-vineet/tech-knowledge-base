import unittest

import election as el
from helpers import SimClock, call, serve
from kv_store import KVStore


class TestLeaseStore(unittest.TestCase):
    def setUp(self):
        self.clock = SimClock()
        KVStore.reset(self.clock)
        self.srv = serve(KVStore)
        self.url = f"http://127.0.0.1:{self.srv.server_port}"

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def test_cas_lets_exactly_one_node_create_the_lease(self):
        a = call(self.url + "/cas", {"key": "k", "expect": 0, "value": "a", "ttl": 3})
        b = call(self.url + "/cas", {"key": "k", "expect": 0, "value": "b", "ttl": 3})
        self.assertEqual((a[0], b[0]), (200, 409))
        self.assertEqual(call(self.url + "/get", {"key": "k"})[1]["value"], "a")

    def test_ttl_expiry_frees_the_key_and_revisions_only_grow(self):
        first = call(self.url + "/cas", {"key": "k", "expect": 0, "value": "a", "ttl": 3})[1]
        self.clock.advance(3.0)  # expires at exactly t = 3
        self.assertEqual(call(self.url + "/get", {"key": "k"})[0], 404)
        second = call(self.url + "/cas", {"key": "k", "expect": 0, "value": "b", "ttl": 3})[1]
        self.assertGreater(second["created"], first["created"])  # new holder -> higher fencing token


class TestElection(unittest.TestCase):
    def test_failover_after_pause_and_stale_write_is_fenced(self):
        out = el.simulate(events={3: ("n1", "pause"), 7: ("n1", "resume")}, quiet=True)
        holders = [h for _, h, _ in out["holders"]]
        self.assertEqual(holders, ["n1"] * 5 + ["n2"] * 4)  # last renewal t=2 + TTL 3 s -> takeover at t=5
        self.assertIn("t=7 n1 writes with token 1: REJECTED (token 1 < 4)", out["log"])
        self.assertEqual(out["storage"].value, "n2@t8")

    def test_never_two_lease_holders_in_the_store(self):
        out = el.simulate(ticks=12, events={2: ("n1", "pause"), 9: ("n2", "pause")}, quiet=True)
        tokens = [tok for _, h, tok in out["holders"] if h]
        self.assertEqual(tokens, sorted(tokens))  # fencing tokens never go backwards


if __name__ == "__main__":
    unittest.main()
