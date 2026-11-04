# Concept: the toolchain — editor, simulator, serial, stub

## Why it matters
You want to try a micro:bit program without a board, and you want a test to tell you when a change breaks the logic. You need to know which tool runs what, and what each one can prove.

## Mental model
Three "boards" accept the same `main.py`: the **simulator** (real firmware, fake hardware), a **physical micro:bit** (real everything) and the **stub** (fake firmware and hardware).

```
main.py ─► Python Editor ─postMessage─► simulator (MicroPython as WebAssembly) ─► serial panel
   └─────► python -m unittest + labs/sim_stub ─► captured print() text
```

## How it works
1. **Flash** copies `main.py` to the simulator and restarts it: the editor posts `{"kind": "flash", "filesystem": {"main.py": bytes}}` to the iframe. Lab 01's file is **895 bytes** (computed by `research/concept_examples.py`) → see lab step 2
2. **Serial**: every `print()` comes back as a `serial_output` message and appears in the serial panel; Ctrl+C there opens the REPL, Ctrl+D restarts → see lab step 3
3. **Stub tests** import `main.py` under a name other than `__main__`, so `while True` never starts; tests call `step()` with injected inputs, and `sleep(1000)` only advances a virtual clock (three passes = **3000 ms**) → see lab step 6

## Common mistakes
- Running `python main.py` on a PC and getting `ModuleNotFoundError: microbit` — run the tests instead.
- Assuming V2-only code (speaker, logo) works on a V1 board.
- Treating a green stub test as "verified on the simulator".
