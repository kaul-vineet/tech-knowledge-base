"""Feature flags as a file in the repo (static, reviewable) with owner and expiry (not lesson code).

A release toggle is transitional: it must be removed before it expires. gate_flags() is the fitness function.
"""
import json
import pathlib
from datetime import date

HERE = pathlib.Path(__file__).resolve().parent


class Flags:
    def __init__(self, path=HERE / "flags.json", today=date(2026, 10, 28)):
        self.flags = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))["flags"]
        self.today, self.overrides = today, {}

    def enabled(self, name):
        return self.overrides.get(name, self.flags[name]["on"])

    def set(self, name, value):  # runtime override for the rollout simulation and tests
        self.overrides[name] = value

    def expired(self):
        return sorted(n for n, f in self.flags.items() if date.fromisoformat(f["expires"]) < self.today)


def gate_flags(flags):
    expired = flags.expired()
    return {"gate": "no-expired-flags", "ok": not expired, "value": expired, "budget": 0}
