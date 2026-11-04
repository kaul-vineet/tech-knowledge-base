"""tryIt experiments for lesson 1 (python try_it.py). Prints what actually happens."""
import socket, subprocess, sys

import lab


def free_ports(n):
    socks = [socket.socket() for _ in range(n)]
    for s in socks:
        s.bind(("127.0.0.1", 0))
    ports = [s.getsockname()[1] for s in socks]
    for s in socks:
        s.close()
    return ports


# tryIt 1: start a second node on a port that node1 already uses
nodes = lab.start(free_ports(1))
try:
    dup = subprocess.run([sys.executable, str(lab.HERE / "node.py"), "--name", "dup", "--port",
                          str(nodes[0]["port"])], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
    print(f"tryIt 1: second node exit code {dup.returncode}: {dup.stderr.strip().splitlines()[-1]}")
except subprocess.TimeoutExpired:  # would mean the 2nd bind succeeded (port shared!)
    print("tryIt 1: second node is STILL RUNNING on the same port (bind was not exclusive)")
print(f"         node1 still healthy: {lab.health(nodes[0]['port'])['node'] == 'node1'}")
lab.stop(nodes)

# tryIt 2: stop only node2 (terminate + wait), then health-check all three
nodes = lab.start(free_ports(3))
lab.stop([nodes[1]])
results = []
for n in nodes:
    try:
        results.append(f"{n['name']}=OK" if lab.health(n["port"]) else "?")
    except OSError as e:
        results.append(f"{n['name']}={type(getattr(e, 'reason', e)).__name__}")
print("tryIt 2:", ", ".join(results))
lab.stop(nodes)
