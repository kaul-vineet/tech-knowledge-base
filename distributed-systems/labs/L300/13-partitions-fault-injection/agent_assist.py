"""Agent assist (optional): a LOCAL model explains the partition history; code checks every claim it makes.
python agent_assist.py --fake   # deterministic fake model server (no download; used by the tests)
python agent_assist.py          # real local model: LOCAL_MODEL_URL (default Ollama http://localhost:11434/v1)
Boundary: the checker (checker.py) decides what happened; the agent's prose is shown only next to the verdicts."""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import client, fake_model_server  # noqa: E402

import partition as pt  # noqa: E402
from checker import check_register, stale_reads  # noqa: E402
from helpers import jsonl  # noqa: E402

MARKER = "[[PARTITION-HISTORY]]"


def ask_agent(events, history, base_url=None):
    system = ("You review distributed-system test histories. Answer with exactly four lines: 'linearizable: yes|no', "
              "'stale_leader: <node>', 'lost_write: <process> write <value>', 'summary: <one sentence>'.")
    user = (f"{MARKER} Events:\n" + "\n".join(events) + "\nHistory (one operation event per line):\n"
            + "\n".join(jsonl(history)) + "\nWhich node acted on a stale lease, and whose acknowledged write was lost?")
    return client.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], base_url=base_url)


def facts(events, history):
    """The truth, computed by code: checker verdict, the node with the LOWER token in a two-leader window,
    and the write that a later read should have seen."""
    tokens = {n: int(t) for n, t in re.findall(r"(n\d+) acquired the lease, token (\d+)", " ".join(events))}
    believers = {n for e in events for n in re.findall(r"(n\d+) renew timed out .* still thinks it leads", e)}
    stale = min((n for n in believers if n in tokens), key=tokens.get, default="none")
    lost = stale_reads(history)
    return {"linearizable": "yes" if check_register(history)[0] else "no", "stale_leader": stale,
            "lost_write": f"{lost[0][1]['process']} write {lost[0][1]['value']}" if lost else "none"}


def check(reply, truth):
    claims = dict(re.findall(r"^\s*(linearizable|stale_leader|lost_write)\s*:\s*(.+?)\s*$", reply, re.M | re.I))
    return [(k, claims.get(k, "(missing)"), v, claims.get(k, "").lower() == v.lower()) for k, v in truth.items()]


def main(argv):
    events, history, _ = pt.run(pt.OPS, pt.FAULTS)
    srv, base_url = fake_model_server.start_in_thread() if "--fake" in argv else (None, None)
    try:
        reply = ask_agent(events, history, base_url)
    except OSError as e:  # no local model server running
        print(f"no model server reachable ({e}); start Ollama or run with --fake")
        return 2
    finally:
        if srv:
            srv.shutdown()
            srv.server_close()
    for key, claim, truth, ok in check(reply, facts(events, history)):
        print(f"{key:13} agent: {claim:14} code: {truth:14} {'OK' if ok else 'WRONG'}")
    summary = next((l for l in reply.splitlines() if l.lower().startswith("summary:")), "summary: (none)")
    print("agent prose (unverified):", summary[len("summary:"):].strip())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
