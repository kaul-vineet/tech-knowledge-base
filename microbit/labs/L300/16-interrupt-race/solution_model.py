"""AFTER - Python mirror of take() in firmware/src/bin/fixed.rs (critical section)."""


def take(m, work):
    m.mask()               # critical_section::with(|_| {
    n = m.pending          #     PENDING.load(Relaxed)
    work(m)                #     delay: an IRQ now only sets the pending bit
    m.pending = 0          #     PENDING.store(0, Relaxed)
    m.unmask()             # }) -> the held IRQ runs now, after our write
    m.consumed += n
    return n
