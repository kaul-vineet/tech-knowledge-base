"""Read-only ops tools over MCP stdio - lesson 10's server with a different tool table (imported, not copied).

Tools: get_metrics, get_recent_logs, get_last_deploy for a service, read from CAPSTONE_INCIDENTS (JSON fixture).
Side-effecting actions are NOT MCP tools here: they go through the durable, approval-gated workflow.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "L200" / "10-mcp-server-client"))
import mcp_server  # noqa: E402

FIXTURE = Path(os.environ.get("CAPSTONE_INCIDENTS", HERE / "fixtures" / "incidents.json"))
BY_SERVICE = {i["service"]: i for i in json.loads(FIXTURE.read_text(encoding="utf-8"))}
SERVICE = {"type": "object", "properties": {"service": {"type": "string", "enum": sorted(BY_SERVICE)}},
           "required": ["service"], "additionalProperties": False}
mcp_server.INFO = {"name": "ops-mcp", "version": "0.1.0"}
mcp_server.TOOLS = {
    "get_metrics": (lambda service: BY_SERVICE[service]["metrics"], "Current error rate, p99, users affected, burn rate.", SERVICE),
    "get_recent_logs": (lambda service: BY_SERVICE[service]["logs"], "The last log lines of a service.", SERVICE),
    "get_last_deploy": (lambda service: {"age_min": BY_SERVICE[service]["deploy_age_min"]}, "Minutes since the last deploy.", SERVICE),
}

if __name__ == "__main__":
    print("ops-mcp ready on stdio", file=sys.stderr)
    mcp_server.serve()
