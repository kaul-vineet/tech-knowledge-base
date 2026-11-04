import os
import pathlib
import re
import subprocess
import sys
import unittest

from config import ConfigError, load_settings

HERE = pathlib.Path(__file__).parent


class LoadSettingsTest(unittest.TestCase):
    def test_defaults_when_env_is_empty(self):
        s = load_settings({})
        self.assertEqual((s.port, s.db_path, s.max_active_loans, s.log_level, s.smtp_password),
                         (8080, "loans.db", 3, "INFO", None))

    def test_env_overrides_defaults(self):
        s = load_settings({"LOANS_PORT": "9000", "LOANS_LOG_LEVEL": "debug",
                           "LOANS_MAX_ACTIVE_LOANS": "5", "LOANS_DB_PATH": "/data/l.db"})
        self.assertEqual((s.port, s.log_level, s.max_active_loans, s.db_path),
                         (9000, "DEBUG", 5, "/data/l.db"))

    def test_all_errors_reported_together(self):
        with self.assertRaises(ConfigError) as ctx:
            load_settings({"LOANS_PORT": "abc", "LOANS_MAX_ACTIVE_LOANS": "0", "LOANS_LOG_LEVEL": "LOUD"})
        message = str(ctx.exception)
        for name in ("LOANS_PORT", "LOANS_MAX_ACTIVE_LOANS", "LOANS_LOG_LEVEL"):
            self.assertIn(name, message)

    def test_port_range_is_checked(self):
        with self.assertRaisesRegex(ConfigError, "between 1 and 65535"):
            load_settings({"LOANS_PORT": "70000"})

    def test_secret_is_never_shown(self):
        s = load_settings({"LOANS_SMTP_PASSWORD": "s3cr3t-value"})
        self.assertEqual(s.smtp_password, "s3cr3t-value")
        self.assertNotIn("s3cr3t-value", repr(s))
        self.assertNotIn("s3cr3t-value", str(s))


class StartupTest(unittest.TestCase):
    def run_app(self, **env):
        clean = {k: v for k, v in os.environ.items() if not k.startswith("LOANS_")}
        return subprocess.run([sys.executable, "app.py"], cwd=HERE, env={**clean, **env},
                              capture_output=True, text=True, encoding="utf-8")

    def test_good_config_starts(self):
        result = self.run_app(LOANS_PORT="9000", LOANS_SMTP_PASSWORD="xyz-not-printed")
        self.assertEqual(result.returncode, 0)
        self.assertIn("port=9000", result.stdout)
        self.assertNotIn("xyz-not-printed", result.stdout)

    def test_bad_config_fails_fast(self):
        result = self.run_app(LOANS_PORT="not-a-port")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid configuration", result.stderr)


class EnvNameCaseTest(unittest.TestCase):
    def test_env_name_case_rule_of_this_os(self):
        # Windows: os.environ upper-cases keys, so loans_port and LOANS_PORT are one variable.
        # macOS/Linux: names are case-sensitive, so a lower-case name is simply ignored by config.py.
        os.environ["loans_case_probe"] = "1"
        try:
            self.assertEqual("LOANS_CASE_PROBE" in os.environ, os.name == "nt")
        finally:
            del os.environ["loans_case_probe"]


class NoSecretsInCodeTest(unittest.TestCase):
    def test_no_hardcoded_secret_assignments(self):
        pattern = re.compile(r"(password|secret|token|api_key)\s*=\s*['\"][^'\"]+['\"]", re.I)
        for path in HERE.glob("*.py"):
            if path.name != "test_config.py":
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), f"literal secret in {path.name}")


if __name__ == "__main__":
    unittest.main()
