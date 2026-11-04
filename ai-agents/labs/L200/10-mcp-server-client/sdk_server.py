"""Equivalent (pending-ci): the same two tools with the official MCP Python SDK (pip install mcp==2.3.0).

The SDK builds each inputSchema from the type hints and speaks stdio when run directly.
"""
from mcp.server import MCPServer

mcp = MCPServer("tiny-mcp-sdk")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def word_count(text: str) -> int:
    """Count the words in a text."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run()  # transport defaults to "stdio"
