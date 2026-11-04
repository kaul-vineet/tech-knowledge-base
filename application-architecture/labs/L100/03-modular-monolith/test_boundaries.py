import pathlib
import unittest

from check_boundaries import package_of, scan, violations
from library import catalog, loans

HERE = pathlib.Path(__file__).parent


class BoundaryRuleTest(unittest.TestCase):
    def test_real_code_has_no_violations(self):
        count, problems = scan(HERE)
        self.assertGreater(count, 0)
        self.assertEqual(problems, [])

    def test_absolute_import_of_other_internals_is_caught(self):
        src = "from library.catalog.internal.store import BOOKS"
        self.assertEqual(len(violations(src, "library.loans.internal")), 1)

    def test_importing_internal_as_name_is_caught(self):
        self.assertEqual(len(violations("from library.catalog import internal", "library.loans")), 1)

    def test_relative_import_of_other_internals_is_caught(self):
        # file library/loans/service.py doing: from ..catalog.internal import store
        self.assertEqual(len(violations("from ..catalog.internal import store", "library.loans")), 1)

    def test_public_interface_and_own_internals_are_allowed(self):
        src = "from library import catalog\nfrom library.loans.internal import rules\nimport library.catalog"
        self.assertEqual(violations(src, "library.loans"), [])


class CrossPlatformPathTest(unittest.TestCase):
    def test_windows_and_posix_paths_give_the_same_package(self):
        win = pathlib.PureWindowsPath(r"library\loans\internal\rules.py")
        posix = pathlib.PurePosixPath("library/loans/internal/rules.py")
        self.assertEqual(package_of(win), "library.loans.internal")
        self.assertEqual(package_of(posix), package_of(win))

    def test_reports_use_forward_slashes(self):
        win = pathlib.PureWindowsPath(r"library\loans\shortcut.py")
        found = violations("from ..catalog.internal import store", package_of(win), win.as_posix())
        self.assertTrue(found[0].startswith("library/loans/shortcut.py:1 "))


class ModulesWorkTogetherTest(unittest.TestCase):
    def test_borrow_and_return_through_public_interfaces(self):
        loan_id = loans.borrow("b2", "m1")
        self.assertFalse(catalog.is_available("b2"))
        loans.give_back(loan_id)
        self.assertTrue(catalog.is_available("b2"))


if __name__ == "__main__":
    unittest.main()
