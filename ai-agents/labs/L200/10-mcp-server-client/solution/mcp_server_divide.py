"""Build-task solution (lesson 10): a divide tool; b = 0 must be a TOOL error (isError: true), not a protocol error."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import mcp_server  # noqa: E402

mcp_server.TOOLS["divide"] = (lambda a, b: a / b, "Divide a by b.", {  # ZeroDivisionError -> isError result
    "type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
    "required": ["a", "b"], "additionalProperties": False})

if __name__ == "__main__":
    mcp_server.serve()
