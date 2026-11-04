import contextlib
import io
import json
import pathlib
import shutil
import tempfile
import unittest
from datetime import date

import api
import app_versions
import dashboard
import migrations
import rollout
from flags import Flags, gate_flags

HERE = pathlib.Path(__file__).resolve().parent


class MigrationStepTest(unittest.TestCase):
    def test_expand_is_idempotent_and_old_code_still_works(self):
        db = migrations.connect()
        migrations.expand(db)
        migrations.expand(db)
        self.assertEqual(migrations.columns(db), ["id", "name", "given_name", "family_name"])
        member = app_versions.create(db, 1, "Ada Lovelace")
        self.assertEqual(app_versions.read(db, 1, member, Flags()), ("Ada", "Lovelace"))

    def test_backfill_in_batches(self):
        db = migrations.connect()
        for i in range(120):
            app_versions.create(db, 1, "Grace Hopper")
        migrations.expand(db)
        self.assertEqual((migrations.backfill(db, batch=50), migrations.missing_new_values(db)), (120, 0))

    def test_v1_api_survives_the_contract(self):
        db = migrations.connect()
        migrations.expand(db)
        member = app_versions.create(db, 2, "Barbara Liskov")
        migrations.contract(db)
        body, headers = api.get_member(db, member, 1)
        self.assertEqual(body, {"id": member, "name": "Barbara Liskov"})
        self.assertEqual(headers["Deprecation"], "@1793491200")
        self.assertEqual(api.get_member(db, member, 2)[0]["familyName"], "Liskov")


class RolloutTest(unittest.TestCase):
    def test_symptom_big_bang_breaks_old_instances(self):
        r, _ = rollout.big_bang(migrations)
        self.assertEqual((r.errors, r.log[0]), (36, "v1: no such column: name"))

    def test_symptom_premature_contract(self):
        r, _ = rollout.expand_contract(migrations)
        self.assertEqual((r.errors, r.log[0]), (62, "v2: table members has no column named name"))


class FitnessHistoryTest(unittest.TestCase):
    def test_flags_gate(self):
        self.assertTrue(gate_flags(Flags())["ok"])
        self.assertEqual(gate_flags(Flags(today=date(2026, 12, 1)))["value"], ["read_split_name"])

    def test_dashboard_flags_broken_steps(self):
        work = pathlib.Path(tempfile.mkdtemp(prefix=".tmp-", dir=HERE))
        self.addCleanup(shutil.rmtree, work, True)
        rows = [{"plan": "p", "step": "a", "errors": 0, "flags_expired": 0, "fleet": "v1", "unbackfilled": 0,
                 "columns": ["id"]}, {"plan": "p", "step": "b", "errors": 3, "flags_expired": 0, "fleet": "v2",
                                      "unbackfilled": 0, "columns": ["id"]}]
        (work / "h.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual([p for _, p in dashboard.judge(rows)], [[], ["errors=3 > 0"]])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dashboard.main(["--file", str(work / "h.jsonl")]), 1)


if __name__ == "__main__":
    unittest.main()
