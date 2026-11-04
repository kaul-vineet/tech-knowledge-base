import contextlib
import io
import unittest

import check_env


class CheckEnvTest(unittest.TestCase):
    def test_current_python_is_supported(self):
        self.assertTrue(check_env.check_python())

    def test_old_python_is_rejected(self):
        self.assertFalse(check_env.check_python((3, 11, 9)))

    def test_all_required_stdlib_modules_import(self):
        self.assertEqual(check_env.missing_modules(), [])

    def test_unknown_module_is_reported(self):
        self.assertEqual(check_env.missing_modules(["no_such_module_xyz"]), ["no_such_module_xyz"])

    def test_main_returns_zero(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(check_env.main(), 0)
        self.assertIn("python", out.getvalue())

    def test_optional_tools_cover_both_container_engines(self):
        self.assertTrue({"podman", "docker", "npx"} <= set(check_env.OPTIONAL_TOOLS))


if __name__ == "__main__":
    unittest.main()
