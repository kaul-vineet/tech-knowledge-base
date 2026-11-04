"""Conversation state, summarise-to-fit a token budget, and explicit long-term memory in SQLite."""
import json
import os
import sqlite3
from pathlib import Path

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
TOOLS = [{"type": "function", "function": {"name": n, "description": d, "parameters": {
    "type": "object", "properties": {k: {"type": "string", "maxLength": 300}}, "required": [k],
    "additionalProperties": False}}} for n, d, k in [
    ("save_memory", "Store a fact the user explicitly asked you to remember.", "note"),
    ("recall_memory", "Look up stored facts by keyword.", "query")]]


class MemoryStore:
    """Long-term memory = rows in a SQLite file; survives restarts, unlike the message list."""
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, note TEXT NOT NULL)")

    def save(self, note):
        with self.db:  # commits on success
            return f"saved note {self.db.execute('INSERT INTO notes (note) VALUES (?)', (note,)).lastrowid}"

    def recall(self, query, limit=3):
        words = [w for w in query.lower().split() if len(w) > 2] or [query.lower()]
        where = " OR ".join("lower(note) LIKE ?" for _ in words)  # placeholders only: no SQL injection
        rows = self.db.execute(f"SELECT id, note FROM notes WHERE {where} ORDER BY id DESC LIMIT ?",
                               [f"%{w}%" for w in words] + [limit]).fetchall()
        return "; ".join(f"{i}: {n}" for i, n in rows) or "no matching notes"

    def close(self):
        self.db.close()


def count_tokens(messages):
    # budget estimate = words (the fake server counts words too); real tokenizers differ -> compare usage.prompt_tokens
    return sum(len((m.get("content") or "").split()) for m in messages)


class Chat:
    def __init__(self, memory, budget=60, keep_last=2, base_url=BASE_URL, model=MODEL):
        self.messages = [{"role": "system", "content": "You are a helpful assistant with a memory tool."}]
        self.memory, self.budget, self.keep_last = memory, budget, keep_last
        self.base_url, self.model, self.summaries = base_url, model, 0

    def _post(self, messages, tools=None):
        body = {"model": self.model, "messages": messages, "temperature": 0, **({"tools": tools} if tools else {})}
        return requests.post(f"{self.base_url}/chat/completions", json=body, timeout=120).json()

    def fit(self):
        """Summarise-to-fit: if over budget, replace old turns with one model-written summary."""
        if count_tokens(self.messages) <= self.budget:
            return
        system, old, recent = self.messages[0], self.messages[1:-self.keep_last], self.messages[-self.keep_last:]
        transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old if m.get("content"))
        prompt = f"Summarise the conversation in one line.\n<transcript>\n{transcript}\n</transcript>"
        summary = self._post([{"role": "user", "content": prompt}])["choices"][0]["message"]["content"]
        self.messages = [{"role": "system", "content": f"{system['content']}\nEarlier: {summary}"}, *recent]
        self.summaries += 1

    def send(self, text, max_steps=4):
        self.messages.append({"role": "user", "content": text})
        self.fit()  # budget check BEFORE every model call
        for _ in range(max_steps):
            reply = self._post(self.messages, TOOLS)["choices"][0]["message"]
            self.messages.append(reply)
            if not reply.get("tool_calls"):
                return reply["content"]
            for call in reply["tool_calls"]:
                args = json.loads(call["function"]["arguments"])
                fn = {"save_memory": self.memory.save, "recall_memory": self.memory.recall}[call["function"]["name"]]
                self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": fn(next(iter(args.values())))})
        return "stopped: max_steps"


if __name__ == "__main__":
    db = Path(__file__).resolve().parent / "memory_demo.db"
    db.unlink(missing_ok=True)  # fresh demo each run
    chat = Chat(MemoryStore(str(db)))
    for text in ["Remember that the staging database is on port 5433.", "Thanks. Now tell me a fun fact about otters.",
                 "And one about penguins please, keep it short."]:
        print(f"> {text}\n  {chat.send(text)}\n  tokens={count_tokens(chat.messages)} summaries={chat.summaries}")
    print("system now:", chat.messages[0]["content"].splitlines()[-1])
    chat.memory.close()
    later = Chat(MemoryStore(str(db)))  # new conversation: empty history, same SQLite file
    print("> What do you remember about staging?\n ", later.send("What do you remember about staging?"))
    later.memory.close()
