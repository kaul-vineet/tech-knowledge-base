"""Agent assist (optional): a LOCAL model proposes a replica layout; code validates every rule and decides.
python agent_assist.py --fake   # deterministic fake model server (no download; used by the tests)
python agent_assist.py          # real local model: LOCAL_MODEL_URL (default Ollama http://localhost:11434/v1)
Boundary: the agent only proposes; the checker below accepts or rejects; a rejected layout is never applied."""
import math, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import client, fake_model_server  # noqa: E402

MARKER = "[[SHARD-LAYOUT]]"
ZONES = {"n1": "a", "n2": "a", "n3": "b", "n4": "b", "n5": "c", "n6": "c"}
SHARDS, RF = 8, 3
CAP = math.ceil(SHARDS * RF / len(ZONES))  # 24 replicas over 6 nodes -> at most 4 per node


def ask_agent(base_url=None):
    system = ("You plan replica placement for a sharded store. Reply with exactly one line per shard, "
              "formatted 'S<i>: node,node,node', then one line starting 'summary:'.")
    nodes = " ".join(f"{n}@{z}" for n, z in ZONES.items())
    user = (f"{MARKER} Place {SHARDS} shards S0-S{SHARDS - 1}, {RF} replicas each, on nodes: {nodes} "
            f"(the part after @ is the zone). Rules: {RF} different nodes in {RF} different zones per shard; at most {CAP} replicas per node.")
    return client.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], base_url=base_url)


def parse(reply):
    return {int(s): [n.strip() for n in nodes.split(",") if n.strip()]
            for s, nodes in re.findall(r"^\s*S(\d+)\s*:\s*([\w ,]+)$", reply, re.M)}


def check(layout):
    """Returns a list of rule violations; empty list = the layout may be applied."""
    problems = [f"S{s}: missing" for s in range(SHARDS) if s not in layout]
    for s, nodes in sorted(layout.items()):
        if s >= SHARDS or len(nodes) != RF or len(set(nodes)) != RF:
            problems.append(f"S{s}: needs {RF} different nodes, got {nodes}")
        elif unknown := [n for n in nodes if n not in ZONES]:
            problems.append(f"S{s}: unknown node(s) {unknown}")
        elif len({ZONES[n] for n in nodes}) != RF:
            problems.append(f"S{s}: zones {[ZONES[n] for n in nodes]} -> two replicas share a zone")
    load = Counter(n for nodes in layout.values() for n in nodes)
    problems += [f"{n}: {c} replicas > capacity {CAP}" for n, c in sorted(load.items()) if c > CAP]
    return problems


def main(argv):
    srv, base_url = fake_model_server.start_in_thread() if "--fake" in argv else (None, None)
    try:
        reply = ask_agent(base_url)
    except OSError as e:  # no local model server running
        print(f"no model server reachable ({e}); start Ollama or run with --fake")
        return 2
    finally:
        if srv:
            srv.shutdown()
    layout = parse(reply)
    print("agent proposal:", " | ".join(f"S{s}: {','.join(n)}" for s, n in sorted(layout.items())))
    summary = next((l for l in reply.splitlines() if l.lower().startswith("summary:")), "summary: (none)")
    print("agent prose (unverified):", summary[len("summary:"):].strip())
    problems = check(layout)
    print("checker:", "PASS - layout may be applied" if not problems else "REJECTED")
    for p in problems:
        print("  -", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
