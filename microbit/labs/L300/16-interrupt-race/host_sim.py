"""Lab 16 host model (CPython, runs in the sandbox): the pure logic of
logic/src/lib.rs, line for line, so the race can be shown deterministically.

Rules: the ISR runs to completion; while masked an IRQ is held pending with ONE
pending bit (like the NVIC); `work` is the moment between read and write.
"""
import random


class Machine:
    def __init__(self):
        self.pending = self.isr_total = self.consumed = self.irqs = 0
        self._masked = self._irq_pended = False

    def _isr(self):                    # TIMER1(): PENDING += 1; ISR_TOTAL += 1
        self.pending += 1
        self.isr_total += 1

    def irq(self):                     # the timer raises its interrupt
        self.irqs += 1
        if self._masked:
            self._irq_pended = True
        else:
            self._isr()

    def mask(self):
        self._masked = True

    def unmask(self):
        self._masked = False
        if self._irq_pended:
            self._irq_pended = False
            self._isr()

    def lost(self):                    # counted by the ISR, never taken, not pending
        return self.isr_total - self.consumed - self.pending


def schedule(take, fire):
    """One take() with IRQs at chosen points: fire is a subset of before/window/after."""
    m = Machine()
    if "before" in fire:
        m.irq()
    take(m, (lambda mm: mm.irq()) if "window" in fire else (lambda mm: None))
    if "after" in fire:
        m.irq()
    return m


def soak(take, takes=1000, p_window=0.3, seed=16):
    """Many takes; an IRQ lands in the read/write window with probability p_window."""
    rng, m = random.Random(seed), Machine()
    for _ in range(takes):
        m.irq()                                        # a tick between two takes
        take(m, (lambda mm: mm.irq()) if rng.random() < p_window else (lambda mm: None))
    return m
