"""Build task (lesson 10): add a divide tool; a zero divisor is a tool error (isError), not a protocol error."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mcp_client import StdioClient  # noqa: E402


class BuildTask(unittest.TestCase):
    def test_divide(self):
        client = StdioClient([os.path.join(HERE, "solution", "mcp_server_divide.py")])
        try:
            client.connect()
            self.assertEqual([t["name"] for t in client.list_tools()], ["add", "word_count", "divide"])
            self.assertEqual(client.call_tool("divide", {"a": 6, "b": 3})["content"][0]["text"], "2.0")
            zero = client.call_tool("divide", {"a": 1, "b": 0})
            self.assertEqual((zero["isError"], zero["content"][0]["text"]), (True, "error: division by zero"))
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
