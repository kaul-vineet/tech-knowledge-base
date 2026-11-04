**Concept: MCP – one protocol between agents and tools**

## Why it matters
Every agent framework used to wrap tools in its own format. The Model Context Protocol (MCP) defines one JSON-RPC 2.0 interface, so a tool server written once works with any MCP host – including llama.cpp's `llama-server`, which can launch stdio MCP servers itself (experimental).

## Mental model
A USB port for tools: the host's client plugs into a server, asks "what can you do?" (`tools/list`) and then "do this" (`tools/call`). Over stdio the plug is a subprocess: one JSON message per line on stdin/stdout, logs on stderr.

```
client ──spawn──► server (stdin/stdout, newline-delimited JSON-RPC)
  server/discover  ─►  supportedVersions ["2026-07-28"]      (modern)
     └ other error ─►  initialize + notifications/initialized (legacy fallback)
  tools/list ─► tools[] with inputSchema   tools/call ─► content[], isError
```

## How it works
1. **Version per request.** In MCP 2026-07-28 the `initialize` handshake is gone: every request carries `_meta.io.modelcontextprotocol/protocolVersion` and client capabilities. Worked example: a request with version `1900-01-01` returns error `-32022` with `{"supported": ["2026-07-28"], "requested": "1900-01-01"}`. → see lab step 2
2. **Discover, then fall back.** A dual-era client sends `server/discover`; any error other than a recognised modern one means a legacy server, so it falls back to `initialize` (2025-11-25) and sends the `notifications/initialized` notification, which gets no reply. → see lab step 1
3. **Tools are JSON Schema.** `inputSchema` maps unchanged to chat-completions `parameters`, so an agent can offer MCP tools to any model. → see lab step 3
4. **Two kinds of error.** Unknown tool or malformed request → JSON-RPC error (`-32602`). Bad arguments or a failing tool → a normal result with `isError: true`, which the model can read and fix. → see lab step 3
5. **stdout is sacred.** Anything that is not a protocol message on stdout breaks the client; close stdin to shut the server down. → see lab step 3

## Trade-offs
| Use when | Avoid when |
|---|---|
| Tools are shared by several agents or hosts | One script with one tool – a local function is simpler |
| Tool code needs its own process or language | Calls are latency-critical inside one process |
| You want the official SDKs' validation and transports | You cannot vet the server you are launching |

## Common mistakes
- Printing logs to stdout.
- Returning tool failures as protocol errors, so the model never sees them.
- Building against the 2025 handshake only; current clients probe `server/discover` first.
