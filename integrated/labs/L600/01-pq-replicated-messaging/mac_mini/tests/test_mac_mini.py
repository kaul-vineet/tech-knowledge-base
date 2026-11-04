"""Tests for the Mac mini scripts of project 01, at sandbox size (run: python -m unittest discover -s mac_mini/tests).
They check behaviour (pass/fail of the fitness functions, the shape of the budget line), never timings."""
import contextlib
import io
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import _mac  # noqa: E402
import bench_crypto  # noqa: E402
import multiproc  # noqa: E402
import replica  # noqa: E402

RUNS = MAC / "runs"


def lines(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = fn(*args)
    return code, [json.loads(x) for x in buf.getvalue().splitlines() if x.startswith("{")]


class BenchHere(unittest.TestCase):
    def test_here_mode_prints_ops_and_budget(self):
        code, rows = lines(bench_crypto.main, ["--here"])
        self.assertEqual(code, 0)
        ops = {r["op"] for r in rows if "op" in r}
        self.assertIn("ml-kem-768 encapsulate", ops)
        self.assertIn("project welcome (hybrid KEM + HKDF + AES-GCM wrap)", ops)
        budget = rows[-1]
        self.assertEqual(budget["budget"], "rotation + per-key")
        self.assertGreater(budget["max_members_in_rotate_budget"], 0)
        self.assertEqual(rows[0]["mode"], "here")


class LogReplay(unittest.TestCase):
    def setUp(self):
        self.dir = RUNS / "test-logreplay"
        shutil.rmtree(self.dir, ignore_errors=True)
        (self.dir / "r1").mkdir(parents=True)
        (self.dir / "epoch1.key").write_text(os.urandom(32).hex())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_truncate_marker_and_repeated_append_survive_restart(self):
        r = replica.Replica("r1", self.dir / "r1", "random", fsync=False)
        e = [{"i": i, "t": 1, "ikey": f"k{i}", "env": {}} for i in (1, 2, 3)]
        self.assertTrue(r.handle({"op": "append", "term": 1, "prev": 0, "entries": e})["ok"])
        self.assertTrue(r.handle({"op": "append", "term": 1, "prev": 0, "entries": e[:2]})["ok"])  # repeat: no-op
        new3 = {"i": 3, "t": 2, "ikey": "k3b", "env": {}}
        self.assertTrue(r.handle({"op": "append", "term": 2, "prev": 2, "entries": [new3]})["ok"])  # repair suffix
        again = replica.Replica("r1", self.dir / "r1", "random", fsync=False)  # "restart": replay from disk
        self.assertEqual([x["ikey"] for x in again.log], ["k1", "k2", "k3b"])
        self.assertEqual(again.term, 2)
        self.assertFalse(again.handle({"op": "promote", "term": 2, "peers": []})["ok"])  # terms never go back


    def test_torn_last_line_from_a_kill_is_dropped_and_terminated(self):
        (self.dir / "r1" / "log.jsonl").write_text('{"i": 1, "t": 1, "ikey": "k1", "env": {}}\n{"i": 2, "t"')
        r = replica.Replica("r1", self.dir / "r1", "random", fsync=False)
        self.assertEqual([x["ikey"] for x in r.log], ["k1"])
        r.append([{"i": 2, "t": 1, "ikey": "k2", "env": {}}])
        self.assertEqual([x["ikey"] for x in replica.read_log(self.dir / "r1")], ["k1", "k2"])


class MultiProcess(unittest.TestCase):
    """Three real processes, 60 messages, 2 leader kills (one may be mid-request)."""

    def go(self, nonce):
        d = RUNS / f"test-{nonce}"
        shutil.rmtree(d, ignore_errors=True)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                head, f1, f2 = multiproc.run(60, 2, nonce, seed=3, run_dir=d, fsync=False)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(head["failovers"], 2)
        self.assertEqual(head["acked"], 60)
        self.assertTrue(f2["pass"], f2)
        return f1

    def test_random_nonces_survive_process_failover(self):
        self.assertTrue(self.go("random")["pass"])

    def test_leader_counter_reuses_nonces_across_processes(self):
        f1 = self.go("leader-counter")
        self.assertFalse(f1["pass"])
        self.assertGreater(f1["reused_nonces"], 0)

    def test_term_counter_solution_survives_process_failover(self):
        self.assertTrue(self.go("derived")["pass"])


class Profile(unittest.TestCase):
    def test_track_profile_is_loaded_not_copied(self):
        p = _mac.profile(16)
        self.assertEqual(p["simulated_ram_gib"], 16)
        self.assertIn("statevector", p)


if __name__ == "__main__":
    unittest.main()
