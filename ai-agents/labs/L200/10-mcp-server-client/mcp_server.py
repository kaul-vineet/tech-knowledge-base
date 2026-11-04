"""Tiny MCP server over stdio (JSON-RPC 2.0, one message per line), stdlib only.

Speaks MCP 2026-07-28 (stateless: protocol version in every request's _meta, server/discover)
and, for older clients, the 2025-11-25 initialize handshake ("dual-era"). --legacy-only drops 2026-07-28.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "08-multi-tool-agent"))
from schema_check import validate  # noqa: E402  (lesson 8 validator)

MODERN, LEGACY = "2026-07-28", "2025-11-25"
INFO = {"name": "tiny-mcp", "version": "0.1.0"}
TOOLS = {  # name -> (function, description, inputSchema); fixed order (spec: deterministic tools/list)
    "add": (lambda a, b: a + b, "Add two numbers.", {"type": "object", "properties": {
        "a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"], "additionalProperties": False}),
    "word_count": (lambda text: len(text.split()), "Count the words in a text.", {"type": "object", "properties": {
        "text": {"type": "string", "maxLength": 10000}}, "required": ["text"], "additionalProperties": False}),
}


def call_tool(params):
    name, args = params.get("name"), params.get("arguments") or {}
    if name not in TOOLS:
        raise LookupError(f"Unknown tool: {name}")  # protocol error (-32602)
    fn, _, schema = TOOLS[name]
    problems = validate(args, schema)
    try:
        if problems:
            raise ValueError("invalid arguments: " + "; ".join(problems))
        value = fn(**args)
        return {"content": [{"type": "text", "text": json.dumps(value)}], "structuredContent": {"result": value},
                "isError": False}
    except Exception as exc:  # tool execution error: reported IN the result so the model can self-correct
        return {"content": [{"type": "text", "text": f"error: {exc}"}], "isError": True}


def handle(msg, state, versions):
    method, params = msg.get("method"), msg.get("params") or {}
    if method == "initialize" and LEGACY in versions:  # legacy era: handshake once per stdio process
        state["legacy"] = True
        return {"protocolVersion": LEGACY, "capabilities": {"tools": {}}, "serverInfo": INFO}
    if MODERN not in versions and not state.get("legacy"):
        raise NotImplementedError(method)  # a legacy-only server knows nothing before initialize
    meta = params.get("_meta") or {}
    version = meta.get("io.modelcontextprotocol/protocolVersion")
    if not state.get("legacy"):  # modern era: every request must carry its own version + capabilities
        if version is None or "io.modelcontextprotocol/clientCapabilities" not in meta:
            raise KeyError("missing required _meta fields")
        if version not in versions or version == LEGACY:
            modern = [v for v in versions if v != LEGACY]  # only versions accepted in _meta; 2025-11-25 needs initialize
            raise RuntimeError(json.dumps({"supported": modern, "requested": version}))
    result = {} if state.get("legacy") else {"resultType": "complete", "_meta": {"io.modelcontextprotocol/serverInfo": INFO}}
    if method == "server/discover" and MODERN in versions:
        return {**result, "supportedVersions": [MODERN], "capabilities": {"tools": {}}, "ttlMs": 60000, "cacheScope": "public"}
    if method == "tools/list":
        tools = [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in TOOLS.items()]
        return {**result, "tools": tools, "ttlMs": 60000, "cacheScope": "public"}
    if method == "tools/call":
        return {**result, **call_tool(params)}
    raise NotImplementedError(method)


def serve(versions=(MODERN, LEGACY)):
    versions, state = list(versions), {}
    for line in sys.stdin:  # stdin closed -> loop ends -> process exits (stdio shutdown)
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            if "id" not in msg:
                continue  # notification (e.g. notifications/initialized): never answered
            try:
                reply = {"jsonrpc": "2.0", "id": msg["id"], "result": handle(msg, state, versions)}
            except Exception as exc:
                code = {NotImplementedError: -32601, RuntimeError: -32022}.get(type(exc), -32602)
                data = json.loads(str(exc)) if code == -32022 else None
                text = {-32601: f"Method not found: {exc}", -32022: "Unsupported protocol version"}.get(code, str(exc).strip("'\""))
                reply = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": code, "message": text, **({"data": data} if data else {})}}
        print(json.dumps(reply), flush=True)  # stdout carries ONLY protocol messages; logs go to stderr


if __name__ == "__main__":
    print("tiny-mcp ready on stdio", file=sys.stderr)
    serve((LEGACY,) if "--legacy-only" in sys.argv else (MODERN, LEGACY))
