"""Retrieval-augmented answers: chunk local docs, embed, cosine top-k with numpy, answer with checked citations."""
import os
import re
from pathlib import Path

import numpy as np
import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "embeddinggemma")
DOCS = Path(__file__).resolve().parent / "docs"


def chunk(text, max_words=40, overlap=10):
    """Split on blank lines; a long paragraph becomes overlapping word windows."""
    chunks = []
    for para in re.split(r"\n\s*\n", text):
        words = para.split()
        if not words or para.lstrip().startswith("#"):
            continue  # skip headings / empty paragraphs
        for start in range(0, len(words), max_words - overlap):
            chunks.append(" ".join(words[start:start + max_words]))
            if start + max_words >= len(words):
                break
    return chunks


def load_chunks(folder=DOCS):
    return [(f"{p.stem}#{i}", c) for p in sorted(folder.glob("*.md"))
            for i, c in enumerate(chunk(p.read_text(encoding="utf-8")))]


def embed(texts, base_url=BASE_URL, model=EMBED_MODEL):
    resp = requests.post(f"{base_url}/embeddings", json={"model": model, "input": texts}, timeout=120)
    resp.raise_for_status()
    vectors = np.array([d["embedding"] for d in sorted(resp.json()["data"], key=lambda d: d["index"])])
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True).clip(min=1e-12)  # unit length: dot = cosine


def search(question, chunks, vectors, k=2, base_url=BASE_URL):
    scores = vectors @ embed([question], base_url)[0]  # cosine similarity against every chunk
    best = np.argsort(-scores)[:k]
    return [(chunks[i][0], chunks[i][1], round(float(scores[i]), 3)) for i in best]


def answer(question, chunks, vectors, k=2, base_url=BASE_URL, model=MODEL):
    return ask(question, search(question, chunks, vectors, k, base_url), base_url, model)


def ask(question, hits, base_url=BASE_URL, model=MODEL):
    context = "\n".join(f"[{cid}] {text}" for cid, text, _ in hits)  # ids let the model cite
    prompt = ("Answer only from the context and cite the chunk id in brackets.\n"
              f"<context>\n{context}\n</context>\nQuestion: {question}")
    reply = requests.post(f"{base_url}/chat/completions", timeout=120, json={
        "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
    text = reply.json()["choices"][0]["message"]["content"]
    cited = re.findall(r"\[([^\]]+)\]", text)
    retrieved = {cid for cid, _, _ in hits}
    grounded = bool(cited) and set(cited) <= retrieved  # code checks every citation is a retrieved chunk
    return {"answer": text, "hits": hits, "cited": cited, "grounded": grounded}


if __name__ == "__main__":
    chunks = load_chunks()
    vectors = embed([text for _, text in chunks])
    print(f"{len(chunks)} chunks, vectors {vectors.shape}")
    for q in ["How many tokens does Ollama use for the context window by default?",
              "Which tools need human approval?"]:
        result = answer(q, chunks, vectors)
        print(f"Q: {q}\n  hits: {[(cid, score) for cid, _, score in result['hits']]}")
        print(f"  A: {result['answer']}  grounded={result['grounded']}")
