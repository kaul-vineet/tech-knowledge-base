**Concept: retrieval-augmented answers – look it up, then answer with citations**

## Why it matters
A model only knows its training data; asked about your team's notes, it guesses. Retrieval-augmented generation (RAG) finds the relevant passages first and puts them in the prompt, so the answer can be checked against a source you own.

## Mental model
An open-book exam: an index points to the right pages, the model reads only those pages, and the answer must quote a page number that code can verify.

```
docs ─► chunk ─► embed ─► vectors (index, built once)
question ─► embed ─► cosine top-k ─► [id] chunks ─► model ─► answer [id]
                                                    code: cited id ∈ retrieved ids?
```

## How it works
1. **Chunk.** Split documents into passages small enough that several fit one prompt; long paragraphs become overlapping word windows. → see lab step 3
2. **Embed.** An embedding model maps each chunk to a vector (`POST /v1/embeddings` on Ollama, llama.cpp or vLLM; Ollama also has `/api/embed`). Use the same model for chunks and questions. → see lab step 5
3. **Search.** With unit-length vectors, cosine similarity is a dot product: `[0.6, 0.8]·[1, 0] = 0.6`. One matrix product scores all chunks; `argsort` picks the top-k. → see lab step 3
4. **Answer and check.** The prompt lists chunks as `[id] text`; code accepts the answer only if every cited id was retrieved. Worked example (fake server): "Which tools need human approval?" retrieves `tool-safety#1` (0.387) and `tool-safety#0` (0.313) and the answer cites `[tool-safety#1]` → grounded. "What is the capital of France?" still returns a top hit (0.183, a hash collision), but the answer has no citation → not grounded. → see lab step 4
5. **Store.** numpy is enough for thousands of chunks; sqlite-vec or pgvector keep vectors next to your data. → see lab step 6

## Trade-offs
| Use when | Avoid when |
|---|---|
| Answers must come from your own, changing documents | The answer needs reasoning over a whole corpus (counts, trends) |
| You need a source to show the user | Documents are tiny – put them in the prompt directly |
| Data cannot be used for fine-tuning | You cannot keep the index up to date |

## Common mistakes
- Trusting top-k blindly: search always returns *something*; add a minimum score (build task).
- Mixing embedding models between indexing and querying.
- Treating retrieved text as instructions – it is untrusted data (lesson 11).
