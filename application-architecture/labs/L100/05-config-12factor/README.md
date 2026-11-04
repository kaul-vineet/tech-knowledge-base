# Lab 05 – Configuration the 12-factor way

All per-deploy values come from environment variables, with safe defaults for
non-secrets, validated once at startup. A bad value stops the process with exit code 2.
Secrets have no default in code and never appear in `repr`/logs.

| Variable | Default | Rule |
|---|---|---|
| `LOANS_PORT` | `8080` | integer 1–65535 |
| `LOANS_DB_PATH` | `loans.db` | not empty |
| `LOANS_MAX_ACTIVE_LOANS` | `3` | integer 1–50 |
| `LOANS_LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR (case-insensitive) |
| `LOANS_SMTP_PASSWORD` | *(none)* | secret – optional here, never printed |

## Files
| File | Purpose |
|---|---|
| `config.py` | `Settings` dataclass + `load_settings(environ)` with validation |
| `app.py` | Startup: load config or exit 2 with all errors |
| `test_config.py` | Defaults, overrides, aggregated errors, secret hiding, startup exit codes, no literal secrets in code |
| `try_it.py` | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |

## Run: the same config, two shells
zsh (Mac mini) and PowerShell (Windows PC) set environment variables differently; `config.py` reads
them the same way. Use upper-case names: Windows treats `loans_port` and `LOANS_PORT` as one variable,
macOS does not.

**Mac mini (zsh)**: `export` for the session, or `VAR=value command` for one command
```bash
cd labs/L100/05-config-12factor
python app.py
export LOANS_PORT=9000 LOANS_LOG_LEVEL=debug LOANS_SMTP_PASSWORD=example-only
python app.py
unset LOANS_PORT LOANS_LOG_LEVEL LOANS_SMTP_PASSWORD
LOANS_PORT=abc LOANS_LOG_LEVEL=LOUD python app.py; echo "exit=$?"
python -m unittest -v
```
**Windows PC (PowerShell)**: `$env:` lasts for the session; there is no one-command form
```powershell
cd labs\L100\05-config-12factor
python app.py
$env:LOANS_PORT = "9000"; $env:LOANS_LOG_LEVEL = "debug"; $env:LOANS_SMTP_PASSWORD = "example-only"
python app.py
Remove-Item Env:\LOANS_*
$env:LOANS_PORT = "abc"; $env:LOANS_LOG_LEVEL = "LOUD"
python app.py; "exit=$LASTEXITCODE"
Remove-Item Env:\LOANS_*
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15; the zsh commands were run with bash, which uses the same syntax)
```
starting with Settings(port=8080, db_path='loans.db', max_active_loans=3, log_level='INFO')
smtp password: not set
starting with Settings(port=9000, db_path='loans.db', max_active_loans=3, log_level='DEBUG')
smtp password: set
invalid configuration: LOANS_PORT='abc' is not an integer; LOANS_LOG_LEVEL='LOUD' must be one of ['DEBUG', 'ERROR', 'INFO', 'WARNING']
exit=2
```
The PowerShell sequence should print the same lines (not run here; covered by the CI matrix on `windows-latest`,
which runs the tests, not the PowerShell commands).
```
test_env_name_case_rule_of_this_os (test_config.EnvNameCaseTest.test_env_name_case_rule_of_this_os) ... ok
test_all_errors_reported_together (test_config.LoadSettingsTest.test_all_errors_reported_together) ... ok
test_defaults_when_env_is_empty (test_config.LoadSettingsTest.test_defaults_when_env_is_empty) ... ok
test_env_overrides_defaults (test_config.LoadSettingsTest.test_env_overrides_defaults) ... ok
test_port_range_is_checked (test_config.LoadSettingsTest.test_port_range_is_checked) ... ok
test_secret_is_never_shown (test_config.LoadSettingsTest.test_secret_is_never_shown) ... ok
test_no_hardcoded_secret_assignments (test_config.NoSecretsInCodeTest.test_no_hardcoded_secret_assignments) ... ok
test_bad_config_fails_fast (test_config.StartupTest.test_bad_config_fails_fast) ... ok
test_good_config_starts (test_config.StartupTest.test_good_config_starts) ... ok

----------------------------------------------------------------------
Ran 9 tests in 1.692s

OK
```

## Caution
Env vars keep secrets out of the repo, but OWASP notes they are visible to all processes
of the same user and can end up in logs or dumps; in production prefer a secrets manager
or orchestrator-mounted files, and never bake secrets into images (`ENV`/`ARG`).

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] LOANS_LOG_LEVEL=warn -> exit 2: invalid configuration: LOANS_LOG_LEVEL='WARN' must be one of ['DEBUG', 'ERROR', 'INFO', 'WARNING']
[2] repr=True -> starting with Settings(port=8080, db_path='loans.db', max_active_loans=3, log_level='INFO', smtp_password='example-only')
[2] python -m unittest -> exit 1; FAILED (failures=2)
    FAIL: test_secret_is_never_shown (test_config.LoadSettingsTest.test_secret_is_never_shown)
    FAIL: test_good_config_starts (test_config.StartupTest.test_good_config_starts)
```

## Troubleshooting
| Symptom | Action |
|---|---|
| Value change has no effect | `os.environ` is captured when Python starts; set the variable before launching the process. |
| Secret shows up in a log line | Print the `Settings` object (secret field has `repr=False`), never `os.environ` or the raw value. |
| `loans_port=9000` works on Windows but is ignored on macOS | Env names are case-insensitive on Windows (Python upper-cases `os.environ` keys) and case-sensitive on macOS; always use `LOANS_*`. `test_env_name_case_rule_of_this_os` shows your OS's rule. |
| PowerShell: an old value still applies | `$env:` lasts for the session: `Remove-Item Env:\LOANS_*` or open a new window. |
