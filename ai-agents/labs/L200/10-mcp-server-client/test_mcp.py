import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mcp_client import StdioClient, as_chat_tools  # noqa: E402

SERVER = os.path.join(HERE, "mcp_server.py")
META = {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}}


def raw(*lines, legacy_only=False):
    """Send raw JSON-RPC lines to a fresh server; return its stdout lines as dicts."""
    args = [sys.executable, SERVER] + (["--legacy-only"] if legacy_only else [])
    out = subprocess.run(args, input="\n".join(lines) + "\n", capture_output=True, encoding="utf-8", timeout=20).stdout
    return [json.loads(ln) for ln in out.splitlines()]


class McpServerWire(unittest.TestCase):
    def test_modern_request_needs_meta(self):
        r = raw(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}))[0]
        self.assertEqual(r["error"]["code"], -32602)

    def test_unsupported_version_lists_supported(self):
        meta = {**META, "io.modelcontextprotocol/protocolVersion": "1900-01-01"}
        r = raw(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta": meta}}))[0]
        self.assertEqual(r["error"]["code"], -32022)
        self.assertEqual(r["error"]["data"], {"supported": ["2026-07-28"], "requested": "1900-01-01"})

    def test_notifications_and_parse_errors(self):
        out = raw('{"jsonrpc": "2.0", "method": "notifications/initialized"}', "not json")
        self.assertEqual(len(out), 1)  # the notification got no reply
        self.assertEqual((out[0]["id"], out[0]["error"]["code"]), (None, -32700))

    def test_results_carry_result_type(self):
        r = raw(json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {"_meta": META}}))[0]
        self.assertEqual((r["id"], r["result"]["resultType"], r["result"]["cacheScope"]), (7, "complete", "public"))


class McpClientEndToEnd(unittest.TestCase):
    def check_session(self, args, era, version):
        client = StdioClient(args)
        try:
            self.assertEqual(client.connect()["era"], era)
            self.assertEqual(client.version, version)
            self.assertEqual([t["name"] for t in client.list_tools()], ["add", "word_count"])
            self.assertEqual(client.call_tool("add", {"a": 2, "b": 3})["content"][0]["text"], "5")
            self.assertEqual(client.call_tool("word_count", {"text": "one two three"})["structuredContent"], {"result": 3})
            bad = client.call_tool("add", {"a": "two", "b": 3})
            self.assertTrue(bad["isError"])  # tool execution error: inside the result
            with self.assertRaises(RuntimeError) as ctx:
                client.call_tool("rm_rf", {})
            self.assertEqual(ctx.exception.args[0]["code"], -32602)  # protocol error: JSON-RPC error
        finally:
            client.close()
        self.assertIsNotNone(client.proc.returncode)  # server exited after stdin closed

    def test_modern_server(self):
        self.check_session([SERVER], "modern", "2026-07-28")

    def test_legacy_fallback(self):
        self.check_session([SERVER, "--legacy-only"], "legacy", "2025-11-25")

    def test_bridge_to_chat_tools(self):
        client = StdioClient([SERVER])
        client.connect()
        spec = as_chat_tools(client.list_tools())[0]
        client.close()
        self.assertEqual(spec["function"]["parameters"]["required"], ["a", "b"])

    def test_cli_runs(self):
        out = subprocess.run([sys.executable, "mcp_client.py"], cwd=HERE, capture_output=True,
                             encoding="utf-8", check=True, timeout=60).stdout
        self.assertIn("mcp_server.py: era=modern version=2026-07-28", out)
        self.assertIn("mcp_server.py --legacy-only: era=legacy version=2025-11-25", out)


if __name__ == "__main__":
    unittest.main()
