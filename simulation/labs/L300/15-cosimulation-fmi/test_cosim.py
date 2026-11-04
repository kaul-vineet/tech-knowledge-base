import json
import math
import unittest
from pathlib import Path

import cosim
from units import Room, Thermostat

HERE = Path(__file__).resolve().parent


class TestUnits(unittest.TestCase):
    def test_room_solver_matches_the_exact_solution(self):
        room = Room()
        room.instantiate()
        room.setup_experiment(0.0)
        room.set_real([room.vr("heater")], [0.5])
        room.do_step(0.0, 1800.0)
        t_eq = 5 + 0.008 * 3000 * 0.5  # 17 C
        exact = t_eq + (15 - t_eq) * math.exp(-1800 / 3600)
        self.assertAlmostEqual(room.get_real([room.vr("T")])[0], exact, places=6)

    def test_interface_uses_value_references(self):
        ctrl = Thermostat(setpoint=19.0)
        ctrl.instantiate()
        self.assertEqual(ctrl.get_real([ctrl.vr("setpoint")]), [19.0])

    def test_small_step_settles_at_setpoint(self):
        m = cosim.metrics(cosim.run(60))
        self.assertEqual(m["last_hour_swing_C"], 0.0)
        self.assertEqual(m["last_hour_mean_error_C"], 0.0)

    def test_log_is_valid_json_lines(self):
        path = HERE / "cosim_log_test.jsonl"
        try:
            records = cosim.run(600, hours=1, log_path=path)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual([json.loads(x) for x in lines], records)
        finally:
            path.unlink(missing_ok=True)


class TestFailureLab(unittest.TestCase):
    """Physics of the fault and the fix at explicit steps. Your fix to COMM_STEP_S is checked by test_build_task.py."""

    def test_fault_large_step_oscillates(self):
        m = cosim.metrics(cosim.run(900))
        self.assertGreater(m["last_hour_swing_C"], 3.0)
        self.assertGreaterEqual(m["heater_flips"], 5)

    def test_fix_small_step_is_stable(self):
        m = cosim.metrics(cosim.run(60))
        self.assertLess(m["last_hour_swing_C"], 0.2)
        self.assertLessEqual(m["heater_flips"], 2)

    def test_stability_bound_from_theory(self):
        # P-loop with one step of delay: stable iff (1 - exp(-h/tau)) * K < 1, K = Kp*Q*R = 12 -> h < 313 s
        h_max = 3600 * math.log(12 / 11)
        self.assertLess(cosim.metrics(cosim.run(0.75 * h_max))["last_hour_swing_C"], 0.2)
        self.assertGreater(cosim.metrics(cosim.run(1.15 * h_max))["last_hour_swing_C"], 1.0)


try:
    import fmpy  # noqa: F401
except ImportError:  # FMPy runs in CI only
    fmpy = None


@unittest.skipIf(fmpy is None, "fmpy not installed (pending-ci)")
class TestFMPyEquivalent(unittest.TestCase):
    def test_fmpy_offers_the_api_the_adapter_uses(self):
        import fmpy_cosim
        self.assertTrue(fmpy_cosim.api_check())

    @unittest.skipUnless((HERE / "RoomThermal.fmu").exists(), "RoomThermal.fmu not exported (manual OpenModelica step)")
    def test_fmu_room_matches_the_python_room(self):
        import fmpy_cosim
        fmu = cosim.metrics(cosim.run(60, room=fmpy_cosim.FMURoom(str(HERE / "RoomThermal.fmu"))))
        self.assertLess(fmu["last_hour_swing_C"], 0.2)


if __name__ == "__main__":
    unittest.main()
