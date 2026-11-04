"""Startup: load + validate config first; refuse to start on bad config. Run: python app.py"""
import sys

from config import ConfigError, load_settings


def main():
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"invalid configuration: {exc}", file=sys.stderr)
        return 2  # non-zero exit: the deploy fails before serving any traffic
    print(f"starting with {settings}")
    print(f"smtp password: {'set' if settings.smtp_password else 'not set'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
