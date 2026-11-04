"""Policy decision point adapter: the tools.rego file evaluated by rego_lite (application-architecture L400 #19)."""
from pathlib import Path

import _kb

rego_lite = _kb.load("rego_lite")
POLICY = Path(__file__).resolve().parent / "policy" / "tools.rego"


class RegoPolicy:
    def __init__(self, path=POLICY):
        self.policy = rego_lite.load_policy(path)
        self.revision = self.policy.revision  # logged with every decision: decisions can be replayed later

    def decide(self, inp):
        values, matched = self.policy.evaluate(inp)
        return {"allowed": values.get("allowed") is True, "deny": values.get("deny") or [],
                "needs_approval": values.get("needs_approval") is True, "matched": matched, "revision": self.revision}
