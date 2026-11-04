"""Build task check. Default: tests solution_intermediate.py.
Test YOUR version:  macOS  BUILD_IMPL=local_ca python -m unittest test_build_task
                    Windows  $env:BUILD_IMPL="local_ca"; python -m unittest test_build_task"""
import importlib
import os
import unittest

from cryptography import x509
from cryptography.x509.verification import VerificationError

import local_ca

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_intermediate"))


class TestIntermediate(unittest.TestCase):
    def test_three_link_chain(self):
        root, inter, leaf, _ = impl.make_hierarchy()
        chain = local_ca.verify(leaf, [root], "localhost", intermediates=[inter])
        self.assertEqual([c.subject for c in chain], [leaf.subject, inter.subject, root.subject])

    def test_missing_intermediate_fails(self):
        root, _, leaf, _ = impl.make_hierarchy()
        with self.assertRaises(VerificationError):
            local_ca.verify(leaf, [root], "localhost")

    def test_intermediate_cannot_sign_cas(self):
        _, inter, _, _ = impl.make_hierarchy()
        self.assertEqual(inter.extensions.get_extension_for_class(x509.BasicConstraints).value.path_length, 0)


if __name__ == "__main__":
    unittest.main()
