# Concept: finite state machines driven by events and time

## Why it matters
Games, menus, alarms and protocols all behave differently depending on "where they are". Flags like `playing` and `game_over` multiply bugs; one explicit state plus a transition table keeps behaviour readable and testable.

## Mental model
A **board game card**: you are on exactly one square; an event says which arrow to follow; arrows not printed on the card do nothing.

```
          A / shake              timeout (6 s)
  idle ───────────────► play ────────────────► over
   ▲                    │  ▲ A: hit/miss        │
   │      shake         │  └────────┘           │
   └────────────────────┘◄──────────────────────┘ A
```

## How it works
1. **States are a fixed set:** `idle`, `play`, `over`; the game is in exactly one → see lab step 1
2. **Events come from inputs and time:** `was_pressed()` (edge), `was_gesture("shake")`, and `timeout` when `running_time() - started >= ROUND_MS` → see lab step 2
3. **The table is the behaviour:** `TRANSITIONS[(state, event)] -> (next state, action)`; a missing pair means "ignore" → see lab step 3
4. **Actions run on transitions:** `start` stores the start time, `hit` scores if the dot is in the middle column, `score` prints the result → see lab step 1
5. **Time from a clock, not from counting sleeps:** `running_time()` stays correct even when a loop pass takes longer → see lab step 4

Worked example (`research/concept_examples_l200.py`): 3 states × 3 events = 9 pairs; the table has 6 rows, so 3 pairs are ignored. With `STEP_MS = 300` the dot is at column 2 at 600 ms (hit) and column 3 at 900 ms (miss); at 5999 ms the round is still on, at 6000 ms `timeout` fires.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Behaviour depends on a small set of modes | The "states" are really continuous values |
| You want every transition testable as data | Two independent things change (use two machines) |
| Inputs arrive as events over time | Logic is a single if/else |

## Common mistakes
- Checking `is_pressed()` (a level) instead of an edge, so one press fires many events.
- Measuring time by counting loop passes.
- Hiding transitions inside actions, so the table no longer tells the truth.
