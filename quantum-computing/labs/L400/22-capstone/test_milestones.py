"""One test per capstone milestone (M1-M6). Run: python -m unittest -v
Uses run_capstone.collect(): real HTTP calls to 127.0.0.1, seeded faults, the fake model server only.
"""
import unittest

import pipeline
import run_capstone as rc


def setUpModule():
    global OUT, MS
    OUT = rc.collect()
    MS = {name.split()[0]: (ok, measure) for name, ok, measure in rc.milestones(OUT)}


class M1Api(unittest.TestCase):
    def test_api(self):
        self.assertTrue(MS["M1"][0], MS["M1"][1])
        with self.assertRaises(ValueError):
            pipeline.validate({"budget": 10})


class M2Orchestration(unittest.TestCase):
    def test_batched_cached_retried(self):
        self.assertTrue(MS["M2"][0], MS["M2"][1])
        self.assertEqual(MS["M2"][1], {"jobs": 10, "retries": 2, "transpiles": 1, "wall_s": 28.8, "mode": "batched"})


class M3CompileAndNoise(unittest.TestCase):
    def test_compile_and_white_noise_model(self):
        self.assertTrue(MS["M3"][0], MS["M3"][1])
        self.assertEqual(MS["M3"][1], {"esp": 0.5072, "cx": 52, "depth": 42, "gate_fidelity": 0.6224,
                                       "tvd_model": 0.0213, "tvd_ideal": 0.073})


class M4Mitigation(unittest.TestCase):
    def test_mitigation_reduces_readout_bias(self):
        self.assertTrue(MS["M4"][0], MS["M4"][1])
        m = MS["M4"][1]
        self.assertEqual((m["raw"], m["mitigated"], m["gate_noise_only"]), (6.774, 6.8549, 6.8418))


class M5BenchmarkAndDecision(unittest.TestCase):
    def test_fair_and_code_decides(self):
        self.assertTrue(MS["M5"][0], MS["M5"][1])
        self.assertEqual(MS["M5"][1]["winner"], "annealing")


class M6AgentExplains(unittest.TestCase):
    def test_explanations_are_checked(self):
        self.assertTrue(MS["M6"][0], MS["M6"][1])


if __name__ == "__main__":
    unittest.main()
