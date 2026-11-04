# 10 – Build an MCP server and client

An MCP server is a process that answers tools/list and tools/call over newline-delimited JSON-RPC; since 2026-07-28 every request carries its own protocol version.

## Run (validated – no model server needed)
```bash
python mcp_client.py
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"1900-01-01","io.modelcontextprotocol/clientCapabilities":{}}}}' | python mcp_server.py
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python mcp_client.py
'{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"1900-01-01","io.modelcontextprotocol/clientCapabilities":{}}}}' | python mcp_server.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
mcp_server.py: era=modern version=2026-07-28
  tools: ['add', 'word_count']
  add(2, 3): 5
  add('two', 3): isError = True | error: invalid arguments: $.a: expected number, got str
  rm_rf: protocol error -32602 Unknown tool: rm_rf
mcp_server.py --legacy-only: era=legacy version=2025-11-25
  tools: ['add', 'word_count']
  add(2, 3): 5
  add('two', 3): isError = True | error: invalid arguments: $.a: expected number, got str
  rm_rf: protocol error -32602 Unknown tool: rm_rf
```
Tests: `Ran 14 tests ... OK (skipped=3)`.

## Build task
Add a divide(a, b) tool; dividing by zero must come back as a tool execution error (isError: true), never as a JSON-RPC error.

Hints:
- Add an entry to mcp_server.TOOLS: (function, description, inputSchema).
- call_tool already turns exceptions into isError results.
- Run the server through a small module that imports mcp_server and calls serve().

Solution: `solution/mcp_server_divide.py` · proof: `python -m unittest -v test_build_task`

## Equivalents
- Official MCP Python SDK 2.3.0: MCPServer + @mcp.tool(), mcp.run() on stdio; Client(StdioServerParameters(...)) (sdk_server.py, test_sdk_equivalent.py, pending-ci)
- MCP TypeScript SDK: same protocol for Node 24 hosts and servers
- llama.cpp llama-server --mcp-servers-config (experimental): a local host that launches stdio MCP servers
- MCP Inspector >= 2.12.0 (npx @modelcontextprotocol/inspector): interactive client for testing a server - see `documentation/LEARNING-TOOLS.md`

## Optional steps (not run in the sandbox)
**official Python SDK as client and server** – The SDK client connects to the SDK server and to YOUR server (both eras) - an interoperability check.
```bash
python -m pip install "mcp==2.3.0"
python -m unittest -v test_sdk_equivalent
```
```powershell
python -m pip install "mcp==2.3.0"
python -m unittest -v test_sdk_equivalent
```
Expected: 3 tests ok; versions 2026-07-28, 2026-07-28, 2025-11-25

**give the tools to a local model via llama-server (experimental)** – Experimental in llama.cpp; see the [llama-server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md). llama-server launches stdio MCP servers listed in a Cursor-style JSON file and exposes their tools as <server>_<tool>. Use absolute paths.
```bash
echo '{"mcpServers": {"tiny": {"command": "python3", "args": ["'$PWD'/mcp_server.py"]}}}' > mcp.json
llama-server -m model.gguf --mcp-servers-config mcp.json
```
```powershell
'{"mcpServers": {"tiny": {"command": "python", "args": ["C:/path/to/mcp_server.py"]}}}' | Set-Content mcp.json
llama-server -m model.gguf --mcp-servers-config mcp.json
```
Expected: GET /tools on llama-server lists tiny_add and tiny_word_count

## Troubleshooting
| Symptom | Action |
|---|---|
| Client waits until timeout | The server buffered output: print(..., flush=True), one message per line. |
| Every request returns -32602 missing _meta | A 2026-07-28 server needs protocolVersion and clientCapabilities in every request's _meta. |
| Server process left running | Close stdin first; kill only after a wait (TerminateProcess on Windows, SIGKILL on POSIX). |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_10` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Make the server print 'server starting...' to stdout before serving. | first stdout line 'server starting...' -> JSONDecodeError: Expecting value - one stray print breaks the protocol. |
| Make the client send protocolVersion '2025-06-18' in _meta. | {'code': -32022, 'message': 'Unsupported protocol version', 'data': {'supported': ['2026-07-28'], 'requested': '2025-06-18'}} - a modern error, so a client retries with a listed version; 2025-11-25 is not listed because it is reachable only through initialize. |
