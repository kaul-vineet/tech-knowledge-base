"""Build-task solution (lesson 7): drop weak hits; with nothing left, say "I don't know" WITHOUT calling the model."""
import rag


def answer_with_threshold(question, chunks, vectors, k=2, min_score=0.2, base_url=rag.BASE_URL, model=rag.MODEL):
    hits = [h for h in rag.search(question, chunks, vectors, k, base_url) if h[2] >= min_score]
    if not hits:  # deterministic refusal: no model call, nothing to hallucinate from
        return {"answer": f"I don't know: no chunk scored >= {min_score}.", "hits": [], "cited": [], "grounded": False}
    return rag.ask(question, hits, base_url, model)
