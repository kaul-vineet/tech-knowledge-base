# Concept: non-blocking firmware with a cooperative scheduler

## Why it matters
A board does several jobs: read a sensor every second, watch a button, refresh the display. With `sleep(1000)` in the loop, everything else stops for that second. A quick tap inside the sleep never happened as far as the program knows: no error, no log.

## Mental model
**A kitchen timer board.** Each task has its own timer (button 20 ms, sensor 1000 ms, display 100 ms). The cook never sleeps: glance at the clock, do what is due, glance again, and note any job that ran long.

```
blocking:  [btn][sensor] sleep(1000) ......... [btn][sensor] sleep ...
                         ^ tap 932..1082 ms: seen only because it covers t=1000
scheduler: btn btn btn ... sensor ... btn btn display btn ...  (every 20 / 1000 / 100 ms)
```

## How it works
1. **Polling only sees "now".** `is_pressed()` reports the pin at the moment of the call; `was_pressed()` latches one press but loses the count and length → see lab step 1
2. **Each task has a period, a due time and a budget.** `run_once()` compares `running_time()` with each task's `due`, runs what is due and sets the next due time → see lab step 3
3. **No sleep in the main loop.** The loop only asks "what is due?"; the button task runs every 20 ms, well inside a 150 ms tap → see lab step 3
4. **Overrun and late detection.** A run longer than its budget prints a JSON `overrun` line; a start over one period late prints `late` with the missed periods, which are skipped, not run in a burst → see lab step 4
5. **Contain errors, then go safe.** An exception in a task is caught and logged; after 3 in a row the task is disabled and `safe_state()` sets outputs off and shows a cross, once → see lab step 5
6. **Cooperative means trusting every task.** A task that blocks still blocks everyone; the overrun line tells you which one → see lab step 6

Worked example (from `research/concept_examples_l300.py`): 8 taps of 150 ms at 932, 1680 … 7744 ms. The blocking loop samples once per 1000 ms, so each tap has a 150/1000 = 15% chance of covering a sample; it counted 1 of 8 (the tap at 932–1082 ms covers t = 1000). The scheduler counted 8 of 8 in 610 task runs with 0 overruns, 0 missed periods, 0 errors.

## Failure modes
- **Polling slower than the shortest event.** With the button task at 200 ms, 6 of 8 taps were counted. Notice it by comparing the period with the event length.
- **A blocking call inside a task.** `sleep(300)` in the sensor task produced 10 overruns and 170 missed periods in 10 s. The JSON lines name the task.
- **A sensor that keeps failing.** Uncontained, one exception ends the program; contained, the board reports and goes safe.
- **Busy loop power.** No sleep keeps the CPU awake; lesson 14 trades this against current.

## Common mistakes
- Catching up missed periods in a burst after a stall.
- Timing a task from a start time read before an earlier task ran, which blames the wrong task.
- Logging every error forever instead of disabling the task and going to a safe state.
