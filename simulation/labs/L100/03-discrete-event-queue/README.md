# 03 · Discrete-event simulation: a single-server queue

Coffee shop or API worker: heap-based event list, clock jumps between events, mean wait vs the M/M/1 formula.

Read the concept note first: `../../../content/concepts/03-discrete-event-queue.md`.

## Run
```bash
python des_queue.py
```

## Expected output (real run, Python 3.12.15, Linux; seeded, identical on every run)
```
first events (clock jumps from event to event):
t=  0.180  arrive  customer 0  queue=0 busy=False
t=  1.623  depart  customer 0  queue=0
t=  2.531  arrive  customer 1  queue=0 busy=False
t=  2.899  arrive  customer 2  queue=0 busy=True
t=  3.215  depart  customer 1  queue=1
t=  3.645  arrive  customer 3  queue=0 busy=True
t=  4.269  depart  customer 2  queue=1
t=  4.368  depart  customer 3  queue=0
customers=200000  simulated time=250,436 min
simulated mean wait = 3.871 min | M/M/1 formula Wq = 4.000 min | diff -3.2%
```

## Test
```bash
python -m unittest -v
```
Observed: `Ran 6 tests ... OK (skipped=1)` - SimPy test skipped locally (not installed); runs in CI.

## Try it
```bash
python try_it.py
```
Observed:
```
lam=0.8: simulated Wq=3.87 min, formula Wq=4.00 min
lam=0.88: simulated Wq=7.08 min, formula Wq=7.33 min
200 customers, seed 1: mean wait 4.19 min
200 customers, seed 2: mean wait 2.31 min
200 customers, seed 3: mean wait 7.71 min
```

## Library equivalent (pending-ci)
`simpy_queue.py` does the same with the library. It is not installed in the offline sandbox, so it has **not been run yet**; the CI workflow installs the pinned version and runs it plus the un-skipped test.

## Files
- `des_queue.py` - main lab code
- `simpy_queue.py` - SimPy 4.1.2 equivalent (pending-ci)
- `test_des_queue.py` - tests; SimPy test skipped locally
- `try_it.py` - tryIt script
