"""One test class per milestone (M1-M5)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import contract  # noqa: E402
import model  # noqa: E402
import pipeline  # noqa: E402
import registry  # noqa: E402
import run_project  # noqa: E402


class M1ModelVerified(unittest.TestCase):
    def test_ci_covers_mm1_formula_and_same_seed_same_bits(self):
        rows, same = run_project.verify_model()
        self.assertTrue(same)
        for r in rows:
            self.assertTrue(r["covered"], r)

    def test_model_version_is_hash_of_reused_source(self):
        self.assertEqual(len(model.VERSION), 12)
        self.assertAlmostEqual(model.mm1_wq(0.8, 1.0), 4.0, places=12)


class M2ContractGate(unittest.TestCase):
    def test_invalid_proposals_never_run(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(10**6))
        for bad in ({"baseline": {"lam": 0.97, "mu": 1.0}, "candidate": _fixture.B},
                    {"baseline": _fixture.A, "candidate": {"lam": 0.9, "mu": 0.95}}):
            self.assertEqual(pl.submit("run_experiment", bad)["status"], "rejected")
        self.assertEqual((len(pl.registry.runs()), pl.budget.spent), (0, 0))

    def test_tool_spec_and_validator_share_one_schema(self):
        spec = {t["function"]["name"]: t["function"]["parameters"] for t in contract.TOOLS}
        self.assertEqual(spec, contract.SCHEMAS)


class M3Registry(unittest.TestCase):
    def test_run_record_has_identity_fields_and_persists(self):
        path = _fixture.LAB / "out" / "test-registry.jsonl"
        path.parent.mkdir(exist_ok=True)
        path.unlink(missing_ok=True)
        try:
            reg = registry.Registry(path)
            v = model.run_once(_fixture.A, 7)
            rec = reg.record_run(_fixture.A, 7, v, "job-x")
            reg.close()
            for key in ("run_id", "params_hash", "model", "version", "seed", "value_hex", "env"):
                self.assertIn(key, rec)
            again = registry.Registry(path)
            self.assertEqual(again.runs()[0]["run_id"], rec["run_id"])
            self.assertEqual(registry.digest({**rec["params"]}, 12), rec["params_hash"])
        finally:
            path.unlink(missing_ok=True)

    def test_same_params_and_seed_give_the_same_run_id(self):
        reg = registry.Registry()
        a = reg.record_run(_fixture.A, 7, 1.0, "j1")["run_id"]
        b = reg.record_run(dict(reversed(list(_fixture.A.items()))), 7, 1.0, "j2")["run_id"]
        self.assertEqual(a, b)


class M4Replications(unittest.TestCase):
    def test_default_session_meets_target_half_width(self):
        _, f = _fixture.ab_facts(_fixture.session()[0])
        self.assertEqual(f["replications"], 55)
        self.assertLessEqual(f["difference_half_width"], run_project.HALF_WIDTH)
        self.assertEqual(f["verdict"], "significant decrease")


class M5ClaimCheck(unittest.TestCase):
    def test_hallucinated_sentence_rejected_and_published_text_rechecks_clean(self):
        reg, _, _, rows, published = _fixture.session()
        bad = [r for r in rows if not r["ok"]]
        self.assertEqual([r["sentence"] for r in bad], ["At lam 0.97 the mean wait would be about 32.3 min."])
        import claims
        self.assertTrue(all(r["ok"] for r in claims.review(published, reg)[0]))


if __name__ == "__main__":
    unittest.main()
