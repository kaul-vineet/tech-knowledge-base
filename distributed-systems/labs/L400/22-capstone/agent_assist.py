"""Agent assist (optional): a LOCAL model explains the chaos campaign to an on-call engineer; code checks every claim.
python run_capstone.py --explain --fake   # deterministic fake model server (used by the tests)
python run_capstone.py --explain          # real local model: LOCAL_MODEL_URL (default Ollama http://localhost:11434/v1)
Boundary: checks.py and run_capstone.py decide pass/fail. The model sees only experiment results (no secrets, no
customer data) and cannot change the verdict: its 'verdict' line is shown as ignored."""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import client, fake_model_server  # noqa: E402

MARKER = "[[CHAOS-SCORECARD]]"


def ask(rows, base_url=None):
    system = ("You explain chaos-experiment results to an on-call engineer. For every experiment write one line "
              "'fault: <name> held=<yes|no> harmed=<n>' (harmed = total harmed orders over all seeds), then "
              "'summary: <one sentence on what the results mean>'. Do not decide whether to release.")
    user = f"{MARKER} Campaign results, one object per run:\n" + "\n".join(json.dumps(r, sort_keys=True) for r in rows)
    return client.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], base_url=base_url)


def truth(rows):
    out = {}
    for r in rows:
        held, harmed = out.get(r["experiment"], (True, 0))
        out[r["experiment"]] = (held and r["held"], harmed + r["harmed_orders"])
    return {k: ("yes" if held else "no", harmed) for k, (held, harmed) in out.items()}


def check(reply, rows):
    """[(fault, agent claim, code value, ok)]: every experiment must be claimed, and correctly."""
    claims = {m[0]: (m[1], int(m[2])) for m in re.findall(r"^fault:\s*(\S+)\s+held=(yes|no)\s+harmed=(\d+)", reply, re.M)}
    return [(name, claims.get(name), real, claims.get(name) == real) for name, real in truth(rows).items()]


def explain(rows, fake=False):
    srv, url = fake_model_server.start_in_thread() if fake else (None, None)
    try:
        reply = ask(rows, url)
    except OSError as e:
        print(f"no model server reachable ({e}); start Ollama or use --fake")
        return None
    finally:
        if srv:
            srv.shutdown()
            srv.server_close()
    results = check(reply, rows)
    for name, claim, real, ok in results:
        print(f"agent check {name:19} agent: {claim} code: {real} {'OK' if ok else 'WRONG'}")
    absorbed = sum(r["duplicates_absorbed"] for r in rows)
    for line in reply.splitlines():
        if line.lower().startswith("summary:"):
            n = re.search(r"absorbed (\d+)", line)
            tag = "unverified" if not n else ("number OK" if int(n[1]) == absorbed else f"number WRONG, code: {absorbed}")
            print(f"agent summary ({tag}):", line[8:].strip())
        if line.lower().startswith("verdict:"):
            print("agent verdict IGNORED (code decides):", line[8:].strip())
    return results
