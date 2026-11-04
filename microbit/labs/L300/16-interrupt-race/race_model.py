"""BEFORE - Python mirror of take() in firmware/src/main.rs (racy)."""


def take(m, work):
    n = m.pending          # PENDING.load(Relaxed)
    work(m)                # cortex_m::asm::delay(2_000): the IRQ may fire here
    m.pending = 0          # PENDING.store(0, Relaxed) - wipes a tick added by `work`
    m.consumed += n
    return n
