**Concept: time-stepped simulation**

## Why it matters
A delivery drone drops a 2 kg parcel from 100 m. How fast does it land? With drag you simulate, and you need to know how wrong the simulation is.

## Mental model
Walking in fog: look at your current speed, step forward dt, look again. Small steps keep you on the path; big steps drift.

```
state (y, v) ──rates (v, a)──> state + dt·rates ──> … until y ≤ 0
            explicit Euler: 1 slope per step
            RK4:            4 slopes per step, weighted 1-2-2-1
```

## How it works
1. **Advance state with rates:** height changes by v·dt, velocity by a·dt, where a = −g − drag/m → see lab step 1.
2. **Error depends on method and dt:** without drag the exact height at 3 s is 55.9 m; explicit Euler is +1.47 m off at dt = 0.1 and +0.147 m at dt = 0.01 (first order), while RK4 is exact apart from round-off → see lab step 2.
3. **Validate on the exact case, then add physics:** with drag the parcel lands at 18.37 m/s, just under the terminal velocity √(2mg/(Cd·ρ·A)) = 18.40 m/s → see lab step 4.

## Common mistakes
- Drag with the wrong sign, so the parcel accelerates forever.
- Picking dt by habit instead of halving it until the answer stops changing.
- Reporting ground time without noticing it is rounded to a multiple of dt.
