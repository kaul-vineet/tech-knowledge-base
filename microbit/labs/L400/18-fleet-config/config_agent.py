# Lab 18 - device side of fleet configuration (BEFORE the design review).
# Config = version + key=value pairs: i (sample interval ms), th (temperature alarm C), g (radio group).
# Gateway -> device: C:<dev>:<ver>:<cfg>   Device -> gateway: A:<dev>:<ver> (applied), N (invalid)
# One-phase: the device APPLIES a new config the moment it arrives, then acks. If the ack is lost,
# or the new config cuts the device off (wrong radio group), it runs a config nobody acknowledged.
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


def new_state(dev):
    return {"dev": dev, "cfg": dict(FACTORY), "stats": {"applied": 0, "rejected": 0}}


def apply(state, cfg):
    if cfg["g"] != state["cfg"]["g"]:
        radio.config(group=cfg["g"])
    state["cfg"] = cfg
    state["stats"]["applied"] += 1


def on_message(state, msg, now):
    kind, dev, ver, payload = msg
    if dev != state["dev"] or kind != "C":
        return
    if ver <= state["cfg"]["v"]:
        radio.send(encode("A", dev, state["cfg"]["v"]))     # already running: ack again
        return
    cfg = parse_cfg(ver, payload)
    if cfg is None:
        state["stats"]["rejected"] += 1
        radio.send(encode("N", dev, ver))
        return
    apply(state, cfg)                                        # one-phase: run it now ...
    radio.send(encode("A", dev, ver))                        # ... and hope the ack arrives


def step(state, now):
    while True:
        try:
            text = radio.receive()
        except ValueError:
            text = "?"
        if text is None:
            return
        msg = decode(text)
        if msg:
            on_message(state, msg, now)


def main():
    state = new_state(device_id())
    while True:
        step(state, running_time())
        sleep(10)


if __name__ == "__main__":
    main()
