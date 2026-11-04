"""Build task check (failureLab proof). Default: tests solution_strict.py.
Test YOUR version:  macOS  BUILD_IMPL=wycheproof_check python -m unittest -v test_build_task
                    Windows  $env:BUILD_IMPL="wycheproof_check"; python -m unittest -v test_build_task"""
import importlib
import os
import unittest

import wycheproof_check as wc

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_strict"))


class TestStrictWrappers(unittest.TestCase):
    def setUp(self):
        self.rows = wc.run(impl.aead_open, impl.sig_verify)

    def test_every_vector_passes(self):
        self.assertEqual(wc.failures(self.rows), [])
        self.assertEqual(len(self.rows), 21)

    def test_truncated_tag_rejected(self):
        self.assertEqual([r[4] for r in self.rows if "TruncatedTag" in r[2]], ["invalid", "invalid"])

    def test_non_canonical_signatures_rejected(self):
        self.assertEqual([r[4] for r in self.rows if {"TrailingBytes", "NonCanonicalS"} & set(r[2])], ["invalid"] * 2)


if __name__ == "__main__":
    unittest.main()
