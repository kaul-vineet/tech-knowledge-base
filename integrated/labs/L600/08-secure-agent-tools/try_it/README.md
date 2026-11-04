# Try it (L600 #08)
Run from the lab folder; each script starts what it needs (the shared fake model on 127.0.0.1 for try_it_1).

1. `python try_it/try_it_1.py` – Predict: if the session token DOES include `send_email`, does the injected email go out?
2. `python try_it/try_it_2.py` – Predict: can an agent widen its own token by attenuating it with a bigger tool list?

Expected outputs are in the lab README and asserted by `tests/test_try_it.py`.
