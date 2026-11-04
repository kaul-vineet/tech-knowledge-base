"""Try it (lesson 10): two small changes. Run: python -m unittest -v test_try_it_10"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcp_client  # noqa: E402

SERVER = os.path.join(HERE, "mcp_server.py")


class TryIt(unittest.TestCase):
    def test_1_print_to_stdout_breaks_the_protocol(self):
        # change: the server prints a log line to stdout instead of stderr
        code = ("import runpy, sys; print('server starting...'); sys.argv = [sys.argv[1]]; "
                "runpy.run_path(sys.argv[0], run_name='__main__')")
        msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {
            "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}}}})
        out = subprocess.run([sys.executable, "-c", code, SERVER], input=msg + "\n", capture_output=True,
                             encoding="utf-8", timeout=20).stdout.splitlines()
        try:
            json.loads(out[0])
            observed = "first stdout line parsed"
        except json.JSONDecodeError as exc:
            observed = f"first stdout line {out[0]!r} -> JSONDecodeError: {exc.msg}"
        print("\nobserved:", observed)
        self.assertIn("JSONDecodeError", observed)

    def test_2_client_pins_an_old_version(self):
        # change: the client sends protocolVersion "2025-06-18" in _meta (a version this server does not speak)
        client = mcp_client.StdioClient([SERVER])
        client.version = "2025-06-18"
        try:
            client.request("tools/list")
        except RuntimeError as err:
            observed = err.args[0]
        finally:
            client.close()
        print("\nobserved:", observed)
        self.assertEqual(observed["code"], -32022)


if __name__ == "__main__":
    unittest.main(verbosity=2)
