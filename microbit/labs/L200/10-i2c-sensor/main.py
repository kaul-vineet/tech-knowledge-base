# Lab 10 - an external temperature sensor over I2C (TMP102 register map).
# Wiring on a real board: SCL -> pin19, SDA -> pin20, GND, 3V; ADD0 -> GND.
# The browser simulator has NO I2C devices: expect "no device" there.
# Unit tests attach a simulated TMP102 (labs/sim_stub/i2c_devices.py).
from microbit import *

ADDR = 0x48            # 7-bit address (TMP102 with ADD0 to GND)
REG_TEMP = 0x00        # pointer register values: temperature (read-only)
REG_CONFIG = 0x01      # configuration, power-up value 0x60A0
LSB_C = 0.0625         # 12-bit result: one step = 0.0625 C


def decode_temp(msb, lsb):
    # 12-bit two's complement, left-justified: MSB holds bits 11..4, LSB bits 3..0
    raw = (msb << 4) | (lsb >> 4)
    if raw & 0x800:                      # sign bit set -> negative temperature
        raw -= 4096
    return raw * LSB_C


def read_register(reg, n=2):
    i2c.write(ADDR, bytes([reg]))        # 1) set the pointer register
    return i2c.read(ADDR, n)             # 2) read n bytes, most significant first


def read_temp_c():
    data = read_register(REG_TEMP)
    return decode_temp(data[0], data[1])


def step():
    # an I2C error is an OSError; 19 (ENODEV) = nothing answered at ADDR
    try:
        t = read_temp_c()
    except OSError as e:
        print("i2c: no device at {} (errno {})".format(hex(ADDR), e.args[0]))
        display.show(Image.NO, wait=False)
        return None
    print("temp_c={:.2f}".format(t))
    display.show(Image.YES if t < 30 else Image.ANGRY, wait=False)
    return t


def main():
    print("scan:", [hex(a) for a in i2c.scan()])   # which addresses answer?
    while True:
        step()
        sleep(1000)


if __name__ == "__main__":
    main()
