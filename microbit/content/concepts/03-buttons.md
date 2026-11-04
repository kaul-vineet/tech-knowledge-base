# Concept: level vs edge — reading buttons from a polling loop

## Why it matters
A counter skips presses, or one press counts twice. The cause is almost always asking the wrong question: *is it down now?* versus *did it go down since I last looked?*

## Mental model
A doorbell with a **notepad**. `is_pressed()` looks at the bell right now. `was_pressed()` checks for a tick on the notepad and rubs it out. `get_presses()` counts all the ticks and rubs them all out. Your loop glances every 100 ms.

```
clicks:   ▼ ▼ ▼
poll 1:   is_pressed False | was_pressed True  | get_presses 3
poll 2:   is_pressed False | was_pressed False | get_presses 0
```
(Values from `research/concept_examples.py`.)

## How it works
1. `get_presses()` returns every press since the last call and resets to 0 (counted edges), so three clicks between polls print `count 3` → see lab step 2
2. `was_pressed()` is a yes/no **edge** flag, cleared when read; a second call with no new press returns False → see lab step 3
3. `is_pressed()` is the **level** at this instant. A slow loop misses quick taps with it, while the runtime keeps counting presses for `get_presses()` → see lab step 4

## Common mistakes
- Counting with `is_pressed()`: a held press counts once per poll, a quick tap may count 0.
- Calling `was_pressed()` twice in one loop and expecting both to be True.
- Long `sleep()` or blocking `scroll()` making reactions late (presses are kept).
