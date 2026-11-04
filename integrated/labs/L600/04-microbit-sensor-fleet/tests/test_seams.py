"""Seam tests: one class per contract that crosses a topic boundary (S1-S5 in the lesson)."""
import random
import unittest

from tests._shared import LAB, run
import _kb  # noqa: E402
import api  # noqa: E402
import fleet_sim  # noqa: E402
import gateway  # noqa: E402
from store import ReadingStore  # noqa: E402

radio = _kb.radio()


def board(schema=2):
    """One stub board running the firmware (schema 1 via the same patch the fleet uses)."""
    src = fleet_sim.firmware_sources()["d17" if schema == 1 else "d01"]
    b = _kb.labtest().load_boards(str(fleet_sim.FIRMWARE), ["x"], sources={"x": src})[0]
    b.mb._inject_temperature(-5)
    b.mb.display.inject_light_level(200)
    return b, b.lab.new_state(3, {"epoch_s": fleet_sim.EPOCH0})


class S1RadioLengthVsDeltaSize(unittest.TestCase):
    def test_every_frame_fits_the_configured_length(self):
        for schema in (1, 2):
            b, st = board(schema)
            for _ in range(40):
                b.lab.sample(st)
            out = b.lab.frames(st)
            self.assertEqual(len(out), b.lab.MAX_FRAMES)
            self.assertLessEqual(max(map(len, out)), b.lab.RADIO_LENGTH)
            self.assertEqual(b.lab.RECORDS_PER_FRAME, (32 - 3) // b.lab.REC_LEN[2])

    def test_one_big_frame_is_truncated_by_the_radio_and_rejected(self):
        b, st = board()
        for _ in range(10):
            b.lab.sample(st)
        big = bytes([2, ord("D"), 3]) + b"".join(b.lab.pack(r) for r in st["flash"]["log"])   # 93 B
        air = radio.Air()
        tx, rx = radio.Endpoint(air, "tx"), radio.Endpoint(air, "rx")
        rx.config(length=251)
        tx.send_bytes(big)                                # sender truncates to its length (32)
        got = rx.receive_bytes()
        self.assertEqual((len(big), len(got)), (93, 32))
        with self.assertRaises(ValueError):
            gateway.decode_frame(got)

    def test_full_state_does_not_fit_but_the_delta_does(self):
        full = 720 * 9                                    # one device, 12 h, schema 2
        self.assertEqual(-(-full // 29), 224)             # frames of 29 B payload
        self.assertLessEqual(run()["max_frame_bytes"], 32)


class S2ClockVsIdentity(unittest.TestCase):
    def test_wall_clock_repeats_but_dots_do_not(self):
        r = run()
        self.assertGreater(r["wall_key_repeats"], 0)
        self.assertEqual(len(r["truth"]), r["sampled"])   # dict keyed by dot: no dot collides
        self.assertEqual(r["lost"], 0)

    def test_per_device_order_is_boot_then_seq(self):
        rows = run()["stores"]["b1"].rows(7)
        dots = [d for d, _ in rows]
        self.assertEqual(dots, sorted(dots))
        walls = [v[0] for _, v in rows]
        self.assertNotEqual(walls, sorted(walls))          # wall time goes backwards after the reboot


class S3BatteryVsSync(unittest.TestCase):
    def test_model_matches_the_microbit_budget_without_sync(self):
        budget = _kb.budget()
        fig, total = budget.FIGURES, 3600 * 1000
        ours = fleet_sim.life_hours(60 * fig["ACTIVE_MS"], total, fig)[0]
        theirs = budget.life_h({"wakeups": 60, "total_ms": total}, fig, fig["SLEEP_MA"])[2]
        self.assertEqual(ours, theirs)

    def test_more_frequent_sync_costs_battery(self):
        fig = _kb.budget().FIGURES
        lives = [fleet_sim.life_hours(1200 + syncs * 70, 3600 * 1000, fig)[0] for syncs in (6, 60, 360)]
        self.assertEqual(lives, sorted(lives, reverse=True))
        self.assertEqual(run()["boards"][0].lab.ACTIVE_MS, fig["ACTIVE_MS"])


class S4SchemaVsContract(unittest.TestCase):
    def test_layout_tables_agree(self):
        b, _ = board()
        self.assertEqual(b.lab.REC_LEN, gateway.REC_LEN)

    def test_schema1_frame_decodes_with_light_none(self):
        b, st = board(schema=1)
        b.lab.sample(st)
        schema, dev, recs = gateway.decode_frame(b.lab.frames(st)[0])
        self.assertEqual((schema, dev, recs[0][3], recs[0][4]), (1, 3, -5, None))

    def test_ignoring_the_schema_byte_rejects_schema1_frames(self):
        b, st = board(schema=1)
        for _ in range(3):
            b.lab.sample(st)
        with self.assertRaises(ValueError):
            gateway.decode_frame(b.lab.frames(st)[0], trust_schema_byte=False)


class S5CrdtVsApiPaging(unittest.TestCase):
    def test_paging_never_skips_a_late_reading(self):
        rng, final = random.Random(4), list(range(1, 201))
        order = final[:]
        rng.shuffle(order)                               # gossip delivers seqs in any order
        s, seen, after = ReadingStore(), [], 0
        for seq in order:
            s.add((1, 1, seq), (fleet_sim.EPOCH0 + seq, 20, 100, 2))
            page, _ = api.readings(s, "d01", 1, after, limit=10)     # a client polling while gossip runs
            seen += [i["seq"] for i in page["items"]]
            after = page["next"] or after
        while True:                                                 # then pages to the end
            page, _ = api.readings(s, "d01", 1, after, limit=10)
            if page["next"] is None:
                break
            seen += [i["seq"] for i in page["items"]]
            after = page["next"]
        self.assertEqual(seen, final)

    def test_serving_the_cloud_would_skip(self):
        s = ReadingStore()
        for seq in (1, 2, 4):                                       # 3 is still on its way
            s.add((1, 1, seq), (fleet_sim.EPOCH0 + seq, 20, 100, 2))
        page, _ = api.readings(s, "d01", 1, 0)
        self.assertEqual(([i["seq"] for i in page["items"]], page["stableThrough"]), ([1, 2], 2))


if __name__ == "__main__":
    unittest.main()
