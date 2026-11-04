# 02 · Two services talking

Service B answers `GET /price?item=…`; service A calls it with `urllib` and times each call with `time.perf_counter()`.

Files: `two_services.py` (the lesson code), `helpers.py` (plumbing: quiet handler, `reply()`, background server), `try_it.py` (tryIt experiments), `test_two_services.py`.

## Run
```bash
python two_services.py
```

## Expected output (real run, Python 3.12.15, Linux — your port and ms values will differ)
```
service B listening on http://127.0.0.1:36181
A -> B  GET /price?item=apple -> 200 {'item': 'apple', 'price': 3}  (10.0 ms)
A -> B  GET /price?item=pear  -> 200 {'item': 'pear', 'price': 4}  (4.8 ms)
A -> B  GET /price?item=plum  -> 200 {'item': 'plum', 'price': 5}  (4.7 ms)
A -> B  GET /price?item=apple -> 200 {'item': 'apple', 'price': 3}  (3.2 ms)
A -> B  GET /price?item=pear  -> 200 {'item': 'pear', 'price': 4}  (3.0 ms)
A -> B  GET /price?item=kiwi  -> 404 {'error': "unknown item 'kiwi'"}
latency ms: min=3.0 median=4.7 max=10.0
```
No randomness is used; only the measured latencies vary between runs.

## Test
```bash
python -m unittest -v          # Ran 2 tests ... OK
```

## Run A and B as separate processes (optional)
B is a normal `ThreadingHTTPServer`; to run it alone:
`python -c "import two_services as t, time; s=t.start_b(8002); print('B on 8002'); time.sleep(3600)"`
then from another terminal: `curl "http://127.0.0.1:8002/price?item=pear"` (Windows PowerShell: `curl.exe`).

## Try it (real run, Python 3.12.15, Linux)
```bash
python try_it.py
```
```
tryIt 1: URLError -> ConnectionRefusedError: Connection refused
tryIt 2: every call >= 50 ms: True; 3 sequential calls >= 150 ms: True (total 166 ms)
```
The total ms varies per run; the two `True` checks do not. The refusal text is Linux's: Windows reports `[WinError 10061]` (WSAECONNREFUSED) with its own wording; the exception class is the same.
