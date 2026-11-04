"""Equivalent (pending-ci, Linux CI job): the same top-k in PostgreSQL + pgvector 0.8.7.

python pgvector_equivalent.py            -> SQL script for psql (prints the top chunk ids)
python pgvector_equivalent.py --expected -> the ids numpy returns, for diffing
"""
import sys

import rag

QUESTION = "Which tools need human approval?"

if __name__ == "__main__":
    chunks = rag.load_chunks()
    vectors = rag.embed([text for _, text in chunks])
    if "--expected" in sys.argv:
        print("\n".join(cid for cid, _, _ in rag.search(QUESTION, chunks, vectors, k=2)))
        sys.exit(0)
    vec = lambda v: "[" + ",".join(f"{x:.6f}" for x in v) + "]"
    print("CREATE EXTENSION IF NOT EXISTS vector;")
    print(f"CREATE TEMP TABLE chunks (id text PRIMARY KEY, embedding vector({vectors.shape[1]}));")
    for (cid, _), v in zip(chunks, vectors):
        print(f"INSERT INTO chunks VALUES ('{cid}', '{vec(v)}');")
    q = rag.embed([QUESTION])[0]
    print(f"SELECT id FROM chunks ORDER BY embedding <=> '{vec(q)}' LIMIT 2;  -- <=> = cosine distance")
