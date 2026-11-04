"""Agent assist (optional): a LOCAL model drafts the model card prose; code checks every claim against the evidence.

Safety boundary: deterministic code decides. The agent sees only the evidence summary (no code, no keys) and
its draft is never published as-is: code extracts each claim (envelope, accuracy, key input, test count),
compares it with evidence.json and marks it OK or OVERCLAIM; any other number is reported as UNVERIFIED.

python agent_assist.py --fake    # deterministic fake model server (used by the tests)
python agent_assist.py           # local Ollama / llama.cpp server at LOCAL_MODEL_URL (default http://localhost:11434/v1)
"""
import argparse
import json
import re
import sys
import urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[1] / "_shared" / "local_agent"))  # vendored helper
from client import chat  # noqa: E402

MARKER = "[[SIM-CARD]]"  # lets the fake server recognise this lab's prompt; harmless for a real model
SYSTEM = "You draft documentation for simulation models. You never decide whether a model may be used."
PROMPT = (f"{MARKER} Draft the 'Validity and evidence' section of a model card in at most 5 short lines, using "
          "ONLY these facts. Use the phrases 'utilisation up to', 'within X% of Erlang C', 'most sensitive to' "
          "and 'N of M tests pass'.\n<evidence>\n{facts}\n</evidence>")
INPUT_NAMES = {"arrival rate": "lam", "arrival": "lam", "service rate": "mu", "service": "mu"}


def facts(ev):
    rows = "; ".join(f"rho {r['rho']}: error {r['rel_error']:.1%}, ok {r['ok']}" for r in ev["validation"])
    return (f"verification: {ev['verification']['tests_run']} tests, {ev['verification']['failures']} failures\n"
            f"validation vs Erlang C: {rows}\nvalidated envelope: utilisation <= {ev['envelope_rho_max']}\n"
            f"max error inside envelope: {ev['max_rel_error_in_envelope']:.1%}\n"
            f"elasticities of mean wait: arrival rate {ev['sensitivity']['lam']}, service rate {ev['sensitivity']['mu']}")


def check_claims(text, ev):
    """The decision: each recognised claim is compared with the evidence; the agent's wording decides nothing."""
    out = []
    if m := re.search(r"utilisation up to (\d*\.\d+)", text):
        out.append(("envelope", m.group(0), float(m.group(1)) <= ev["envelope_rho_max"]))
    if m := re.search(r"within (\d+(?:\.\d+)?)% of Erlang C", text):
        out.append(("accuracy", m.group(0), float(m.group(1)) / 100 >= ev["max_rel_error_in_envelope"] - 1e-9))
    if m := re.search(r"most sensitive to (?:the )?([a-z ]+?)(?: rate)?\b[ (.,]", text):
        named = INPUT_NAMES.get(m.group(1).strip(), m.group(1).strip())
        out.append(("key input", m.group(0).rstrip(" (.,"), named == ev["most_influential"]))
    if m := re.search(r"(\d+) of (\d+) tests pass", text):
        v = ev["verification"]
        out.append(("verification", m.group(0), int(m.group(1)) == int(m.group(2)) == v["tests_run"] and not v["failures"]))
    return out


def unverified_numbers(text, ev):
    known = [ev["envelope_rho_max"], ev["max_rel_error_in_envelope"] * 100, *ev["sensitivity"].values(),
             ev["verification"]["tests_run"], *[r["rho"] for r in ev["validation"]],
             *[r["rel_error"] * 100 for r in ev["validation"]]]
    return [t for t in re.findall(r"-?\d+(?:\.\d+)?", text) if not any(abs(float(t) - k) < 0.051 for k in known)]


def fake_card_writer(user_text):
    """Fake-model rule for MARKER: a fluent draft with two overclaims (envelope and accuracy) and one true claim."""
    return ("Validity and evidence (draft):\n- Valid for utilisation up to 0.95 with 3 desks.\n"
            "- Mean wait within 2.0% of Erlang C across the range.\n"
            "- Results are most sensitive to the service rate (elasticity -7.02).\n- 7 of 7 tests pass.")


def use_fake_rule(fake_model_server):
    """Register this lab's rule through the shared server's documented EXTRA_RULES hook (file unchanged)."""
    if (MARKER, fake_card_writer) not in fake_model_server.EXTRA_RULES:
        fake_model_server.EXTRA_RULES.append((MARKER, fake_card_writer))


def assist(ev, base_url=None, model=None):
    draft = chat([{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": PROMPT.replace("{facts}", facts(ev))}], base_url=base_url, model=model)
    return {"draft": draft, "claims": check_claims(draft, ev), "unverified": unverified_numbers(draft, ev)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fake", action="store_true", help="use the deterministic fake model server")
    path = HERE / "evidence.json"
    if not path.exists():
        sys.exit("Run python governance.py first: it writes evidence.json.")
    ev, base_url, server = json.loads(path.read_text(encoding="utf-8")), None, None
    if parser.parse_args().fake:
        import fake_model_server
        use_fake_rule(fake_model_server)
        server, base_url = fake_model_server.start_in_thread()  # binds 127.0.0.1 on a free port
    try:
        r = assist(ev, base_url)
    except (urllib.error.URLError, ConnectionError) as exc:
        sys.exit(f"No model server reachable ({exc}). Start Ollama, or run: python agent_assist.py --fake")
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("1. agent drafted:\n" + "\n".join("   " + line for line in r["draft"].splitlines()))
    print("2. code checked each claim against evidence.json:")
    for kind, text, ok in r["claims"]:
        print(f"   {'OK       ' if ok else 'OVERCLAIM'} {kind:12s} '{text}'")
    print(f"3. numbers not found in the evidence (UNVERIFIED): {', '.join(r['unverified']) or 'none'}")
    blocked = [c for c in r["claims"] if not c[2]] or len(r["claims"]) < 4
    print(f"4. code verdict: {'draft REJECTED - fix the claims, then re-run' if blocked else 'draft may go to human review'}")


if __name__ == "__main__":
    main()
