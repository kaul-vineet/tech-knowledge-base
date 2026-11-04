"""Build task check (lesson 17): the extracted fines service matches the monolith on all seeded traffic.

By default this checks solution/fines_service.py. To check your edited fines_service.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

from strangler import Facade, LegacyFines, ServiceFines, cutover_decision, replay
from traffic import requests

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("fines_service.py" if os.environ.get("CHECK_MINE") else "solution/fines_service.py")
spec = importlib.util.spec_from_file_location("fines_service_under_test", TARGET)
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)


class ExtractedServiceTest(unittest.TestCase):
    def test_half_cent_rounds_up_like_the_monolith(self):
        self.assertEqual([service.fine_for(d, "student") for d in (3, 5, 7)], ["0.13", "0.38", "0.63"])

    def test_cap_and_grace_days(self):
        self.assertEqual([service.fine_for(d, "adult") for d in (0, 2, 3, 60)], ["0.00", "0.00", "0.25", "10.00"])

    def test_parallel_run_allows_cutover(self):
        facade = Facade(LegacyFines(), ServiceFines(fn=service.fine_for), mode="shadow")
        replay(facade, list(requests()))
        decision = cutover_decision(facade.shadow.stats)
        self.assertTrue(decision["ready"], decision)


if __name__ == "__main__":
    unittest.main()
