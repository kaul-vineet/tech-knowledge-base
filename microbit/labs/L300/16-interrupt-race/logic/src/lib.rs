//! Lab 16 pure logic: a deterministic model of "the ISR adds, the main loop takes".
//! Same rules as ../host_sim.py (the Python copy that runs in the sandbox):
//!   * the ISR runs to completion; the main loop cannot interrupt it
//!   * while interrupts are masked, an IRQ is held pending - ONE pending bit, like
//!     the NVIC, so two IRQs during one masked section merge into one handler run
//!   * `work` is the moment between the read and the write where an IRQ may fire
#![cfg_attr(not(test), no_std)]

pub struct Machine {
    pub pending: u32,
    pub isr_total: u32,
    pub consumed: u32,
    pub irqs: u32,
    masked: bool,
    irq_pended: bool,
}

impl Machine {
    pub const fn new() -> Self {
        Machine { pending: 0, isr_total: 0, consumed: 0, irqs: 0, masked: false, irq_pended: false }
    }

    fn isr(&mut self) {
        self.pending += 1;
        self.isr_total += 1;
    }

    /// The timer raises its interrupt.
    pub fn irq(&mut self) {
        self.irqs += 1;
        if self.masked {
            self.irq_pended = true;
        } else {
            self.isr();
        }
    }

    fn mask(&mut self) {
        self.masked = true;
    }

    fn unmask(&mut self) {
        self.masked = false;
        if self.irq_pended {
            self.irq_pended = false;
            self.isr();
        }
    }

    /// Ticks the ISR counted that nobody took and that are not pending: overwritten.
    pub fn lost(&self) -> u32 {
        self.isr_total - self.consumed - self.pending
    }
}

impl Default for Machine {
    fn default() -> Self {
        Self::new()
    }
}

/// BEFORE (mirrors firmware/src/main.rs `take`): read, work, write 0.
pub fn take_racy(m: &mut Machine, work: impl FnOnce(&mut Machine)) -> u32 {
    let n = m.pending;
    work(m);
    m.pending = 0;
    m.consumed += n;
    n
}

/// AFTER (mirrors firmware/src/bin/fixed.rs `take`): the same, inside a critical section.
pub fn take_cs(m: &mut Machine, work: impl FnOnce(&mut Machine)) -> u32 {
    m.mask();
    let n = m.pending;
    work(m);
    m.pending = 0;
    m.unmask();
    m.consumed += n;
    n
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn racy_loses_a_tick_that_fires_inside_the_window() {
        let mut m = Machine::new();
        m.irq();
        take_racy(&mut m, |m| m.irq());
        assert_eq!((m.isr_total, m.consumed, m.pending, m.lost()), (2, 1, 0, 1));
    }

    #[test]
    fn racy_is_fine_when_no_irq_hits_the_window() {
        let mut m = Machine::new();
        m.irq();
        take_racy(&mut m, |_| {});
        m.irq();
        assert_eq!(m.lost(), 0);
    }

    #[test]
    fn critical_section_defers_the_tick_instead_of_losing_it() {
        let mut m = Machine::new();
        m.irq();
        take_cs(&mut m, |m| m.irq());
        assert_eq!((m.isr_total, m.consumed, m.pending, m.lost()), (2, 1, 1, 0));
    }

    #[test]
    fn two_irqs_in_one_masked_section_merge() {
        let mut m = Machine::new();
        take_cs(&mut m, |m| {
            m.irq();
            m.irq();
        });
        assert_eq!((m.irqs, m.isr_total, m.lost()), (2, 1, 0));
    }
}
