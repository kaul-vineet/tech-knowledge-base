# Lab 15 - device side: send readings to the PC as framed serial lines.
# Frame:  $LLL<payload>*CCCC   then a line end
#   $      start marker: the gateway resynchronises on it after garbage
#   LLL    payload length, 3 decimal digits: catches dropped or extra bytes
#   *CCCC  CRC-16/CCITT-FALSE of the payload, 4 hex digits: catches flipped bits
# payload: "<seq>,<temp>,<light>"  (never contains $ * or a line end)
from microbit import *

PERIOD_MS = 500


def crc16(text):
    crc = 0xFFFF
    for ch in text:
        crc ^= ord(ch) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def frame(payload):
    return "${:03d}{}*{:04X}".format(len(payload), payload, crc16(payload))


def new_state():
    return {"seq": 0}


def step(state):
    state["seq"] += 1
    payload = "{},{},{}".format(state["seq"], temperature(), display.read_light_level())
    print(frame(payload))          # print adds the line end


def main():
    state = new_state()
    while True:
        step(state)
        sleep(PERIOD_MS)


if __name__ == "__main__":
    main()
