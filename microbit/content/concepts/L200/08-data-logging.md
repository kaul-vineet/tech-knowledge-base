# Concept: a log is a table with a fixed schema and a time column

## Why it matters
A greenhouse sensor, a fridge check, a lap timer: the value of a reading is in the series, not the single number. You need rows with the same columns, a timestamp, a way to get them off the board, and a plan for when storage is full.

## Mental model
A **spreadsheet that only appends**. Labels are the header row, chosen once; each sample adds one row; time is the first column.

```
sample() ──► row {temp, light} ──┬─► log.add(row)  ─► MY_DATA (board flash; "Time (seconds)" first)
                                 └─► print(csv)     ─► serial ─► export_csv.py ─► readings.csv
```

## How it works
1. **Schema first.** `log.set_labels("temp", "light", timestamp=log.SECONDS)` sets the header once; a new label later adds a column and a second header row → see lab step 1
2. **One sample = one row.** `log.add(dict)` writes the values plus the timestamp; missing labels become empty fields → see lab step 4
3. **Two outputs on purpose.** `MY_DATA` survives power-off on a V2 board; serial CSV is what the simulator panel shows and what `export_csv.py` turns into an RFC 4180 file → see lab step 3
4. **Full is a normal state.** `log.add` raises `OSError` 28 (`ENOSPC`); inside `run_every` an uncaught exception unschedules the callback, so catch it → see lab step 6
5. **Code computes, people interpret.** Statistics come from the CSV by code; an agent may only explain them → see lab step 7

Worked example (stub run, `research/concept_examples_l200.py`): three samples one second apart give serial rows `0,21,120`, `1000,22,110`, `2000,23,100` and log rows `0.00,21,120`, `1.00,22,110`, `2.00,23,100` under `Time (seconds),temp,light`. One serial row is 13 bytes with CRLF; one row per second is 3600 rows per hour.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| The board runs unattended (`log`, V2 only) | You need sub-millisecond sampling |
| A laptop listens anyway (serial CSV) | Rows are free text with commas or quotes |
| Readings must survive power-off | A V1 board must run the same code (no `log`) |

## Common mistakes
- Changing labels or the timestamp unit mid-run, which starts a new header section.
- Ignoring the full log, so a scheduled logger silently stops.
- Parsing serial text without checking field count and number format.
