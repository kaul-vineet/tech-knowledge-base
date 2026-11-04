"""Project 08 Mac mini additions, tested here: loopback-only model URLs, the --real-model hook (pointed at the fake
model on loopback, so the scorecard must be identical), and the injection evaluation with the fake model."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
LAB = MAC.parent
sys.path.insert(0, str(MAC))
import _lab  # noqa: E402,F401
import adapters  # noqa: E402
import injection_eval  # noqa: E402
from model_endpoint import RemoteModelRefused, check_model_url, is_loopback  # noqa: E402


class LoopbackTest(unittest.TestCase):
    def test_loopback_urls_pass(self):
        for url in ("http://localhost:11434/v1", "http://127.0.0.1:11434/v1", "http://127.8.9.10:1/v1",
                    "http://[::1]:11434/v1", "https://localhost/v1"):
            self.assertTrue(is_loopback(url), url)
            self.assertEqual(check_model_url(url), url)

    def test_non_loopback_refused_unless_flag(self):
        for url in ("http://192.168.1.20:11434/v1", "http://10.0.0.5/v1", "http://0.0.0.0:11434/v1",
                    "http://mac-mini.local:11434/v1", "http://localhost.evil.test/v1", "https://api.example.com/v1"):
            with self.assertRaises(RemoteModelRefused, msg=url):
                check_model_url(url)
            self.assertEqual(check_model_url(url, allow_remote=True), url)

    def test_bad_schemes_refused_even_with_flag(self):
        for url in ("file:///etc/passwd", "ftp://127.0.0.1/", "127.0.0.1:11434"):
            with self.assertRaises(RemoteModelRefused):
                check_model_url(url, allow_remote=True)

    def test_http_model_enforces_it(self):
        with self.assertRaises(RemoteModelRefused):
            adapters.HttpModel("http://192.168.1.20:11434/v1")
        self.assertEqual(adapters.HttpModel("http://192.168.1.20:11434/v1", allow_remote=True).model, "fake-model")
        old = adapters.ALLOW_REMOTE
        try:
            adapters.ALLOW_REMOTE = True
            adapters.HttpModel("http://192.168.1.20:11434/v1")
        finally:
            adapters.ALLOW_REMOTE = old
        m = adapters.HttpModel("http://127.0.0.1:1/v1")
        self.assertEqual((m.model, m.timeout), ("fake-model", 30))  # the default path is unchanged


class RunProjectHookTest(unittest.TestCase):
    def _run(self, env, *args):
        return subprocess.run([sys.executable, "run_project.py", *args], cwd=LAB, env={**os.environ, **env},
                              capture_output=True, text=True, timeout=900)

    def test_remote_url_refused_before_anything_runs(self):
        res = self._run({"LOCAL_MODEL_URL": "http://192.168.1.20:11434/v1"}, "--real-model")
        self.assertEqual(res.returncode, 2)
        self.assertIn("refusing non-loopback model URL", json.loads(res.stdout.strip().splitlines()[-1])["error"])

    def test_real_model_switch_with_the_fake_on_loopback(self):
        _, url = adapters.start_fake_model()
        card_file = LAB / "out" / "scorecard.jsonl"
        saved = card_file.read_bytes() if card_file.exists() else None
        try:
            res = self._run({"LOCAL_MODEL_URL": url, "LOCAL_MODEL": "fake-model"}, "--real-model")
        finally:  # run_project.py always writes out/: put the committed default scorecard back
            if saved is not None:
                card_file.unlink(missing_ok=True)
                card_file.write_bytes(saved)
        card = json.loads(res.stdout.strip().splitlines()[-1])["scorecard"]
        self.assertEqual(res.returncode, 0, res.stdout[-2000:])
        self.assertEqual((card["passed"], card["checks"], card["model"]), (13, 13, "fake-model"))


class InjectionEvalTest(unittest.TestCase):
    def test_wilson(self):
        self.assertEqual(injection_eval.wilson(24, 40), (0.446, 0.7365))
        # NIST/SEMATECH e-Handbook 7.2.4.1 example: p = 0.13, n = 200, one-sided 95 % (z = 1.645) lower limit 0.09577
        self.assertAlmostEqual(injection_eval.wilson(26, 200, z=1.645)[0], 0.09577, places=4)
        lo, hi = injection_eval.wilson(0, 40)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.0876, places=4)

    def test_fake_model_obeys_but_nothing_executes(self):
        tmp = Path(tempfile.mkdtemp(prefix="scratch-", dir=Path(__file__).parent))
        try:
            self.assertEqual(injection_eval.main(["--here", "--naive", "--out", str(tmp)]), 0)
            (s,) = [json.loads(x) for x in (tmp / "08-injection-eval.jsonl").read_text(encoding="utf-8").splitlines()]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual((s["items"], s["obeyed"], s["executed"], s["unscoped"], s["effects"]), (40, 24, 0, 0, 0))
        self.assertEqual((s["naive_executed"], s["naive_effects"]), (24, 16))

    def test_remote_url_refused(self):
        old = os.environ.get("LOCAL_MODEL_URL")
        os.environ["LOCAL_MODEL_URL"] = "http://192.168.1.20:11434/v1"
        try:
            self.assertEqual(injection_eval.main(["--models", "qwen2.5:7b"]), 2)
        finally:
            os.environ.pop("LOCAL_MODEL_URL") if old is None else os.environ.__setitem__("LOCAL_MODEL_URL", old)


if __name__ == "__main__":
    unittest.main()
