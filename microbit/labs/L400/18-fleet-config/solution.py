# Lab 18 - device side of fleet configuration (AFTER = build task solution).
# Two-phase, acknowledged, with probation and automatic rollback:
#   C:<dev>:<ver>:<cfg>  prepare -> validate, STAGE (do not run), reply K (staged) or N (invalid)
#   G:<dev>:<ver>        commit  -> only a staged version; keep last-good, apply, reply A every 500 ms
#   OK:<dev>:<ver>       confirm -> the gateway heard A on the new settings: probation over
#   no OK within PROBATION_MS -> roll back to last-good and reply R (e.g. a wrong radio group)
# Invariant: a device only runs a version the gateway acknowledged (it sent G after K).
from microbit import *
import radio

GROUP = 18
radio.config(group=GROUP)
LIMITS = {"i": (100, 60000), "th": (0, 50), "g": (0, 255)}
FACTORY = {"v": 1, "i": 1000, "th": 30, "g": GROUP}


def crc16(text):
    crc = 0xFFFF
    for ch in text:
        crc ^= ord(ch) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def encode(kind, dev, ver, payload=""):
    body = "{}:{}:{}:{}".format(kind, dev, ver, payload)
    return "{}:{:04X}".format(body, crc16(body))


def decode(text):
    body, sep, check = text.rpartition(":")
    if not sep or len(check) != 4:
        return None
    try:
        if int(check, 16) != crc16(body):
            return None
        kind, dev, ver, payload = body.split(":", 3)
        return kind, dev, int(ver), payload
    except ValueError:
        return None


def parse_cfg(ver, text):
    # "i=500;th=28;g=18" -> dict, or None if any key/value is unknown or out of range
    cfg = {"v": ver}
    try:
        for pair in text.split(";"):
            key, value = pair.split("=")
            lo, hi = LIMITS[key]
            if not lo <= int(value) <= hi:
                return None
            cfg[key] = int(value)
    except (KeyError, ValueError):
        return None
    return cfg if len(cfg) == len(LIMITS) + 1 else None


def device_id():
    try:
        import machine               # identity: the chip's unique id, never a typed-in name
        return "".join("%02x" % b for b in machine.unique_id())[-6:]
    except ImportError:
        return "stub"


PROBATION_MS = 3000
REPORT_MS = 500


def new_state(dev):
    return {"dev": dev, "cfg": dict(FACTORY), "good": dict(FACTORY), "staged": None,
            "probation": None, "next_report": 0,
            "stats": {"applied": 0, "rejected": 0, "rolled_back": 0}}


def apply(state, cfg):
    if cfg["g"] != state["cfg"]["g"]:
        radio.config(group=cfg["g"])
    state["cfg"] = cfg
    state["stats"]["applied"] += 1


def on_message(state, msg, now):
    kind, dev, ver, payload = msg
    if dev != state["dev"]:
        return
    if kind == "C":
        if ver <= state["cfg"]["v"]:
            radio.send(encode("A", dev, state["cfg"]["v"]))   # already running it
            return
        cfg = parse_cfg(ver, payload)
        if cfg is None:
            state["stats"]["rejected"] += 1
            radio.send(encode("N", dev, ver))
            return
        state["staged"] = cfg                                 # stage only: nothing runs yet
        radio.send(encode("K", dev, ver))
    elif kind == "G" and state["staged"] and state["staged"]["v"] == ver:
        state["good"] = state["cfg"]                          # last-good, for rollback
        apply(state, state["staged"])
        state["staged"] = None
        state["probation"] = now + PROBATION_MS
        state["next_report"] = now
    elif kind == "OK" and state["probation"] and ver == state["cfg"]["v"]:
        state["probation"] = None                             # confirmed: keep it
        state["good"] = state["cfg"]


def watchdog(state, now):
    if state["probation"] is None:
        return
    if now >= state["probation"]:                             # nobody confirmed: roll back
        bad = state["cfg"]["v"]
        apply(state, state["good"])
        state["probation"] = None
        state["stats"]["rolled_back"] += 1
        radio.send(encode("R", state["dev"], bad))
    elif now >= state["next_report"]:
        radio.send(encode("A", state["dev"], state["cfg"]["v"]))
        state["next_report"] = now + REPORT_MS


def step(state, now):
    while True:
        try:
            text = radio.receive()
        except ValueError:
            text = "?"
        if text is None:
            break
        msg = decode(text)
        if msg:
            on_message(state, msg, now)
    watchdog(state, now)


def main():
    state = new_state(device_id())
    while True:
        step(state, running_time())
        sleep(10)


if __name__ == "__main__":
    main()
