**Capstone: a digital twin of a service centre - from call logs to a governed staffing decision**

## Overview
A service centre is open 08:00-20:00 and wants a staffing plan: at least 80% of calls answered within 1 minute and at most 5% abandoned in every hour, with as few agent-hours as possible. It also wants the plan to react when today's demand departs from the forecast. The capstone builds that end to end and scores itself with six milestones in a JSON-lines scorecard. Deterministic code makes every decision; an optional local model only explains, and its explanation is published only if every number in it checks out.

## Architecture walkthrough
```
history.csv --M1 fit--> rates, lognormal service --M3 calibrate patience (days 1-3)--> holdout check (days 4-5)
                                   |                                                     |
                              centre.py DES (M2: Erlang C degenerate check)               |
                                   |                                                     v
          M4: Erlang C seed -> hour_check (95% bounds) -> full-day repair -> plan --M5a--> runner (spawn pool, SQLite)
today.jsonl --M5b DemandTwin (Kalman + lesson 17 CUSUM)--> alarm --> re-plan rest of day
          M6: governance_pack.check(model_card.json) + agent_explain (code checks numbers) --> scorecard.jsonl
```
1. **Input modelling (M1).** Arrival rates per hour, and handle times fitted with lesson 7's candidates and KS distance. Lognormal wins (D 0.0059 against 0.1403 normal and 0.1762 exponential). The rates are within 7% of the hidden truth.
2. **DES core (M2).** Thinning for time-varying arrivals (Lewis & Shedler 1979), plus exponential patience. With no abandonment and exponential service, the simulated service level of 0.8376 matches Erlang C's 0.8365.
3. **Calibration and validation (M3).** Patience cannot be observed directly, so it is fitted to the abandonment profile of days 1-3. The best value is 4.5 min, but anything from 3.0 to 5.5 fits within 20%, so patience is weakly identified (lesson 13). On the holdout days 4-5 the errors are 1.09 pp for service level and 0.73 pp for abandonment.
4. **Sensitivity and optimisation (M4).** The peak-hour service level has elasticity -0.64 to demand, -0.68 to handle time and -0.01 to patience, so the weak identification does not matter for the decision. Staffing starts from Erlang C (219 agent-hours), is checked hour by hour with 95% bounds, and is repaired against full-day runs. The result is 221 agent-hours. Deciding on point estimates gave 208, but its worst hour abandoned 6.4% of calls.
5. **Parallel replications and the twin (M5).** 24 full-day replications run on a process pool into SQLite, with streams keyed on the replication (lesson 20). A crashed-and-resumed run is identical. The twin raised its alarm 75 minutes into a +30% surge. Re-planning from 15:00 added 14 agent-hours and lifted the worst service level in the affected hours from 0.719 to 0.896.
6. **Governance and agent (M6).** The model card's claims are checked against this run's evidence, with hashes of the code and data (lesson 21). The surge plan needs 6.16 calls/min, more than the validated 5.6, so it carries a review flag. The fake agent's invented "9% saving" is caught, and its explanation is not published.

## How it ties the levels together
L100 gives the event list, seeds and the difference between V&V. L200 gives input fitting, Erlang C and common random numbers. L300 gives calibration with a holdout, sensitivity and independent streams. L400 adds the twin, budget-aware optimisation, checkpointed parallel runs and machine-checked governance. Three ADRs record the decisions, and `test_fitness.py` keeps them true.
