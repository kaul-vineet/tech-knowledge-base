"""Seeded attack scenario on the stub radio (CPython only).

Three sensors (n1..n3) send 60 sealed readings each over radio.Air(loss 10 %, dup 5 %, reorder 10 %,
corrupt 2 %). Eve, another radio in range, records every frame. After 30 readings she:
  replays  20 recorded frames (a real "temp 21" from earlier, again)
  forges   20 frames "n1:<fresh ctr>:45,100,0" (45 C -> a false TEMP_HIGH) with the best tag she can
           make: CRC -> recompute it; toy -> recover the 16-bit CRC state from 2 frames, then tag;
           siphash -> no key, so a random 64-bit tag (and the same toy state attack, which fails).
The gateway runs a verifier (verifier.py = BEFORE, solution.py = AFTER) on everything it hears.
Demo keys come from a seeded RNG; real keys are random (secrets.token_bytes(16)), provisioned
over USB once, kept on the device and the gateway only.
"""
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "sim_stub"))
import frame_auth as fa  # noqa: E402
import radio as radio_stub  # noqa: E402

DEVICES = ("n1", "n2", "n3")
FAULTS = dict(loss=0.10, dup=0.05, reorder=0.10, corrupt=0.02)
STRING = radio_stub.STRING_HEADER


def load_verifier(filename):
    path = Path(filename) if Path(filename).is_absolute() else HERE / filename
    spec = importlib.util.spec_from_file_location("verifier_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Verifier


def recover_toy_state(frames):
    """CRC is affine: crc16(key + msg) == crc16(msg, start=crc16(key)). Try all 65,536 starts."""
    hits = [s for s in range(65536) if all(fa.crc16(b, s) == t for b, t in frames[:1])]
    hits = [s for s in hits if all(fa.crc16(b, s) == t for b, t in frames[1:])]
    return hits[0] if len(hits) == 1 else None


def forge_tag(mode, body, toy_state, rng):
    if mode == "crc":
        return "%04x" % fa.crc16(body.encode())
    if mode == "toy" and toy_state is not None:
        return "%04x" % fa.crc16(body.encode(), toy_state)
    return "%016x" % rng.getrandbits(64) if mode == "siphash" else "%04x" % rng.getrandbits(16)


def run(verifier_file="solution.py", mode="siphash", seed=19, n=60):
    rng = random.Random(seed)
    keys = dict((d, bytes(rng.getrandbits(8) for _ in range(16))) for d in DEVICES)
    air = radio_stub.Air(seed=seed, **FAULTS)
    eps = dict((d, radio_stub.Endpoint(air, d)) for d in DEVICES + ("eve", "gw"))
    for ep in eps.values():
        ep.config(length=64, queue=50)                  # a 64-bit tag in hex needs more than 32 bytes
    ver = load_verifier(verifier_file)(keys, mode=mode)     # verifier.py ignores mode: CRC only
    m = {"genuine_sent": 0, "genuine_intact": 0, "genuine_accepted": 0, "forged_accepted": 0, "replays_accepted": 0,
         "toy_state_recovered": False}
    heard, sent_ok = [], set()

    def deliver_all():
        for name in ("eve", "gw"):
            while True:
                text = eps[name].receive_bytes()
                if text is None:
                    break
                text = text[3:].decode("utf-8", "replace")
                if name == "eve":
                    heard.append(text)
                    continue
                if text in genuine:
                    intact.add(genuine[text])             # reached the gateway unmodified
                res = ver.check(text)
                if res is None:
                    continue
                if text in forged:
                    m["forged_accepted"] += 1
                elif text in replayed and (res[0], res[1]) in accepted:
                    m["replays_accepted"] += 1
                else:
                    accepted.add((res[0], res[1]))
    forged, replayed, accepted, intact, genuine = set(), set(), set(), set(), {}
    for i in range(1, n + 1):
        for d in DEVICES:
            frame = fa.seal(d, i, "%d,%d,0" % (20 + i % 2, 100 + i), keys[d], mode)
            genuine[frame] = (d, i)
            eps[d].send(frame)
            m["genuine_sent"] += 1
            sent_ok.add((d, i))
        deliver_all()
        if i == 30:
            n1 = [t for t in heard if t.startswith("n1:")][:2]
            pairs = [(t.rpartition(":")[0].encode(), int(t.rpartition(":")[2], 16)) for t in n1]
            toy_state = recover_toy_state(pairs) if mode in ("toy", "siphash") else None
            m["toy_state_recovered"] = toy_state is not None
            for k in range(20):
                old = heard[rng.randrange(len(heard))]
                replayed.add(old)
                eps["eve"].send(old)
                body = fa.body("n1", 30 + 3 + k, "45,100,0")
                fake = body + ":" + forge_tag(mode, body, toy_state, rng)
                forged.add(fake)
                eps["eve"].send(fake)
            deliver_all()
    m["genuine_intact"] = len(intact)
    m["genuine_accepted"] = len(accepted & sent_ok)
    m["rejected"] = ver.stats["rejected"]
    return m, ver


def line(verifier_file, mode, m):
    return json.dumps(dict({"verifier": verifier_file, "mode": mode}, **m))


if __name__ == "__main__":
    for vf, mode in (("verifier.py", "crc"), ("solution.py", "toy"), ("solution.py", "siphash")):
        print(line(vf, mode, run(vf, mode)[0]))
