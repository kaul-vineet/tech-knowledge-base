# Concept: interrupts, shared data and critical sections

## Why it matters
Below MicroPython, firmware reacts to hardware with interrupt handlers: a timer fires, the handler runs, the main code continues. Data shared between the two is where the bugs live. A counter that loses one tick in four looks right in a quick test and is wrong forever after. This lab writes it in Rust with Embassy for the micro:bit V2's nRF52833 and shows the race deterministically on the host.

## Mental model
**Two clerks, one tally sheet.** The interrupt clerk adds a mark whenever the bell rings. The main clerk copies the total, works for a moment, then wipes the sheet. A bell during the "work" adds a mark that is wiped without ever being copied.

```
main:  read PENDING=3 ──── work ──── write PENDING=0
ISR:                   ▲ PENDING=4
result: consumed 3, PENDING 0, ISR counted 4  →  1 tick lost
fix:   mask ─ read ─ work ─ write ─ unmask → held ISR runs now → PENDING=1
```

## How it works
1. **The window is between read and write.** `take()` loads `PENDING`, delays 2,000 cycles, stores 0. Two atomic operations are not one atomic read-modify-write → see lab step 1
2. **Prove it without hardware.** `host_sim.py` (and the Rust `logic` crate) model the rules: the ISR runs to completion; an IRQ during masking is held with one pending bit. An IRQ placed in the window loses exactly one tick → see lab step 1
3. **Critical section.** `critical_section::with` masks interrupts around read-work-write; the held IRQ runs after the write, so the tick lands in `PENDING` → see lab step 2
4. **Keep the section short.** It adds latency to every interrupt; two IRQs inside one section merge into one handler run → see lab step 6
5. **Register-level setup.** TIMER1 at 0x40009000: prescaler 4 (1 MHz), CC[0] = 100 (100 µs), COMPARE0→CLEAR short, interrupt enabled; the handler clears `EVENTS_COMPARE[0]` → see lab step 3
6. **A close sibling, honestly labelled.** Renode has no nRF52833 model; its nRF52840 has the same TIMER1, UART0 and IRQ numbers and more memory. It checks the firmware boots and the fixed build reports `lost=0`, not the micro:bit board → see lab step 5

Worked example (from `research/concept_examples_l300.py`): the window is 2,000 cycles at 64 MHz = 31.25 µs, against a 100 µs timer period, so about 31% of takes overlap an interrupt. The host soak (1,000 takes, window probability 0.3, seed 16): racy `take()` counted 1,316 interrupts but consumed 1,000, so 316 (24%) were lost; with the critical section all 1,316 were consumed.

## Failure modes
- **Rare races.** A 10× shorter window lost 39 ticks in 1,000 takes: rarer, and more likely to pass a quick test.
- **Masking too long.** Sections longer than the timer period merge interrupts: 1,632 IRQs became 1,316 handler runs.
- **Forgetting to clear the event.** The handler re-enters immediately and starves the main loop.
- **Emulator timing.** Renode schedules instructions differently from silicon; whether the racy build loses ticks there is recorded, not asserted.

## Common mistakes
- Believing `AtomicU32` makes a load followed by a store atomic.
- Doing slow work (formatting, UART output) inside the critical section.
- Calling an emulator run "tested on the micro:bit".
