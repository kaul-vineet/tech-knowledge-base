"""Computes every worked-example value used in content/concepts/L200/*.md (run: python research/L200_concept_examples.py).

Uses numpy, requests, the lab code and the fake server, so the numbers match what learners see in the L200 labs.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L200 = os.path.join(HERE, "..", "labs", "L200")
sys.path.insert(0, os.path.join(HERE, "..", "labs", "L100", "01-setup"))
for lab in ("07-rag-answers", "08-multi-tool-agent", "09-state-memory", "10-mcp-server-client", "11-guardrails"):
    sys.path.insert(0, os.path.join(L200, lab))
from fake_model_server import start_in_thread  # noqa: E402
import rag  # noqa: E402
import multi_tool_agent  # noqa: E402
import memory_agent  # noqa: E402
import guarded_agent  # noqa: E402

server, base = start_in_thread()

print("== 07 retrieval ==")
chunks = rag.load_chunks()
vectors = rag.embed([t for _, t in chunks], base)
print("chunks:", len(chunks), "dims:", vectors.shape[1])
for q in ["Which tools need human approval?", "What is the capital of France?"]:
    print(q, [(c, s) for c, _, s in rag.search(q, chunks, vectors, 2, base)])
a, b = np.array([0.6, 0.8]), np.array([1.0, 0.0])
print("cosine([0.6,0.8],[1,0]) =", float(a @ b))

print("== 08 validation ==")
print(multi_tool_agent.execute("get_weather", '{"city": "Paris", "unit": "kelvin"}'))
print(multi_tool_agent.execute("search_docs", '{"query": "context window", "top_k": 50}'))

print("== 09 budget ==")
chat = memory_agent.Chat(memory_agent.MemoryStore(), budget=60, base_url=base, model="fake-model")
for text in ["Remember that the staging database is on port 5433.", "Thanks. Now tell me a fun fact about otters.",
             "And one about penguins please, keep it short."]:
    before = memory_agent.count_tokens(chat.messages + [{"role": "user", "content": text}])
    chat.send(text)
    print(f"tokens before call={before} after={memory_agent.count_tokens(chat.messages)} "
          f"messages={len(chat.messages)} summaries={chat.summaries}")
print("summary line:", chat.messages[0]["content"].splitlines()[-1])
chat.memory.close()

print("== 10 MCP wire ==")
meta = {"io.modelcontextprotocol/protocolVersion": "1900-01-01", "io.modelcontextprotocol/clientCapabilities": {}}
line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {"_meta": meta}})
out = subprocess.run([sys.executable, os.path.join(L200, "10-mcp-server-client", "mcp_server.py")], input=line + "\n",
                     capture_output=True, encoding="utf-8", timeout=20).stdout.strip()
print(out)

print("== 11 guardrails ==")
for guarded in (False, True):
    guarded_agent.OUTBOX.clear()
    s = guarded_agent.Session({"search_docs", "send_email"}, guarded=guarded)
    s.run('Search docs for "vendor portal deploys".', base_url=base, model="fake-model")
    print(f"guarded={guarded} emails sent={len(guarded_agent.OUTBOX)} log={s.log[0][:40]}")
server.shutdown()
