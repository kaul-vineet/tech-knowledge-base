"""12-factor config: every per-deploy value comes from an env var, validated once at startup."""
import os
from dataclasses import dataclass, field

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}


class ConfigError(Exception):
    """Raised with ALL problems at once so a bad deploy fails fast and clearly."""


@dataclass(frozen=True)
class Settings:
    port: int
    db_path: str
    max_active_loans: int
    log_level: str
    # Secret: no default in code, and repr=False keeps it out of logs and tracebacks.
    smtp_password: str | None = field(default=None, repr=False)


def load_settings(environ=None):
    # config in the environment: read once at startup, then pass the frozen Settings around
    env = os.environ if environ is None else environ
    errors = []

    def integer(name, default, low, high):
        raw = env.get(name, str(default))
        try:
            value = int(raw)
        except ValueError:
            errors.append(f"{name}={raw!r} is not an integer")
            return default
        if not low <= value <= high:
            errors.append(f"{name}={value} must be between {low} and {high}")
        return value

    port = integer("LOANS_PORT", 8080, 1, 65535)
    max_loans = integer("LOANS_MAX_ACTIVE_LOANS", 3, 1, 50)
    log_level = env.get("LOANS_LOG_LEVEL", "INFO").upper()
    if log_level not in LOG_LEVELS:
        errors.append(f"LOANS_LOG_LEVEL={log_level!r} must be one of {sorted(LOG_LEVELS)}")
    db_path = env.get("LOANS_DB_PATH", "loans.db")
    if not db_path.strip():
        errors.append("LOANS_DB_PATH must not be empty")
    # fail fast: collect every problem, then refuse to start with all of them in one message
    if errors:
        raise ConfigError("; ".join(errors))
    return Settings(port, db_path, max_loans, log_level, env.get("LOANS_SMTP_PASSWORD") or None)
