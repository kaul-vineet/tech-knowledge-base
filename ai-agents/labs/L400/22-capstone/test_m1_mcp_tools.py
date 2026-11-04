"""Milestone 1: read-only ops tools over MCP (lesson 10's server, new tool table)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import triage  # noqa: E402


class M1McpTools(unittest.TestCase):
    def test_tools_are_read_only_and_validated(self):
        mcp = triage.start_mcp()
        try:
            names = [t["name"] for t in mcp.list_tools()]
            metrics = mcp.call_tool("get_metrics", {"service": "checkout"})["structuredContent"]["result"]
            bad = mcp.call_tool("get_metrics", {"service": "billing-db"})
        finally:
            mcp.close()
        self.assertEqual(names, ["get_metrics", "get_recent_logs", "get_last_deploy"])  # no side-effecting tool
        self.assertEqual(metrics, {"error_rate": 7.5, "p99_ms": 2300, "users_affected_pct": 12, "burn_rate": 16})
        self.assertTrue(bad["isError"])  # schema enum: unknown service is refused by the server


if __name__ == "__main__":
    unittest.main()
