"""Same lesson on a real coordination store: etcd's lease + transaction (CAS) + election API via etcdctl.
Needs an etcd server on 127.0.0.1:2379 (e.g. `podman run -d -p 2379:2379 gcr.io/etcd-development/etcd:v3.7.3
/usr/local/bin/etcd --listen-client-urls http://0.0.0.0:2379 --advertise-client-urls http://127.0.0.1:2379`)
and etcdctl on PATH (or ETCDCTL=/path/to/etcdctl). Run: python etcd_equivalent.py   (pending-ci: run in CI only)."""
import json, os, queue, re, subprocess, sys, threading, time

ETCDCTL = os.environ.get("ETCDCTL", "etcdctl")


def ctl(*args, stdin=None):
    out = subprocess.run([ETCDCTL, *args], input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    if out.returncode:
        sys.exit(f"etcdctl {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def grant(ttl):  # "lease 694d5765fc71500b granted with TTL(5s)"
    return re.search(r"lease (\w+) granted", ctl("lease", "grant", str(ttl))).group(1)


def campaign(name, lease):  # txn = compare-and-swap: create "leader" only if it does not exist yet
    txn = f'create("leader") = "0"\n\nput leader {name} --lease={lease}\n\nget leader\n\n'
    return ctl("txn", stdin=txn).splitlines()[0]  # SUCCESS or FAILURE


def token():  # fencing token = the key's create_revision (grows every time a new holder creates it)
    return int(json.loads(ctl("get", "leader", "-w", "json"))["kvs"][0]["create_revision"])


def lease_demo():
    a = grant(2)
    print("node-a campaign:", campaign("node-a", a), "| token", token())
    print("node-b campaign:", campaign("node-b", grant(30)))
    first = token()
    for _ in range(30):  # node-a sends no keep-alive: its lease expires and etcd deletes the key
        if not ctl("get", "leader", "--print-value-only"):
            break
        time.sleep(0.5)
    print("node-a lease expired -> node-b campaign:", campaign("node-b", grant(30)), "| token", token())
    assert token() > first, "fencing token must grow"


def lines_of(proc):
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l.strip()) for l in proc.stdout], daemon=True).start()
    return q


def wait_for(q, word, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            if q.get(timeout=0.2) == word:
                return True
        except queue.Empty:
            pass
    return False


def election_demo():  # etcdctl elect = the built-in election recipe (lease + key with lowest revision)
    a = subprocess.Popen([ETCDCTL, "elect", "demo-election", "node-a"], stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    qa = lines_of(a)
    assert wait_for(qa, "node-a", 10), "node-a should win"
    b = subprocess.Popen([ETCDCTL, "elect", "demo-election", "node-b"], stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    qb = lines_of(b)
    print("elect: node-a leads; node-b waiting:", not wait_for(qb, "node-b", 2))
    a.terminate()  # SIGTERM: etcdctl resigns (deletes its key) -> the next campaigner wins at once
    print("elect: node-a resigned -> node-b elected:", wait_for(qb, "node-b", 10))
    b.terminate()
    a.wait(10), b.wait(10)


if __name__ == "__main__":
    ctl("del", "leader")
    lease_demo()
    election_demo()
    print("etcd equivalent OK")
