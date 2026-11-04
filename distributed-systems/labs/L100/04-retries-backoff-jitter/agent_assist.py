"""Agent assist (optional): a LOCAL model summarizes a retry/latency log; code checks every number.
python agent_assist.py --fake   # deterministic fake model server (no download; used by the tests)
python agent_assist.py          # real local model: LOCAL_MODEL_URL (default Ollama http://localhost:11434/v1)
Boundary: code computes the truth and decides; the agent only proposes a summary."""
import math, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import client, fake_model_server  # noqa: E402

MARKER = "[[RETRY-LOG-SUMMARY]]"
TOLERANCE = {"attempts": 0, "errors": 0, "p50_ms": 1.0, "p99_ms": 1.0}  # allowed absolute error


def make_log(seed=7, requests=80, fail_rate=0.25, max_attempts=4):
    """Seeded retry log: 503s are fast failures and get retried; latencies are lognormal ~40 ms."""
    rng, lines = random.Random(seed), []
    for req in range(1, requests + 1):
        for attempt in range(1, max_attempts + 1):
            status = 503 if rng.random() < fail_rate else 200
            ms = rng.lognormvariate(math.log(40), 0.6) * (0.25 if status == 503 else 1)
            lines.append(f"req={req:02d} attempt={attempt} status={status} latency_ms={ms:.1f}")
            if status == 200:
                break
    return lines


def true_stats(lines):  # the truth comes from code, never from the model
    rows = [dict(kv.split("=") for kv in line.split()) for line in lines]
    lat = sorted(float(r["latency_ms"]) for r in rows)
    pct = lambda p: lat[max(0, math.ceil(p / 100 * len(lat)) - 1)]  # nearest-rank percentile
    return {"attempts": len(rows), "errors": sum(r["status"] != "200" for r in rows),
            "p50_ms": pct(50), "p99_ms": pct(99)}


def ask_agent(lines, base_url=None):
    system = ("You summarize service logs for an on-call engineer. Reply with exactly these lines: "
              "attempts=<n>, errors=<n>, p50_ms=<n>, p99_ms=<n>, then one line starting 'summary:'.")
    user = (f"{MARKER} Summarize this retry/latency log. errors = attempts whose status is not 200; "
            "p50/p99 = latency percentiles over all attempts.\n<log>\n" + "\n".join(lines) + "\n</log>")
    return client.chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
                       base_url=base_url)


def check(reply, truth):
    """Parse 'name=value' lines the agent claimed and compare each with the computed truth."""
    claimed = {k: float(v) for k, v in re.findall(r"^\s*(\w+)\s*[=:]\s*(-?[\d.]+)", reply, re.M)}
    verdict = {}
    for name, tol in TOLERANCE.items():
        if name not in claimed:
            verdict[name] = (None, "MISSING")
        else:
            verdict[name] = (claimed[name], "ok" if abs(claimed[name] - truth[name]) <= tol else "WRONG")
    return verdict


def main(argv):
    srv, base_url = fake_model_server.start_in_thread() if "--fake" in argv else (None, None)
    lines = make_log()
    truth = true_stats(lines)
    try:
        reply = ask_agent(lines, base_url)
    except OSError as e:  # no local model server running
        print(f"no model server reachable ({e}); start Ollama or run with --fake")
        return 2
    finally:
        if srv:
            srv.shutdown()
    print(f"log: {len(lines)} attempts from 80 requests (seeded, seed 7)")
    print(f"{'field':<9}{'agent':>9}{'code':>9}  verdict")
    verdict = check(reply, truth)
    for name, (claimed, v) in verdict.items():
        print(f"{name:<9}{'-' if claimed is None else f'{claimed:g}':>9}{truth[name]:>9}  {v}")
    summary = next((l for l in reply.splitlines() if l.lower().startswith("summary:")), "summary: (none)")
    print("agent prose (unverified):", summary[len("summary:"):].strip())
    wrong = [n for n, (_, v) in verdict.items() if v != "ok"]
    print("flagged:", ", ".join(wrong) if wrong else "none", "-> report the code's numbers, not the agent's")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
