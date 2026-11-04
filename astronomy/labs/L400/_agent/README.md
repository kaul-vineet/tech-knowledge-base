# L400 local-agent helper (astronomy copy)

A copy of `kb/shared/local_agent/` (`client.py`, `fake_model_server.py`, `__init__.py`, `test_shared.py`). The only change is in `fake_model_server.py`: two **documented, deterministic** rules for this topic are registered at import time.
- `[[ASTRO-ALERT]]` (lesson 18): it explains an alert. It deliberately calls a `known_variable` "a new transient" and invents "2.5 magnitudes".
- `[[ASTRO-CANDIDATE]]` (capstone): it calls every candidate "a planet" and invents "1.8 Earth radii".

The labs' code must catch both mistakes. That is the point: the agent explains, and code decides.

- `client.chat()` reads `LOCAL_MODEL_URL` (default `http://localhost:11434/v1`) and `LOCAL_MODEL` (default `qwen2.5:1.5b`).
- Tests use only the fake server (`fake_model_server.start_in_thread()`, bound to 127.0.0.1).
- `python -m unittest -v` in this folder runs the shared helper test plus `test_astro_rules.py`.
