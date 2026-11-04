"""Unit tests + fault reproduction for lesson 21 (stdlib + numpy; astropy/cffconvert checks are skipped locally)."""
import json
import tempfile
import unittest
from pathlib import Path

import defects
import inputs
import release
import votable


class TestPieces(unittest.TestCase):
    def test_votable_round_trip_and_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "t.vot"
            votable.write(p, inputs.rows(3))
            self.assertEqual(votable.check(p), [])
            text = p.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("<?xml version='1.0' encoding='utf-8'?>"))
            self.assertIn('<VOTABLE version="1.5" xmlns="http://www.ivoa.net/xml/VOTable/v1.3">', text)
            p.write_text(text.replace("<TD>4000001</TD>", "<TD>x1</TD>"), encoding="utf-8")
            self.assertEqual(votable.check(p), ["votable: row 1 source_id='x1' is not long"])

    def test_cff_required_keys(self):
        self.assertTrue({"cff-version", "message", "title", "authors"} <= release.cff_keys(release.citation_cff("MIT")))

    def test_credit_texts_are_the_providers_wording(self):
        gaia = inputs.INPUTS[0]["credit"]
        self.assertTrue(gaia.startswith("This work has made use of data from the European Space Agency (ESA) mission Gaia"))
        self.assertTrue(gaia.endswith("participating in the Gaia Multilateral Agreement."))


class TestFailureLab(unittest.TestCase):
    """Shipped release_licence() always answers CC-BY-4.0 - the Gaia input's NonCommercial condition is dropped."""

    def test_check_blocks_the_shipped_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = release.build(Path(tmp) / "r")
            self.assertEqual(release.check(d), ["licence: release CC-BY-4.0 drops the NC condition of input "
                                                "gaia_dr3_astrometry (LicenseRef-CC-BY-NC-3.0-IGO)"])
            self.assertEqual(json.loads((d / "metadata.json").read_text(encoding="utf-8"))["licence"], "CC-BY-4.0")


class TestOptionsEvidence(unittest.TestCase):
    def test_files_present_catches_nothing_check_catches_all(self):
        result = defects.caught()
        self.assertEqual(sum(r[0] for r in result.values()), 0)
        self.assertEqual(sum(r[1] for r in result.values()), 6)


class TestExternalValidators(unittest.TestCase):
    def test_astropy_reads_the_votable(self):
        try:
            import validate_external
        except ImportError:
            self.skipTest("astropy not installed (pending-ci)")
        n, cols, cff_ok = validate_external.validate()
        self.assertEqual((n, cols[0]), (8, "source_id"))
        self.assertIn(cff_ok, (True, None))  # None: cffconvert not on PATH


if __name__ == "__main__":
    unittest.main()
