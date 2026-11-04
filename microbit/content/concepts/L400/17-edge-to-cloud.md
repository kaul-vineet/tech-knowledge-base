# Concept: designing the path from a sensor board to a dashboard

## Why it matters
A classroom monitor is not one program. Six boards sense, something carries their readings, a PC turns
bytes into messages, a broker hands them on, storage keeps them and a dashboard shows them. Each hop can
lose, delay or duplicate data, and the hop you did not design is the one that fails first. In this lab
it was the relay's 3-frame receive queue. Nobody chose that number: it is simply the radio default.
L400 starts by choosing the architecture on purpose. You state the constraints, measure the options
and write the decision down.

## Mental model
**A school's internal post.** Every classroom (board) drops envelopes into one mailbox (the relay).
The mailbox holds three envelopes. If every class posts at 9:00 sharp and re-posts at 9:01 sharp, the
mailbox overflows every minute, however reliable each envelope is. Staggering the times fixes it.
A bigger mailbox does not.

```
sensors --radio, ARQ--> relay --USB serial, framed--> gateway --MQTT QoS 1--> broker
  n1..n6   (loss, queue 3)   (lab 15 framer)       (trust boundary)       |
                                                       store (dev, seq) <--+--> dashboard (CSV / Prometheus)
```

## Design space
- **Direct serial.** Every board has its own USB cable to the PC. There is no radio and no shared queue.
  The forces against it: cables across a classroom, PC ports, and boards you cannot move.
- **Radio relay.** One board on the PC listens to the others (lab 12's ARQ for each sensor). One cable
  and mobile boards. The cost: a shared medium, a small receive queue on every board, and a relay
  that is a single point of failure.
- **BLE.** This needs a stack that micro:bit MicroPython does not offer to user code. On V2 only BLE
  flashing is implemented, so the option cannot even be measured here. A real design would move to
  another firmware.
- Inside the relay option, the forces are **synchronisation** (everyone samples and retries in
  lock-step) against **buffering** (RAM per board). There is also **frame size**: a growing counter and
  timestamp eventually overflow the radio length.

## How to decide
Write the constraints as numbers first. Here they were: at least 99 % of readings stored, p95
sensor-to-store latency of 2 s or less, and at most one cable to the PC. Then measure every option on
the same seeded network (`options.py`, per-link loss 5–15 %, 30 readings per board):

| Option | Stored | p95 | Given up | USB cables |
|---|---|---|---|---|
| Direct serial | 180/180 | 13 ms | 0 | 6 |
| Relay, as first written | 160/180 | 9,578 ms | 56 | 1 |
| Relay + random phase + jittered timeouts + queue 12 | 180/180 | 153 ms | 0 | 1 |

Direct serial wins on speed but fails the cable constraint. The fixed relay meets every constraint.
To find out which part of the fix matters, change one thing at a time with 24 boards. Jitter alone
(queue 3) stored 480/480. A 12-frame queue alone (no jitter) stored only 151/480, which is 31.5 %.
Desynchronisation is the real fix; the queue only absorbs bursts. A fitness test keeps the decision
true: 5 seeds, 6 boards, delivery ≥ 99 %, p95 ≤ 2 s, nothing given up.

## Failure modes at scale
- **Synchronised senders.** Overflow drops climb with the number of boards. The signal is
  `relay_queue_drops` and `sensor_queue_drops` above zero, and `gave_up` rising.
- **Frames outgrow the packet.** Lab 20's 20-minute run lost every reading after about 1,000 s. The
  frame `D:n1:1000:1000920,...` passed the 32-byte default length, and the radio truncated it. The
  signal is CRC failures at the relay on one board after a fixed uptime.
- **The relay's own CPU and the air.** The stub has no airtime, collisions or MicroPython timing, so it
  shows 40 boards working. On a real board, each forwarded frame costs CRC work and UART time
  (115,200 baud ≈ 2 ms for 24 bytes). Measure these before trusting the model past a classroom.

## Common mistakes
- Treating radio defaults (queue 3, length 32) as design decisions nobody needs to check.
- Fixing loss with a bigger buffer when the cause is lock-step timing.
- Comparing options on different runs or seeds, so the difference is noise.
