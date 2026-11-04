// Lab 16 - a timer interrupt and the main loop share a counter (AFTER: fixed).
// Target: nRF52833 (micro:bit V2), Rust + Embassy. Runs under Renode's nRF52840
// model as a CLOSE SIBLING (same TIMER1/UART0 addresses and IRQ numbers; NOT
// the micro:bit board) - see ../README.md "What differs from real V2 hardware".
//
// Fix: the read-work-write runs inside a critical section (interrupts masked).
// A tick that arrives meanwhile stays pending in the NVIC and runs right after
// the section ends, so it lands in PENDING after our write: nothing is lost.
// Cost: interrupt latency grows by the length of the section - keep it short.
// (PENDING.swap(0, Relaxed) also works: LDREX/STREX make it atomic on this core.)
#![no_std]
#![no_main]

use core::fmt::Write;
use core::sync::atomic::{AtomicU32, Ordering::Relaxed};
use embassy_executor::Spawner;
use embassy_nrf::interrupt;
use embassy_nrf::interrupt::{InterruptExt, Priority};
use embassy_time::Timer;
use panic_halt as _;

// nRF52833 Product Specification: TIMER1 base 0x40009000, UART0 base 0x40002000
const TIMER1_BASE: usize = 0x4000_9000;
const UART0_BASE: usize = 0x4000_2000;

fn reg_write(base: usize, offset: usize, value: u32) {
    unsafe { core::ptr::write_volatile((base + offset) as *mut u32, value) }
}

fn reg_read(base: usize, offset: usize) -> u32 {
    unsafe { core::ptr::read_volatile((base + offset) as *const u32) }
}

static PENDING: AtomicU32 = AtomicU32::new(0); // shared: ISR adds, main takes
static ISR_TOTAL: AtomicU32 = AtomicU32::new(0); // written only by the ISR

#[interrupt]
unsafe fn TIMER1() {
    reg_write(TIMER1_BASE, 0x140, 0); // EVENTS_COMPARE[0] = 0, or the IRQ fires again at once
    PENDING.store(PENDING.load(Relaxed) + 1, Relaxed); // safe here: main cannot preempt an ISR
    ISR_TOTAL.fetch_add(1, Relaxed);
}

// FIXED: the whole read ... work ... write is one critical section.
fn take() -> u32 {
    critical_section::with(|_| {
        let n = PENDING.load(Relaxed);
        cortex_m::asm::delay(2_000); // same work as before, now with the IRQ held off
        PENDING.store(0, Relaxed);
        n
    })
}

fn start_timer1() {
    reg_write(TIMER1_BASE, 0x504, 0); // MODE = Timer
    reg_write(TIMER1_BASE, 0x508, 3); // BITMODE = 32 bit
    reg_write(TIMER1_BASE, 0x510, 4); // PRESCALER = 4: 16 MHz / 2^4 = 1 MHz
    reg_write(TIMER1_BASE, 0x540, 100); // CC[0] = 100 ticks = 100 us
    reg_write(TIMER1_BASE, 0x200, 1); // SHORTS: COMPARE0 -> CLEAR (periodic)
    reg_write(TIMER1_BASE, 0x304, 1 << 16); // INTENSET: COMPARE[0]
    interrupt::TIMER1.set_priority(Priority::P2);
    unsafe { interrupt::TIMER1.enable() };
    reg_write(TIMER1_BASE, 0x00C, 1); // TASKS_CLEAR
    reg_write(TIMER1_BASE, 0x000, 1); // TASKS_START
}

// Legacy UART0 TX on P0.06 (micro:bit V2: target TX to the interface MCU), 115200 baud.
struct Uart;

impl Uart {
    fn init() -> Self {
        reg_write(UART0_BASE, 0x50C, 6); // PSEL.TXD = P0.06, connected
        reg_write(UART0_BASE, 0x524, 0x01D7_E000); // BAUDRATE = 115200
        reg_write(UART0_BASE, 0x500, 4); // ENABLE = UART
        reg_write(UART0_BASE, 0x008, 1); // TASKS_STARTTX
        Uart
    }
}

impl Write for Uart {
    fn write_str(&mut self, s: &str) -> core::fmt::Result {
        for b in s.bytes() {
            reg_write(UART0_BASE, 0x11C, 0); // clear EVENTS_TXDRDY
            reg_write(UART0_BASE, 0x51C, b as u32); // TXD
            while reg_read(UART0_BASE, 0x11C) == 0 {}
        }
        Ok(())
    }
}

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let _p = embassy_nrf::init(Default::default()); // clocks + RTC1 time driver
    let mut uart = Uart::init();
    start_timer1();
    let mut consumed: u32 = 0;
    let mut lost_total: u32 = 0;
    for round in 1..=20u32 {
        for _ in 0..50 {
            consumed += take();
            Timer::after_micros(500).await;
        }
        // observability: a consistent snapshot (interrupts masked while we read both)
        let (isr, pending) = critical_section::with(|_| (ISR_TOTAL.load(Relaxed), PENDING.load(Relaxed)));
        let lost = isr - consumed - pending; // invariant: isr == consumed + pending + lost
        lost_total = lost;
        let _ = write!(uart, "round={} isr={} consumed={} pending={} lost={}\r\n", round, isr, consumed, pending, lost);
    }
    let _ = write!(uart, "done lost_total={}\r\n", lost_total);
    loop {
        Timer::after_secs(1).await;
    }
}
