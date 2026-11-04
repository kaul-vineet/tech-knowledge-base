# Vendored local-agent helper

Copied from `kb/shared/local_agent/` (unchanged except two topic rules in `fake_model_server.py`, documented in its header: `[[ASTRO-SKY]]` for L100 lesson 2 and `[[ASTRO-PERIOD]]` for L200 lesson 10).
- `client.py` - `chat()` for any OpenAI-compatible server; `LOCAL_MODEL_URL` (default `http://localhost:11434/v1`), `LOCAL_MODEL` (default `qwen2.5:1.5b`).
- `fake_model_server.py` - deterministic stand-in used by every test; binds 127.0.0.1 only.
- `test_shared.py` - the helper's own test: `python -m unittest -v`.
