**Concept: discrete-event simulation**

## Why it matters
Your API has one worker. Traffic will grow 10%. Will latency grow 10%? Queues are non-linear, and a discrete-event model answers this in seconds before you buy servers.

## Mental model
A diary of future appointments. Read the earliest entry, jump the clock to it, act, and write any new appointments it causes. Nothing happens between entries, so nothing is computed there.

```
heap: (0.180 arrive c0) (… )
pop ─> clock=0.180 ─> start service ─> push (1.623 depart c0), (2.531 arrive c1)
pop ─> clock=1.623 ─> server idle
pop ─> clock=2.531 ─> …
```

## How it works
1. **Event list:** future events sit in a min-heap ordered by time; a sequence number breaks ties so equal times stay first-in-first-out → see lab step 2.
2. **Clock jumps, events schedule events:** popping an arrival schedules the next arrival and, if the server is free, a departure → see lab step 2.
3. **Check against a known case:** for M/M/1, Wq = λ/(μ(μ−λ)) = 0.8/(1·0.2) = 4.0 min; 200,000 simulated customers give 3.871 → see lab step 3.

## Common mistakes
- Stepping a fixed tick (every second) when nothing changes between events.
- Measuring wait from service end instead of service start.
- Running λ ≥ μ: the queue grows forever and there is no steady mean.
