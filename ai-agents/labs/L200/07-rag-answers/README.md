# 07 – Retrieval-augmented answers

Find the passages that matter, put them in the prompt with ids, and accept the answer only if it cites what was retrieved.

## Run (fake server – validated)
```bash
python ../../L100/01-setup/fake_model_server.py --port 8765   # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python rag.py
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\..\L100\01-setup\fake_model_server.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python rag.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
6 chunks, vectors (6, 64)
Q: How many tokens does Ollama use for the context window by default?
  hits: [('context-windows#0', 0.53), ('context-windows#1', 0.077)]
  A: Ollama uses a 4096-token context window by default and the OLLAMA_CONTEXT_LENGTH variable changes it. [context-windows#0]  grounded=True
Q: Which tools need human approval?
  hits: [('tool-safety#1', 0.387), ('tool-safety#0', 0.313)]
  A: Tools that send, delete or pay need a human approval step. [tool-safety#1]  grounded=True
```
Tests: `Ran 13 tests ... OK (skipped=1)`.

## Learning-tools helper: embeddings as CSV (validated)
`export_embeddings.py` writes one row per chunk (`id`, `source`, `e0`…`e63`) for Orange or KNIME and prints each chunk's nearest neighbour, so you can check the tool shows the same pairs (see `documentation/LEARNING-TOOLS.md`).
```bash
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 python export_embeddings.py embeddings.csv
```
Observed with the fake server (2026-10-28):
```
wrote embeddings.csv: 6 rows x 64 dims
  context-windows#0    nearest context-windows#1    cosine 0.182
  context-windows#1    nearest embeddings#0         cosine 0.203
  embeddings#0         nearest embeddings#1         cosine 0.24
  embeddings#1         nearest tool-safety#1        cosine 0.4
  tool-safety#0        nearest tool-safety#1        cosine 0.269
  tool-safety#1        nearest embeddings#1         cosine 0.4
```
Fake embeddings are hashed bags of words; with a real embedding model the numbers (and maybe the pairs) change.

## Build task
Add a minimum similarity (min_score=0.2): drop weaker hits, and if none remain answer "I don't know" without calling the chat model.

Hints:
- Filter the (id, text, score) tuples from search() before calling ask().
- Return early with grounded False and an empty hits list.
- The France question's best score is 0.183, the approval question's 0.387.

Solution: `solution/rag_min_score.py` · proof: `python -m unittest -v test_build_task`

## Equivalents
- sqlite-vec 0.1.9: vec0 virtual table with distance_metric=cosine, WHERE embedding MATCH ? AND k = 2 (sqlite_vec_equivalent.py, pending-ci)
- pgvector 0.8.7: ORDER BY embedding <=> '[...]' LIMIT 2, <=> = cosine distance (pgvector_equivalent.py, pending-ci Linux CI job)
- llama.cpp: llama-server --embedding (or --embd-gemma-default) serves /v1/embeddings; vLLM: vllm serve <embedding model> serves /v1/embeddings
- Frameworks (LlamaIndex, Haystack, LangChain): the same chunk -> embed -> retrieve -> prompt pipeline behind one call

## Optional steps (not run in the sandbox)
**real embedding + chat model** – Pull an embedding model, check the OpenAI-compatible endpoint, then run with the defaults (http://localhost:11434/v1).
```bash
ollama pull embeddinggemma
ollama pull qwen2.5:1.5b
curl http://localhost:11434/v1/embeddings -H "Content-Type: application/json" -d '{"model": "embeddinggemma", "input": "hello"}'
python rag.py
```
```powershell
ollama pull embeddinggemma
ollama pull qwen2.5:1.5b
Invoke-RestMethod http://localhost:11434/v1/embeddings -Method Post -ContentType application/json -Body '{"model": "embeddinggemma", "input": "hello"}'
# or curl.exe (ships with Windows) with the same arguments as on the Mac
python rag.py
```
Expected: A JSON body with data[0].embedding (a long list of floats); rag.py prints (6, N) with the model's vector length N (Ollama docs: typically 384-1024) and a model-worded answer

**same search in SQLite (sqlite-vec)** – Install the extension and run the equivalence test; it compares sqlite-vec's top-k with numpy's.
```bash
# lesson 1's venv uses Homebrew python@3.12, which can load SQLite extensions (the macOS system Python cannot)
python -m pip install sqlite-vec==0.1.9
python -m unittest -v test_sqlite_vec_equivalent
```
```powershell
python -m pip install sqlite-vec==0.1.9
python -m unittest -v test_sqlite_vec_equivalent
```
Expected: test_same_top_k ... ok (same ids; scores equal to 2 decimals)

## Troubleshooting
| Symptom | Action |
|---|---|
| Every score is about the same | Different embedding models for chunks and question, or vectors not normalised; re-embed everything with one model. |
| HTTP 404 on /v1/embeddings | Server lacks the route: llama-server needs --embedding (or an embedding model); on Ollama check the version. |
| Answer cites an id that was not retrieved | grounded=False is the check working: show 'no grounded answer' instead of the text. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_07` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Call chunk() on context-windows.md with max_words=20, overlap=5 instead of 40/10. | chunk sizes [20, 20, 10, 20, 14] - 5 chunks instead of 2; each window repeats 5 words of the previous one. |
| Ask 'What is the capital of France?' | [('embeddings#1', 0.183), ('context-windows#1', 0.154)] -> I don't know based on the provided context. grounded = False - search still returned two (irrelevant) chunks; only the citation check caught it. |
