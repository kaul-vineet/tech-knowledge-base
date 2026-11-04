"""Learning-tools helper: write the RAG chunk embeddings to a CSV (one row per chunk) for Orange or KNIME.

Run: python export_embeddings.py [embeddings.csv]   (same LOCAL_MODEL_URL as rag.py)
Prints each chunk's nearest neighbour by cosine, so you can check the tool shows the same pairs.
"""
import csv
import sys

import numpy as np

import rag


def nearest_neighbours(chunks, vectors):
    sims = vectors @ vectors.T  # unit vectors: dot product = cosine similarity
    np.fill_diagonal(sims, -np.inf)  # a chunk is not its own neighbour
    return [(chunks[i][0], chunks[int(j)][0], round(float(sims[i, j]), 3)) for i, j in enumerate(sims.argmax(axis=1))]


def write_csv(stream, chunks, vectors):
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["id", "source"] + [f"e{d}" for d in range(vectors.shape[1])])
    for (cid, _), vec in zip(chunks, vectors):
        writer.writerow([cid, cid.split("#")[0]] + [f"{x:.6f}" for x in vec])


if __name__ == "__main__":
    chunks = rag.load_chunks()
    vectors = rag.embed([text for _, text in chunks])
    path = sys.argv[1] if len(sys.argv) > 1 else "embeddings.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        write_csv(f, chunks, vectors)
    print(f"wrote {path}: {len(chunks)} rows x {vectors.shape[1]} dims")
    for cid, other, score in nearest_neighbours(chunks, vectors):
        print(f"  {cid:20} nearest {other:20} cosine {score}")
