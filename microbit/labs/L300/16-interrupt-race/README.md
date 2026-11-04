# Lab 16-interrupt-race — Close-sibling low-level code: a timer interrupt race

**What ran here:** only the host model (`host_sim.py`, `race_model.py`, `solution_model.py`) and
static checks of the Rust sources. **pending-ci:** `cargo test` (logic crate), `cargo build` (firmware
for the nRF52833) and the Renode run (nRF52840 model). There is no Rust toolchain, Renode or internet
in the authoring sandbox.

| File | Purpose |
|---|---|
| `firmware/src/main.rs` | BEFORE: Rust + Embassy for the nRF52833 (micro:bit V2). TIMER1 interrupt every 100 µs adds to `PENDING`; the main loop's `take()` reads, works, writes 0 — racy |
| `firmware/src/bin/fixed.rs` | AFTER (build task): the same file with `take()` inside `critical_section::with` |
| `firmware/Cargo.toml`, `.cargo/config.toml`, `memory.x`, `build.rs`, `rust-toolchain.toml` | Build for `thumbv7em-none-eabihf`, 512 KB flash / 128 KB RAM |
| `logic/` | Pure logic as a `no_std` Rust crate with host tests (`cargo test`) — the same model as `host_sim.py` |
| `host_sim.py` | Python copy of the logic: ISR runs to completion; one NVIC pending bit while masked |
| `race_model.py` / `solution_model.py` | Python mirrors of `take()` before / after |
| `test_main.py` | Model rules + static checks: register addresses and values match the nRF52833 PS; before/after differ only in `take()` |
| `test_fault.py` | The failureLab symptom, deterministic: an IRQ in the window loses exactly one tick; soak loses 316 of 1,316 |
| `test_build_task.py` | Proof: fails on `race_model.py`, passes on `solution_model.py` (every interleaving, 11 seeds) |
| `renode/microbit-v2-sibling.repl`, `.resc`, `interrupt_race.robot` | Renode 1.17.0: nRF52840 model with legacy UART0, script and robot test |
| `try_it.py`, `try_it.json`, `test_try_it.py` | Two `tryIt` items (edits to the host model) |

## What differs from real micro:bit V2 hardware (read this first)
* **Chip:** Renode has no nRF52833 platform (checked `platforms/cpus/` in the Renode repo: only
  `nrf52840.repl`). The firmware is built for the nRF52833 and loaded into the **nRF52840** model.
  This is a close sibling, not the target: same Cortex-M4F core, same TIMER1 (0x40009000, IRQ 9) and
  UART0 (0x40002000, IRQ 2) addresses, but the 840 has 1 MB flash / 256 KB RAM (we use the 833's
  512 KB / 128 KB layout, which fits inside) and peripherals the 833 lacks.
* **Board:** no LED matrix, buttons, motion sensor, speaker, microphone, or interface MCU (KL27/nRF52)
  — the UART goes to Renode's analyzer instead of USB serial. Pin P0.06 is configured but not checked.
* **Peripheral models:** Renode models registers and interrupts, not analog behaviour or exact timing.
  Its stock `nrf52840.repl` puts UART0 in EasyDMA mode; legacy-UART firmware then hangs
  (renode issue #1014), so `microbit-v2-sibling.repl` sets `easyDMA: false`, as Renode's own
  `NRF52840.robot` does.
* **Timing:** Renode runs instructions in blocks and virtual time; whether the racy build loses ticks
  in emulation is recorded, not asserted. The race is proven on the host, deterministically.

## Steps 1-2 — the race on the host, then the fix (runs here)
```bash
cd labs/L300/16-interrupt-race
python3 -m unittest -v test_fault                                   # the symptom
BUILD_FILE=race_model.py python3 -m unittest -v test_build_task     # BEFORE fails (macOS zsh)
$env:BUILD_FILE="race_model.py"; py -m unittest -v test_build_task  # Windows (PowerShell)
python3 -m unittest -v test_build_task                              # AFTER passes
```
Observed (Python 3.12.15, Linux sandbox):
```
test_irq_in_the_window_is_lost (test_fault.Symptom.test_irq_in_the_window_is_lost) ... ok
test_only_the_window_is_dangerous (test_fault.Symptom.test_only_the_window_is_dangerous) ... ok
test_soak_loses_about_a_quarter (test_fault.Symptom.test_soak_loses_about_a_quarter) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.003s

OK
```
```
test_every_interleaving (test_build_task.NoLostTicks.test_every_interleaving) ... FAIL
test_other_seeds (test_build_task.NoLostTicks.test_other_seeds) ... FAIL
test_soak (test_build_task.NoLostTicks.test_soak) ... FAIL
FAIL: test_every_interleaving (test_build_task.NoLostTicks.test_every_interleaving)
AssertionError: 1 != 0 : ('window',)
FAIL: test_other_seeds (test_build_task.NoLostTicks.test_other_seeds)
AssertionError: 280 != 0 : 1
FAIL: test_soak (test_build_task.NoLostTicks.test_soak)
AssertionError: Tuples differ: (1316, 316) != (1316, 0)
Ran 3 tests in 0.024s
FAILED (failures=3)
```
```
test_every_interleaving (test_build_task.NoLostTicks.test_every_interleaving) ... ok
test_other_seeds (test_build_task.NoLostTicks.test_other_seeds) ... ok
test_soak (test_build_task.NoLostTicks.test_soak) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.069s

OK
```

## Step 3 — static checks of the Rust sources (runs here)
```
test_before_and_after_differ_only_in_take (test_main.FirmwareSource.test_before_and_after_differ_only_in_take) ... ok
test_memory_layout_is_nrf52833 (test_main.FirmwareSource.test_memory_layout_is_nrf52833) ... ok
test_timer1_registers (test_main.FirmwareSource.test_timer1_registers) ... ok
test_uart0_registers (test_main.FirmwareSource.test_uart0_registers) ... ok
test_isr_alone_counts_every_tick (test_main.Model.test_isr_alone_counts_every_tick) ... ok
test_one_pending_bit_while_masked (test_main.Model.test_one_pending_bit_while_masked) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.274s

OK
```

## Step 4 — build and unit-test the Rust code (pending-ci)
Install Rust (rustup) and the Cortex-M4F target:
```bash
# macOS (zsh) — Homebrew rustup is keg-only: add it to PATH
brew install rustup && export PATH="$(brew --prefix rustup)/bin:$PATH" && rustup default stable
rustup target add thumbv7em-none-eabihf
```
```powershell
# Windows (PowerShell) — needs the MSVC C++ build tools (see Microsoft's Rust setup page)
winget install -e --id Rustlang.Rustup
rustup target add thumbv7em-none-eabihf
```
Then (both OSes):
```bash
cd logic && cargo test                       # host tests of the pure logic: 4 tests expected
cd ../firmware && cargo build --release --bins   # ELFs: microbit-v2-interrupt-race, fixed
```
Not run here. CI job `rust-firmware` runs both on ubuntu/macos/windows.

## Step 5 — run in Renode (pending-ci)
Install Renode 1.17.0 from the GitHub release assets: macOS `renode-1.17.0.osx-arm64-portable.dmg`,
Windows `renode-1.17.0.setup.exe` (or `windows-portable.zip`), Linux `renode-1.17.0.linux-portable.tar.gz`.
```bash
renode renode/microbit-v2-sibling.resc       # opens the uart0 analyzer
# expected lines (fixed build): round=1 isr=... consumed=... pending=... lost=0 ... done lost_total=0
renode-test renode/interrupt_race.robot      # asserts lost=0 for the fixed build
```
To run the racy build interactively: `renode -e '$bin=@firmware/target/thumbv7em-none-eabihf/release/microbit-v2-interrupt-race; include @renode/microbit-v2-sibling.resc'`.
Not run here. CI job `renode` (Linux portable build).

## All local tests in this lab
```bash
python3 -m unittest -v
```
```
test_every_interleaving (test_build_task.NoLostTicks.test_every_interleaving) ... ok
test_other_seeds (test_build_task.NoLostTicks.test_other_seeds) ... ok
test_soak (test_build_task.NoLostTicks.test_soak) ... ok
test_irq_in_the_window_is_lost (test_fault.Symptom.test_irq_in_the_window_is_lost) ... ok
test_only_the_window_is_dangerous (test_fault.Symptom.test_only_the_window_is_dangerous) ... ok
test_soak_loses_about_a_quarter (test_fault.Symptom.test_soak_loses_about_a_quarter) ... ok
test_before_and_after_differ_only_in_take (test_main.FirmwareSource.test_before_and_after_differ_only_in_take) ... ok
test_memory_layout_is_nrf52833 (test_main.FirmwareSource.test_memory_layout_is_nrf52833) ... ok
test_timer1_registers (test_main.FirmwareSource.test_timer1_registers) ... ok
test_uart0_registers (test_main.FirmwareSource.test_uart0_registers) ... ok
test_isr_alone_counts_every_tick (test_main.Model.test_isr_alone_counts_every_tick) ... ok
test_one_pending_bit_while_masked (test_main.Model.test_one_pending_bit_while_masked) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.093s

OK
```

## Step 6 — try it
```bash
python3 try_it.py
```
```
try 1: racy, short window: irqs 1039, isr runs 1039, consumed 1000, pending 0, lost 39
try 2: fixed, long section: irqs 1632, isr runs 1316, consumed 1316, pending 0, lost 0
```
