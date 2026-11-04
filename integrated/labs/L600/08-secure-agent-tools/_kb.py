"""Reuse, don't duplicate: load modules from the source topics' labs by file path (never edited, never copied).

Each module gets a unique name ("kb_<alias>") so labs that share file names (policy.py, try_it.py) cannot clash.
"""
import importlib.util
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
KB = LAB.parents[3]  # kb/integrated/labs/L600/<slug> -> kb/
SOURCES = {
    "schema_check": "ai-agents/labs/L200/08-multi-tool-agent/schema_check.py",     # JSON Schema subset (lesson 8)
    "mcp_server": "ai-agents/labs/L200/10-mcp-server-client/mcp_server.py",         # MCP 2026-07-28 stdio server
    "mcp_client": "ai-agents/labs/L200/10-mcp-server-client/mcp_client.py",         # stdio client
    "fake_model": "shared/local_agent/fake_model_server.py",                        # deterministic fake model
    "tokens": "cryptography/labs/L200/11-tokens/tokens.py",                         # b64u, JWT-style tokens
    "release_sign": "cryptography/labs/L300/14-supply-chain-signing/release_sign.py",  # key_id, digest
    "rego_lite": "application-architecture/labs/L400/19-policy-as-code/rego_lite.py",  # policy as code
}


def load(alias):
    name = f"kb_{alias}"
    if name in sys.modules:
        return sys.modules[name]
    path = KB / SOURCES[alias]
    folder = str(path.parent)
    if folder not in sys.path:
        sys.path.append(folder)  # appended: our own lab modules always win a name clash
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    for alias, rel in SOURCES.items():
        print(f"{alias:13s} {rel} -> {load(alias).__name__}")
