"""Tool: search_docs (read-only). Returns the doc that shares most words with the query."""
import re


def run(world, query):
    words = set(re.findall(r"[a-z]+", query.lower()))
    score = lambda item: (-len(words & set(re.findall(r"[a-z]+", (item[0] + " " + item[1]).lower()))), item[0])
    name, text = sorted(world.docs.items(), key=score)[0]
    return f"{name}: {text}"
