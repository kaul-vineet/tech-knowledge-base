"""Project 05 Mac mini scripts, tested here: fake model, INDI dry run, LST reference route, tiny Monte Carlo."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import _lab  # noqa: E402
import agent_trials  # noqa: E402
import astropy_check  # noqa: E402
import indi_export  # noqa: E402
import sky  # noqa: E402
import stellarium_export  # noqa: E402
import weather  # noqa: E402
import weather_overnight  # noqa: E402


def night():
    return _lab.build()


class PrecessionTest(unittest.TestCase):
    def test_meeus_example_21b(self):
        # theta Persei, J2000 position after proper motion, precessed to 2028 Nov 13.19 TD (JD 2462088.69)
        ra, dec = indi_export.precess(41.054063, 49.227750, 2462088.69)
        self.assertAlmostEqual(ra, 41.547214, delta=2e-5)
        self.assertAlmostEqual(dec, 49.348483, delta=2e-5)

    def test_identity_at_j2000_and_size_of_the_gap(self):
        self.assertAlmostEqual(indi_export.precess(279.23474, 38.78369, 2451545.0)[0], 279.23474, places=9)
        jd = indi_export.jd_from_iso("2026-11-19T13:20:00Z")
        shifts = [indi_export.separation_deg(q.ra_deg, q.dec_deg, *indi_export.precess(q.ra_deg, q.dec_deg, jd))
                  for q in sky.REQUESTS]
        self.assertGreater(min(shifts), 0.05)  # Canopus moves least on the sky (0.092 deg)
        self.assertLess(max(shifts), 0.38)  # ~50.3"/yr x 26.9 yr at most


class IndiExportTest(unittest.TestCase):
    def setUp(self):
        r = night()
        self.rows, self.reqs = r["local_rows"], r["reqs"]
        self.cmds = indi_export.plan_commands(self.rows, self.reqs, indi_export.jd_from_iso)

    def test_only_standard_properties_and_atomic_coordinates(self):
        props = {argv[1].split("=")[0].split(".")[1] for _, argv in self.cmds if argv[0] == "indi_setprop"}
        self.assertEqual(props, indi_export.STANDARD)
        gotos = [argv[1] for _, argv in self.cmds if "EQUATORIAL_EOD_COORD.RA;DEC=" in argv[-1] and argv[0] == "indi_setprop"]
        self.assertEqual(len(gotos), len(self.rows))
        for g in gotos:
            ra_h, dec = map(float, g.split("=")[1].split(";"))
            self.assertTrue(0 <= ra_h < 24 and -90 <= dec <= 90)

    def test_j2000_sent_as_jnow_is_the_seam_bug(self):
        raw = indi_export.plan_commands(self.rows, self.reqs, indi_export.jd_from_iso, precess_coords=False)
        coords = lambda cmds: [tuple(map(float, a[1].split("=")[1].split(";"))) for _, a in cmds
                               if a[0] == "indi_setprop" and "EQUATORIAL_EOD_COORD" in a[1]]
        for (ra1, d1), (ra2, d2) in zip(coords(self.cmds), coords(raw)):
            self.assertGreater(indi_export.separation_deg(ra1 * 15, d1, ra2 * 15, d2), 0.1)

    def test_realtime_waits_and_fills_blocks(self):
        rt = indi_export.plan_commands(self.rows[:1], self.reqs, indi_export.jd_from_iso, sub_exp_s=300, realtime=True)
        self.assertEqual(rt[3][1], ["wait_until_utc", self.rows[0]["start_utc"]])
        exposures = sum(1 for _, a in rt if a[0] == "indi_setprop" and "CCD_EXPOSURE" in a[1])
        self.assertEqual(exposures, 60 * 60 // 300)  # Vega: a 60-minute block of 300 s exposures

    @unittest.skipIf(shutil.which("bash") is None, "bash missing")
    def test_script_is_valid_bash(self):
        tmp = Path(tempfile.mkdtemp(prefix="scratch-", dir=Path(__file__).parent))
        try:
            p = tmp / "night.sh"
            p.write_text(indi_export.script(self.cmds), encoding="utf-8")
            subprocess.run(["bash", "-n", str(p)], check=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @unittest.skipIf(shutil.which("indi_setprop") is not None, "INDI installed: would really execute")
    def test_execute_without_indi_skips(self):
        self.assertEqual(indi_export.main(["--execute"]), 2)


class CrossCheckTest(unittest.TestCase):
    def test_lst_reference_route(self):
        r = night()
        res = astropy_check.compare(r["local_rows"], r["reqs"], astropy_check.lst_route, "lst")
        self.assertLess(res["max_dalt_deg"], 0.02)
        self.assertEqual(res["ff1_violations_by_reference"], [])
        self.assertEqual(len(res["blocks"]), len(r["local_rows"]))

    def test_violation_is_reported(self):
        r = night()
        res = astropy_check.compare(r["local_rows"], r["reqs"], lambda q, ts: [20.0 for _ in ts], "low")
        self.assertEqual(res["ff1_violations_by_reference"], [x["target"] for x in r["local_rows"]])

    @unittest.skipIf(astropy_check.astropy_route() is not None, "astropy installed")
    def test_missing_astropy_skips_cleanly(self):
        self.assertEqual(astropy_check.main([]), 0)

    def test_stellarium_script_and_compare(self):
        r = night()
        text = stellarium_export.ssc(r["local_rows"])
        self.assertIn('core.setDate(plan[i][1], "utc");', text)
        self.assertIn("core.setObserverLocation(77.03, 28.46, 217, 0,", text)
        by = {q.name: q for q in r["reqs"]}
        lines = ["name,utc,altitude-geometric,altitude"]
        for row in r["local_rows"][:2]:
            for t in astropy_check.samples(row):
                alt = sky.alt_deg(by[row["target"]], t) + 0.25
                lines.append(f"{row['target']},{t.dt:%Y-%m-%dT%H:%M:%S},{alt},{alt + 0.03}")
        res = stellarium_export.compare("\n".join(lines + ["done"]), r["reqs"])
        self.assertAlmostEqual(res["max_abs_dalt_deg"], 0.25, places=3)
        self.assertAlmostEqual(res["max_refraction_deg"], 0.03, places=6)


class WeatherOvernightTest(unittest.TestCase):
    def test_chunks_equal_one_big_matrix(self):
        whole = weather.clear_matrix(300, 64, 7)
        self.assertTrue((weather_overnight.clear_rows(7, 0, 120, 64) == whole[:120]).all())
        self.assertTrue((weather_overnight.clear_rows(7, 120, 300, 64) == whole[120:]).all())

    def test_workers_do_not_change_results(self):
        plans = weather_overnight.plans_of(night())
        v1, d1 = weather_overnight.simulate(plans, 64, 600, 1, chunk=200)
        v2, d2 = weather_overnight.simulate(plans, 64, 600, 2, chunk=150)
        self.assertTrue(all((v1[k] == v2[k]).all() for k in plans))
        self.assertTrue(all((d1[k] == d2[k]).all() for k in plans))
        whole = weather.clear_matrix(600, 64, 7)
        self.assertTrue((v1["local"] == weather.realised(plans["local"], whole)).all())

    def test_summary_fields(self):
        plans = weather_overnight.plans_of(night())
        vals, done = weather_overnight.simulate(plans, 64, 400, 1, chunk=400)
        s = weather_overnight.summarise(plans, vals, done, 400, weather.P_CLEAR_TO_CLOUD)
        self.assertEqual(len(s["local"]["blocks"]), len(plans["local"]))
        self.assertIn("ff2_holds", s)


class AgentTrialsTest(unittest.TestCase):
    def test_fake_model_is_refused_and_explanation_checked(self):
        tmp = Path(tempfile.mkdtemp(prefix="scratch-", dir=Path(__file__).parent))
        try:
            self.assertEqual(agent_trials.main(["--here", "--out", str(tmp)]), 0)
            (row,) = [json.loads(x) for x in (tmp / "05-agent-trials.jsonl").read_text(encoding="utf-8").splitlines()]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(row["adopted"], "optimiser")
        self.assertEqual(row["violation_kinds"]["zone"], 1)  # the naive local wall-clock time is refused
        self.assertGreaterEqual(row["violation_kinds"]["airmass"], 1)
        self.assertTrue(row["explanation_published"])
        self.assertEqual(row["invented_numbers"], [])

    def test_classify(self):
        self.assertEqual(agent_trials.classify(["A and B overlap", "x: need ISO 8601 with 'Z'", "weird"]),
                         {"overlap": 1, "zone": 1, "other": 1})


if __name__ == "__main__":
    unittest.main()
