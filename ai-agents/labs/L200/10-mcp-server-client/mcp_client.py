"""Tiny MCP client: launch a server as a subprocess, detect its era, list and call tools over stdio."""
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

MODERN, LEGACY = "2026-07-28", "2025-11-25"
CLIENT = {"name": "tiny-client", "version": "0.1.0"}


class StdioClient:
    def __init__(self, server_args, timeout=10):
        self.proc = subprocess.Popen([sys.executable, *server_args], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1)
        self.lines, self.timeout, self.next_id, self.version = queue.Queue(), timeout, 0, None
        threading.Thread(target=lambda: [self.lines.put(ln) for ln in self.proc.stdout], daemon=True).start()

    def _send(self, msg):
        self.proc.stdin.write(json.dumps(msg) + "\n")  # one JSON-RPC message per line, no embedded newlines
        self.proc.stdin.flush()

    def request(self, method, params=None):
        self.next_id += 1
        params = dict(params or {})
        if self.version != LEGACY:  # modern era: version + capabilities travel with EVERY request
            params["_meta"] = {"io.modelcontextprotocol/protocolVersion": self.version or MODERN,
                               "io.modelcontextprotocol/clientCapabilities": {}, "io.modelcontextprotocol/clientInfo": CLIENT}
        self._send({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params})
        reply = json.loads(self.lines.get(timeout=self.timeout))  # timeout: never wait forever on a server
        if "error" in reply:
            raise RuntimeError(reply["error"])
        return reply["result"]

    def connect(self):
        """Probe with server/discover (modern); any non-modern error -> legacy initialize handshake."""
        try:
            self.version = MODERN
            return {"era": "modern", **self.request("server/discover")}
        except RuntimeError as err:
            if err.args[0]["code"] == -32022:  # modern server, other version: pick one it supports
                self.version = err.args[0]["data"]["supported"][0]
                return {"era": "modern", "supportedVersions": err.args[0]["data"]["supported"]}
        except queue.Empty:
            pass  # no answer within the timeout also means "legacy server"
        self.version = LEGACY
        init = self.request("initialize", {"protocolVersion": LEGACY, "capabilities": {}, "clientInfo": CLIENT})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})  # notification: no id, no reply
        return {"era": "legacy", **init}

    def list_tools(self):
        return self.request("tools/list")["tools"]

    def call_tool(self, name, arguments):
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def close(self):
        self.proc.stdin.close()  # graceful stdio shutdown: close stdin, wait, then force
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()  # TerminateProcess on Windows, SIGKILL on POSIX


def as_chat_tools(mcp_tools):
    """Bridge: MCP inputSchema is already JSON Schema, so it becomes chat-completions `parameters` unchanged."""
    return [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                              "parameters": t["inputSchema"]}} for t in mcp_tools]


if __name__ == "__main__":
    server = str(Path(__file__).resolve().parent / "mcp_server.py")
    for args in ([server], [server, "--legacy-only"]):
        client = StdioClient(args)
        hello = client.connect()
        print(f"{' '.join(Path(a).name for a in args)}: era={hello['era']} version={client.version}")
        print("  tools:", [t["name"] for t in client.list_tools()])
        print("  add(2, 3):", client.call_tool("add", {"a": 2, "b": 3})["content"][0]["text"])
        bad = client.call_tool("add", {"a": "two", "b": 3})
        print("  add('two', 3): isError =", bad["isError"], "|", bad["content"][0]["text"])
        try:
            client.call_tool("rm_rf", {})
        except RuntimeError as err:
            print("  rm_rf: protocol error", err.args[0]["code"], err.args[0]["message"])
        client.close()
