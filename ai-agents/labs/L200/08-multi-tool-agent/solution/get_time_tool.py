"""Build-task solution (lesson 8): register a 4th tool, get_time, with a no-parameter schema."""
from datetime import datetime, timezone

import multi_tool_agent as agent


def get_time():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# empty properties + additionalProperties: false = "accepts only {}" (MCP's recommended no-parameter schema)
agent.REGISTRY["get_time"] = agent.tool(get_time, "Current UTC date and time in ISO 8601.", {})
