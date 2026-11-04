"""Start/stop N local nodes, each a separate Python process on its own port (macOS/Windows/Linux).
Usage: python lab.py demo 3 | start 3 | status | stop | remote <host> [port]   (env LAB_BASE_PORT, default 8001)"""
import contextlib, json, os, signal, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIDFILE = HERE / ".lab_nodes.json"  # start saves PIDs here so a later `stop` can find them
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never proxy localhost


def health(port, host="127.0.0.1", timeout=0.5):  # health check: a cheap GET proves the node answers
    with OPENER.open(f"http://{host}:{port}/health", timeout=timeout) as r:
        return json.load(r)


def start(ports, wait_s=15.0):
    nodes = []
    for i, port in enumerate(ports, 1):  # process = node: own interpreter, own memory, own port
        proc = subprocess.Popen([sys.executable, str(HERE / "node.py"), "--name", f"node{i}",  # no fork():
                                 "--port", str(port)], stdout=subprocess.DEVNULL)  # works on Windows
        nodes.append({"name": f"node{i}", "port": port, "pid": proc.pid, "proc": proc})
    deadline = time.monotonic() + wait_s
    for n in nodes:  # readiness by polling /health, not by sleeping a guessed time
        while True:
            try:
                health(n["port"]); break
            except OSError:
                if time.monotonic() > deadline:
                    stop(nodes); raise RuntimeError(f"{n['name']} did not start")
                time.sleep(0.05)
    return nodes


def stop(nodes, grace_s=5.0):
    for n in nodes:
        proc = n.get("proc")
        if proc is None:  # `python lab.py stop` from a new shell: only the saved PID is known
            with contextlib.suppress(OSError):  # OSError = already gone (also on Windows)
                os.kill(n["pid"], signal.SIGTERM)  # POSIX: SIGTERM; Windows: TerminateProcess
            continue
        proc.terminate()  # POSIX: SIGTERM; Windows: TerminateProcess (hard stop, no cleanup)
        try:
            proc.wait(timeout=grace_s)  # reap it: the port is free once stop() returns
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait()  # POSIX: SIGKILL; Windows: kill() == terminate()


def main(cmd="demo", arg="3", port="8001"):
    base = int(os.environ.get("LAB_BASE_PORT", "8001"))
    if cmd in ("start", "demo"):
        nodes = start(range(base, base + int(arg)))
        for n in nodes:
            h = health(n["port"])
            print(f"{h['node']} up on port {h['port']} -> /health OK")
        if cmd == "start":
            saved = [{k: v for k, v in n.items() if k != "proc"} for n in nodes]
            return PIDFILE.write_text(json.dumps(saved), encoding="utf-8")
        stop(nodes); print(f"stopped {len(nodes)} nodes")
    elif cmd == "status":
        for n in json.loads(PIDFILE.read_text(encoding="utf-8")):
            print(n["name"], health(n["port"]))
    elif cmd == "stop":
        nodes = json.loads(PIDFILE.read_text(encoding="utf-8")); stop(nodes); PIDFILE.unlink()
        print(f"stopped {len(nodes)} nodes")
    elif cmd == "remote":  # optional LAN step: arg = the other machine's IP address
        print(f"{arg}:{port} ->", health(int(port), host=arg, timeout=2.0))


if __name__ == "__main__":
    main(*sys.argv[1:])
