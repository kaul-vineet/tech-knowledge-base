"""Tests for the shared Mac mini track scripts. They run anywhere (the sandbox is Linux): RAM is simulated, the nightly
run uses two tiny fake labs, the launchd plist is rendered (not installed). Scratch folders live next to this file."""
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import mac_profile  # noqa: E402

FAKE_LAB = '''import sys
print('{"check": "x", "pass": true}')
fail = "--inject" in sys.argv
print('{"scorecard": "%s"}' % ("FAIL" if fail else "PASS"))
sys.exit(1 if fail else 0)
'''
BROKEN_LAB = 'print(\'{"scorecard": "PASS"}\')\n'  # ignores --inject: the failure lab does NOT fail -> must be flagged


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="scratch-", dir=HERE))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class MacProfileTest(unittest.TestCase):
    def test_kv_cache_formula(self):
        # 2 x 48 layers x 8 KV heads x 128 x 2 bytes x 4096 tokens = 0.805 GB for qwen2.5:14b
        self.assertAlmostEqual(mac_profile.kv_gb("qwen2.5:14b", 4096, 1), 2 * 48 * 8 * 128 * 2 * 4096 / 1e9)
        self.assertAlmostEqual(mac_profile.kv_gb("qwen2.5:14b", 4096, 4), 4 * mac_profile.kv_gb("qwen2.5:14b", 4096, 1))

    def test_by_ram_recommendations(self):
        got = {g: mac_profile.recommend(mac_profile.ram_from_gib(g)) for g in (16, 24, 32, 64)}
        self.assertEqual(got[16]["statevector"]["complex128"]["max_qubits"], 28)
        self.assertEqual(got[64]["statevector"]["complex64"]["max_qubits"],
                         got[64]["statevector"]["complex128"]["max_qubits"] + 1)
        self.assertNotIn("qwen2.5:32b", got[24]["compare_models"])
        self.assertEqual(got[32]["largest_model"], "qwen2.5:32b")
        sizes = [len([m for m in got[g]["models"] if m["fits"]]) for g in (16, 24, 32, 64)]
        self.assertEqual(sizes, sorted(sizes))  # more RAM never fits fewer models

    def test_qubit_limit_is_tight(self):
        r = mac_profile.recommend(mac_profile.ram_from_gib(16))
        q = r["statevector"]["complex128"]
        self.assertLessEqual(q["with_copies_gb"], r["budget_gb"])
        self.assertGreater(q["next_qubit_gb"], r["budget_gb"])

    def test_cli_json_and_table(self):
        out = subprocess.run([sys.executable, str(SCRIPTS / "mac_profile.py"), "--ram", "24", "--json"],
                             capture_output=True, text=True, check=True).stdout
        p = json.loads(out)
        self.assertEqual(p["simulated_ram_gib"], 24.0)
        self.assertGreaterEqual(p["workers"], 1)
        md = subprocess.run([sys.executable, str(SCRIPTS / "mac_profile.py"), "--table", "16", "24", "32", "64",
                             "--markdown"], capture_output=True, text=True, check=True).stdout.strip().splitlines()
        self.assertEqual(len(md), 6)
        self.assertTrue(md[2].startswith("| 16 GB |"))


@unittest.skipIf(shutil.which("bash") is None, "bash not available")
class NightlyTest(Scratch):
    def _labs(self, broken=False):
        for name, src in (("aa-good", FAKE_LAB), ("bb-lab", BROKEN_LAB if broken else FAKE_LAB)):
            (self.tmp / "labs" / name).mkdir(parents=True)
            (self.tmp / "labs" / name / "run_project.py").write_text(src, encoding="utf-8")
        return {**os.environ, "KB_LAB_ROOT": str(self.tmp / "labs"), "KB_RUNS_DIR": str(self.tmp / "runs"),
                "PYTHON": sys.executable, "KB_LABS": "aa-good:fault:91 bb-lab:fault:92"}

    def _run(self, env, *args):
        return subprocess.run(["bash", str(SCRIPTS / "nightly.sh"), *args], env=env, capture_output=True, text=True)

    def _records(self):
        files = list((self.tmp / "runs").glob("*.jsonl"))
        self.assertEqual(len(files), 1)
        return [json.loads(x) for x in files[0].read_text(encoding="utf-8").splitlines()]

    def test_runs_scorecard_and_failure_lab(self):
        res = self._run(self._labs())
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        recs = self._records()
        self.assertEqual([(r["lab"], r["step"], r["exit"]) for r in recs],
                         [("aa-good", "scorecard", 0), ("aa-good", "failure-lab", 1),
                          ("bb-lab", "scorecard", 0), ("bb-lab", "failure-lab", 1)])
        self.assertTrue(all(r["ok"] for r in recs))
        self.assertEqual(recs[1]["last_json"], {"scorecard": "FAIL"})

    def test_failure_lab_that_passes_is_flagged(self):
        res = self._run(self._labs(broken=True))
        self.assertEqual(res.returncode, 1)
        bad = [r for r in self._records() if not r["ok"]]
        self.assertEqual([(r["lab"], r["step"]) for r in bad], [("bb-lab", "failure-lab")])

    def test_only_and_retention(self):
        env = {**self._labs(), "KB_KEEP_DAYS": "30"}
        (self.tmp / "runs").mkdir()
        old = self.tmp / "runs" / "2000-01-01.jsonl"
        old.write_text("{}\n", encoding="utf-8")
        week = self.tmp / "runs" / "recent.jsonl"
        week.write_text("{}\n", encoding="utf-8")
        os.utime(old, (time.time() - 31 * 86400,) * 2)
        os.utime(week, (time.time() - 7 * 86400,) * 2)
        res = self._run(env, "--only", "92")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse(old.exists())
        self.assertTrue(week.exists())
        today = [p for p in (self.tmp / "runs").glob("*.jsonl") if p not in (week,)]
        recs = [json.loads(x) for x in today[0].read_text(encoding="utf-8").splitlines()]
        self.assertEqual({r["lab"] for r in recs}, {"bb-lab"})

    def test_here_mode_plans_without_running(self):
        res = self._run(self._labs(broken=True), "--here")
        self.assertEqual(res.returncode, 0)
        self.assertIn("[plan]", res.stdout)
        self.assertTrue(all(r["expect"] == "planned" and r["ok"] is None for r in self._records()))


@unittest.skipIf(shutil.which("bash") is None or shutil.which("sed") is None, "bash/sed not available")
class LaunchdTemplateTest(Scratch):
    def test_rendered_plist_is_valid(self):
        out = self.tmp / "local.kb.nightly.plist"
        subprocess.run(["bash", str(SCRIPTS / "install_nightly.sh"), "--here", str(out)], check=True,
                       capture_output=True, text=True)
        with out.open("rb") as fh:
            p = plistlib.load(fh)
        self.assertEqual(p["Label"], "local.kb.nightly")
        self.assertEqual(p["StartCalendarInterval"], {"Hour": 2, "Minute": 30})
        self.assertTrue(p["ProgramArguments"][3].endswith("integrated/mac-mini/scripts/nightly.sh"))
        self.assertNotIn("__", out.read_text(encoding="utf-8"))
        self.assertTrue(Path(p["ProgramArguments"][3]).is_file())


if __name__ == "__main__":
    unittest.main()
