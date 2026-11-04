"""Try it 1: give the injection session send_email in its token scope. Does the injected email go out now?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import corpus  # noqa: E402
import scenarios as sc  # noqa: E402
from adapters import HttpModel, start_fake_model  # noqa: E402


def run():
    _, url = start_fake_model()
    registry, _ = sc.load_registry()
    env = sc.Env(HttpModel(url), registry, extra_docs=sc.POISON)
    env.run(corpus.TASK, corpus.SCOPE + ["send_email"], corpus.ARG_RULES)  # the only change: wider scope
    call = [c for c in env.host.calls if c["tool"] == "send_email"][0]
    deny = [env.audit.bodies[e["seq"]]["deny"] for e in env.audit.entries if e["event"] == "decision"][-1]
    return {"scope_ok": call["scope_ok"], "executed": call["executed"], "deny": deny, "effects": env.world.effects}


if __name__ == "__main__":
    print(run())
