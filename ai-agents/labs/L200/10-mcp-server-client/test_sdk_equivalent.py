"""Equivalent check (pending-ci): the official MCP Python SDK (mcp==2.3.0) as client and as server.

1. SDK client  -> SDK server (sdk_server.py)
2. SDK client  -> OUR stdio server, modern era and legacy-only (interoperability)
Skipped when the `mcp` package is not installed.
"""
import asyncio
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HAVE_SDK = importlib.util.find_spec("mcp") is not None


async def session(*args):
    from mcp import Client
    try:
        from mcp.client.stdio import StdioServerParameters
    except ImportError:  # older layout
        from mcp import StdioServerParameters
    async with Client(StdioServerParameters(command=sys.executable, args=list(args))) as client:  # mode="auto"
        tools = await client.list_tools()
        result = await client.call_tool("add", {"a": 2, "b": 3})
        return client.protocol_version, [t.name for t in tools.tools], result


@unittest.skipUnless(HAVE_SDK, "official SDK not installed (CI installs mcp==2.3.0)")
class SdkEquivalent(unittest.TestCase):
    def check(self, args, version):
        got_version, names, result = asyncio.run(session(*args))
        print(f"\nobserved: {os.path.basename(args[0])} {args[1:]} -> {got_version} {names} {result.content[0].text}")
        self.assertEqual(got_version, version)
        self.assertEqual(names, ["add", "word_count"])
        self.assertFalse(result.is_error)
        self.assertIn(result.content[0].text, ("5", "5.0"))

    def test_sdk_client_sdk_server(self):
        self.check([os.path.join(HERE, "sdk_server.py")], "2026-07-28")

    def test_sdk_client_our_server(self):
        self.check([os.path.join(HERE, "mcp_server.py")], "2026-07-28")

    def test_sdk_client_our_legacy_server(self):
        self.check([os.path.join(HERE, "mcp_server.py"), "--legacy-only"], "2025-11-25")


if __name__ == "__main__":
    unittest.main(verbosity=2)
