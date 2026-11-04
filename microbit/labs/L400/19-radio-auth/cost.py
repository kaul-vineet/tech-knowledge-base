"""What authentication costs per frame (prints JSON lines; CPython numbers are NOT micro:bit numbers).

rounds   SipRounds for one frame: 2 per 8-byte word (message + length byte) + 4 finalization
ops64    14 64-bit operations per SipRound (paper, section 6); a 32-bit Cortex-M4 needs several
         instructions per 64-bit op, and MicroPython big integers cost more - measure in the simulator
bytes    bytes the tag adds on air (hex text here; send_bytes() with raw bytes would add 8)
flash    counter-block writes for 1,000 frames with a 100-number block
"""
import json
import time

import frame_auth as fa

KEY = bytes(range(16))
BODY = fa.body("n1", 1234, "21,112,0").encode()


def per_frame():
    words = len(BODY) // 8 + 1
    rows = []
    for mode, tag_hex in (("crc", 4), ("toy", 4), ("siphash", 16)):
        t0 = time.perf_counter()
        for _ in range(2000):
            fa.seal("n1", 1234, "21,112,0", KEY, mode)
        us = (time.perf_counter() - t0) / 2000 * 1e6
        row = {"mode": mode, "tag_bytes_on_air": tag_hex + 1, "cpython_us_per_tag": round(us, 1)}
        if mode == "siphash":
            row.update(rounds=2 * words + 4, ops64=14 * (2 * words + 4))
        rows.append(row)
    return rows


def flash_writes(frames=1000, block=100):
    store = {"v": 0}
    c = fa.Counter(lambda: store["v"], lambda v: store.update(v=v), block)
    for _ in range(frames):
        c.take()
    return c.writes


if __name__ == "__main__":
    for row in per_frame():
        print(json.dumps(row))
    print(json.dumps({"counter_flash_writes_per_1000_frames": flash_writes()}))
