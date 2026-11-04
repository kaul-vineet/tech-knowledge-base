"""Build task check (failureLab proof). Default: tests solution_renewal.py.
Test YOUR version:  macOS  BUILD_IMPL=cert_lifecycle python -m unittest -v test_build_task
                    Windows  $env:BUILD_IMPL="cert_lifecycle"; python -m unittest -v test_build_task"""
import importlib
import os
import random
import unittest

import cert_lifecycle as cl

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_renewal"))


class TestRenewal(unittest.TestCase):
    def test_no_expired_cert_is_ever_served(self):
        failures, srv = cl.simulate(impl.Server, days=21, log=lambda line: None)
        self.assertEqual(failures, [])
        self.assertGreaterEqual(srv.renewals, 3)

    def test_ca_outage_alerts_and_recovers(self):
        lines = []
        failures, srv = cl.simulate(impl.Server, days=21, ca_down=range(90, 125), log=lines.append)
        self.assertEqual(failures, [])
        self.assertTrue(any('"alert": "cert_expiry_soon"' in line for line in lines))  # monitoring saw it

    def test_jitter_spreads_a_fleet(self):
        ca_key, ca = cl.local_ca.make_root()
        cert = cl.issue(ca_key, ca, cl.T0)
        times = [impl.next_renewal(cert, random.Random(seed)) for seed in range(50)]
        hours = {round((t - cert.not_valid_before_utc) / cl.HOUR) for t in times}
        self.assertGreaterEqual(len(hours), 10)  # not one thundering herd
        for t in times:
            frac = (t - cert.not_valid_before_utc) / cl.LIFETIME
            self.assertTrue(0.5 <= frac <= 0.8, frac)  # well before expiry, not absurdly early


if __name__ == "__main__":
    unittest.main()
