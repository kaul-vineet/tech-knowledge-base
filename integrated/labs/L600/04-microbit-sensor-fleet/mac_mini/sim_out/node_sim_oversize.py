# L600 #04 fleet node firmware (micro:bit V2 MicroPython; here it runs on the microbit topic's CPython stub).
# Offline-first: every reading is written to the flash log first; a sync only deletes what a gateway acked.
# Identity = a "dot" (device, boot, seq): seq restarts at 1 on every boot, boot is persisted in flash.
# Wall time (epoch from the last gateway ack + running_time) is only a display attribute - it can repeat.
from microbit import *
import radio

SCHEMA = 2                   # firmware schema: 1 = temp only (8-byte record), 2 = temp + light (9 bytes)
SAMPLE_MS = 60000            # one reading per minute
SYNC_EVERY = 10              # samples between syncs (10 min)
RADIO_LENGTH = 32            # radio.config(length=...): the docs' default; max 251
HEADER = 3                   # schema, kind, device
REC_LEN = {1: 8, 2: 9}
RECORDS_PER_FRAME = 27        # (RADIO_LENGTH - HEADER) // REC_LEN[SCHEMA]
QUEUE = 16                   # incoming queue: up to 2 gateways x 8 acks per attempt
MAX_FRAMES = 8               # frames per attempt (oldest records first)
MAX_TRIES = 3                # attempts per sync
ACK_WAIT_MS = 50             # radio on, listening for acks (ASSUMPTION, see ADR 0003)
ACTIVE_MS = 20               # awake per sample: microbit L300 #14 budget.FIGURES["ACTIVE_MS"]
MAX_LOG = 400                # records kept in flash (400 x 9 B = 3.6 kB)


def new_state(dev, flash, phase=0):
    """Boot: RAM state is new, `flash` survives resets (on a board: a small file written with open())."""
    flash["boot"] = flash.get("boot", 0) + 1
    flash.setdefault("epoch_s", 0)
    flash.setdefault("log", [])
    return {"dev": dev, "seq": 0, "flash": flash, "since_sync": phase,
            "stats": {"sampled": 0, "dropped": 0, "frames": 0, "tries": 0, "acked": 0, "awake_ms": 0}}


def wall_s(state):
    return state["flash"]["epoch_s"] + running_time() // 1000


def sample(state):
    state["seq"] += 1
    light = display.read_light_level() if SCHEMA >= 2 else None
    rec = (state["flash"]["boot"], state["seq"], wall_s(state), temperature(), light)
    log = state["flash"]["log"]
    if len(log) >= MAX_LOG:              # flash full: the oldest reading is lost (counted, never silent)
        log.pop(0)
        state["stats"]["dropped"] += 1
    log.append(rec)
    state["stats"]["sampled"] += 1
    state["stats"]["awake_ms"] += ACTIVE_MS
    state["since_sync"] += 1
    return rec


def pack(rec):
    boot, seq, wall, temp, light = rec
    out = bytes([boot & 0xFF, (seq >> 8) & 0xFF, seq & 0xFF,
                 (wall >> 24) & 0xFF, (wall >> 16) & 0xFF, (wall >> 8) & 0xFF, wall & 0xFF, temp & 0xFF])
    return out + bytes([light]) if SCHEMA >= 2 else out


def frames(state):
    """Delta, not state: only unacked records, oldest first, RECORDS_PER_FRAME per frame."""
    log, out = state["flash"]["log"], []
    for i in range(0, min(len(log), RECORDS_PER_FRAME * MAX_FRAMES), RECORDS_PER_FRAME):
        body = b"".join(pack(r) for r in log[i:i + RECORDS_PER_FRAME])
        out.append(bytes([SCHEMA, ord("D"), state["dev"]]) + body)
    return out


def on_ack(state, msg):
    """Ack = [schema, 'A', dev, epoch(4), n] + n x (boot, hw(2)) + k x (boot, seq(2)).
    (boot, hw): the gateway holds every seq <= hw of that boot. (boot, seq): it holds exactly this record
    (selective ack - without it, one record lost from a full flash log would block every later ack)."""
    if len(msg) < 8 or msg[1] != ord("A") or msg[2] != state["dev"]:
        return
    epoch = (msg[3] << 24) | (msg[4] << 16) | (msg[5] << 8) | msg[6]
    state["flash"]["epoch_s"] = epoch - running_time() // 1000      # time beacon: may step backwards
    n, hw, exact = msg[7], {}, set()
    for i in range(8, len(msg) - 2, 3):
        boot, seq = msg[i], (msg[i + 1] << 8) | msg[i + 2]
        if (i - 8) // 3 < n:
            hw[boot] = seq
        else:
            exact.add((boot, seq))
    log = state["flash"]["log"]
    keep = [r for r in log if not (r[1] <= hw.get(r[0], 0) or (r[0], r[1]) in exact)]
    state["stats"]["acked"] += len(log) - len(keep)
    state["flash"]["log"] = keep


def sync(state):
    t0 = running_time()
    radio.on()
    radio.config(length=RADIO_LENGTH, queue=QUEUE)
    for _ in range(MAX_TRIES):
        out = frames(state)
        if not out:
            break
        state["stats"]["tries"] += 1
        for f in out:
            radio.send_bytes(f)
            state["stats"]["frames"] += 1
        sleep(ACK_WAIT_MS)
        msg = radio.receive_bytes()
        while msg is not None:
            on_ack(state, msg)
            msg = radio.receive_bytes()
    radio.off()                          # radio off between syncs: Deep Sleep cannot receive anyway
    state["since_sync"] = 0
    state["stats"]["awake_ms"] += ACTIVE_MS + running_time() - t0


def tick(state):
    rec = sample(state)
    if state["since_sync"] >= SYNC_EVERY:
        sync(state)
    return rec


def main(dev=1, ticks=30, gap_ms=200):
    # SIMULATOR DRIVER (generated by mac_mini/make_sim_programs.py): sleep instead of deep_sleep, fixed tick count
    state = new_state(dev, {})
    print("node ready schema %d" % SCHEMA)
    big = 0
    for _ in range(ticks):
        for f in frames(state):
            big = max(big, len(f))       # largest frame the firmware builds (before the radio truncates it)
        tick(state)
        sleep(gap_ms)
    sync(state)
    s = state["stats"]
    print("stats sampled=%d frames=%d tries=%d acked=%d left=%d maxframe=%d" % (
        s["sampled"], s["frames"], s["tries"], s["acked"], len(state["flash"]["log"]), big))


if __name__ == "__main__":
    main()
