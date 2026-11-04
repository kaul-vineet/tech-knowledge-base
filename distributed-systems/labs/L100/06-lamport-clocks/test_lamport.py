import unittest

import lamport


class TestLamport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lamport.EVENTS.clear()
        lamport.TRUE_TIME[0] = 0.0
        cls.events = lamport.scenario()

    def test_send_has_smaller_timestamp_than_receive(self):
        sends = {e[4]: e[0] for e in self.events if e[4] and e[3].startswith("send")}
        recvs = {e[4]: e[0] for e in self.events if e[4] and e[3].startswith("recv")}
        self.assertEqual(sends.keys(), recvs.keys())
        for m in sends:
            self.assertLess(sends[m], recvs[m])

    def test_wall_clock_order_breaks_causality_lamport_does_not(self):
        by_wall = sorted(self.events, key=lambda e: e[2])
        by_lamport = sorted(self.events, key=lambda e: (e[0], e[1]))
        self.assertGreaterEqual(lamport.violations(by_wall), 1)
        self.assertEqual(lamport.violations(by_lamport), 0)

    def test_lamport_plus_node_id_is_a_total_order(self):
        keys = [(e[0], e[1]) for e in self.events]
        self.assertEqual(len(keys), len(set(keys)))

    def test_local_events_tick_monotonically_per_node(self):
        for node in "ABC":
            stamps = [e[0] for e in self.events if e[1] == node]
            self.assertEqual(stamps, sorted(stamps))
            self.assertEqual(len(stamps), len(set(stamps)))


if __name__ == "__main__":
    unittest.main()
