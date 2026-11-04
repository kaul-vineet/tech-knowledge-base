"""Lab 16 local checks: the host model's rules, and static checks of the Rust
sources against the nRF52833 Product Specification. These do NOT compile or run
the firmware (no Rust toolchain or Renode here: pending-ci)."""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import host_sim  # noqa: E402


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as f:
        return f.read()


class Model(unittest.TestCase):
    def test_isr_alone_counts_every_tick(self):
        m = host_sim.Machine()
        for _ in range(5):
            m.irq()
        self.assertEqual((m.isr_total, m.pending, m.lost()), (5, 5, 0))

    def test_one_pending_bit_while_masked(self):
        m = host_sim.Machine()
        m.mask()
        m.irq()
        m.irq()
        m.unmask()
        self.assertEqual((m.irqs, m.isr_total), (2, 1))


class FirmwareSource(unittest.TestCase):
    """Register values in main.rs/fixed.rs = nRF52833 PS (TIMER, UART, Memory chapters)."""

    def test_timer1_registers(self):
        src = read("firmware", "src", "main.rs")
        self.assertIn("const TIMER1_BASE: usize = 0x4000_9000;", src)
        for off, val in (("0x504", "0"), ("0x508", "3"), ("0x510", "4"), ("0x540", "100"),
                         ("0x200", "1"), ("0x304", "1 << 16"), ("0x00C", "1"), ("0x000", "1")):
            self.assertIn("reg_write(TIMER1_BASE, %s, %s)" % (off, val), src)
        self.assertIn("reg_write(TIMER1_BASE, 0x140, 0)", src)        # EVENTS_COMPARE[0] cleared in the ISR

    def test_uart0_registers(self):
        src = read("firmware", "src", "main.rs")
        for needle in ("const UART0_BASE: usize = 0x4000_2000;", "reg_write(UART0_BASE, 0x50C, 6)",
                       "reg_write(UART0_BASE, 0x524, 0x01D7_E000)", "reg_write(UART0_BASE, 0x500, 4)",
                       "reg_write(UART0_BASE, 0x008, 1)", "reg_write(UART0_BASE, 0x51C, b as u32)",
                       "reg_read(UART0_BASE, 0x11C)"):
            self.assertIn(needle, src)

    def test_memory_layout_is_nrf52833(self):
        mem = read("firmware", "memory.x")
        self.assertRegex(mem, r"FLASH : ORIGIN = 0x00000000, LENGTH = 512K")
        self.assertRegex(mem, r"RAM   : ORIGIN = 0x20000000, LENGTH = 128K")

    def test_before_and_after_differ_only_in_take(self):
        racy, fixed = read("firmware", "src", "main.rs"), read("firmware", "src", "bin", "fixed.rs")
        body = lambda s: re.search(r"fn take\(\) -> u32 \{.*?\n\}", s, re.S).group(0)
        self.assertNotIn("critical_section", body(racy))
        self.assertIn("critical_section::with(|_| {", body(fixed))
        strip = lambda s: re.sub(r"fn take\(\) -> u32 \{.*?\n\}", "", s, flags=re.S).split("#![no_std]")[1]
        self.assertEqual(strip(racy).replace("// RACE: read ... window ... write. A tick added inside the window is lost.\n", ""),
                         strip(fixed).replace("// FIXED: the whole read ... work ... write is one critical section.\n", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
