# Vendored local-agent helper

Copied from `kb/shared/local_agent/` (unchanged except three topic rules in `fake_model_server.py`, documented in its header: `[[SIM-SWEEP]]` for L100 lesson 6, `[[SIM-FIT]]` for L200 lesson 7 and `[[SIM-RANK]]` for L300 lesson 14).
- `client.py` - `chat()` for any OpenAI-compatible server; `LOCAL_MODEL_URL` (default `http://localhost:11434/v1`), `LOCAL_MODEL` (default `qwen2.5:1.5b`).
- `fake_model_server.py` - deterministic stand-in used by every test; binds 127.0.0.1 only.
- `test_shared.py` - the helper's own test: `python -m unittest -v` (observed: `Ran 1 test ... OK`).
