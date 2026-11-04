import json
import socket
import subprocess
import sys
import unittest

import lab


def free_ports(n):
    socks = [socket.socket() for _ in range(n)]
    for s in socks:
        s.bind(("127.0.0.1", 0))
    ports = [s.getsockname()[1] for s in socks]
    for s in socks:
        s.close()
    return ports


class TestLocalLab(unittest.TestCase):
    def test_start_health_stop(self):
        ports = free_ports(3)
        nodes = lab.start(ports)
        try:
            names = [lab.health(p)["node"] for p in ports]
            self.assertEqual(names, ["node1", "node2", "node3"])
            self.assertEqual(len({n["pid"] for n in nodes}), 3)  # 3 separate processes
        finally:
            lab.stop(nodes)
        self.assertTrue(all(n["proc"].returncode is not None for n in nodes))  # reaped, no zombies
        for p in ports:
            with self.assertRaises(OSError):
                lab.health(p)

    def test_stop_by_saved_pid(self):  # the `python lab.py stop` path: no Popen handle, PID only
        nodes = lab.start(free_ports(1))
        saved = json.loads(json.dumps([{k: v for k, v in n.items() if k != "proc"} for n in nodes]))
        lab.stop(saved)
        self.assertIsNotNone(nodes[0]["proc"].wait(timeout=10))
        lab.stop(saved)  # stopping twice must not raise (process already gone)

    def test_second_bind_on_same_port_fails(self):  # exclusive bind on every OS (Windows too)
        nodes = lab.start(free_ports(1))
        try:
            dup = subprocess.run([sys.executable, str(lab.HERE / "node.py"), "--port",
                                  str(nodes[0]["port"])], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            self.assertNotEqual(dup.returncode, 0)
            self.assertIn("OSError", dup.stderr)
            self.assertEqual(lab.health(nodes[0]["port"])["node"], "node1")
        finally:
            lab.stop(nodes)

    def test_remote_health_by_host(self):  # LAN step code path, here against loopback
        nodes = lab.start(free_ports(1))
        try:
            self.assertEqual(lab.health(nodes[0]["port"], host="127.0.0.1", timeout=2.0)["node"], "node1")
        finally:
            lab.stop(nodes)


if __name__ == "__main__":
    unittest.main()
