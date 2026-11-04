"""SIMULATED I2C devices for the stub's `microbit.i2c` bus (unit tests only).

The browser simulator cannot attach real or simulated I2C devices; these Python
models exist only so lab logic (bytes, addresses, register maps, errors) can be
tested on a PC. They are NOT part of MicroPython and NOT in the simulator.

TMP102 register map from the TI datasheet (SBOS397I, rev. June 2024):
  7-bit address 0x48 with ADD0 to GND (0x49 V+, 0x4A SDA, 0x4B SCL)
  pointer 0x00 temperature (read-only), 0x01 configuration, 0x02 T_LOW, 0x03 T_HIGH
  12-bit two's complement, left-justified in 2 bytes (MSB first), 0.0625 C per LSB
  power-up: configuration 0x60A0, T_LOW 75 C, T_HIGH 80 C, pointer 0x00
Not modelled: extended mode, shutdown/one-shot timing, ALERT pin, conversion delay.
"""

LSB_C = 0.0625


def c_to_word(celsius):
    """Temperature -> 16-bit register word (12-bit two's complement << 4)."""
    raw = int(round(celsius / LSB_C)) & 0xFFF
    return raw << 4


def word_to_c(word):
    raw = (word >> 4) & 0xFFF
    if raw & 0x800:
        raw -= 0x1000
    return raw * LSB_C


class TMP102:
    REG_TEMP, REG_CONFIG, REG_TLOW, REG_THIGH = 0, 1, 2, 3

    def __init__(self, celsius=21.5):
        self.pointer = self.REG_TEMP
        self.regs = {self.REG_TEMP: c_to_word(celsius), self.REG_CONFIG: 0x60A0,
                     self.REG_TLOW: c_to_word(75), self.REG_THIGH: c_to_word(80)}

    # test helper: what the sensor "measures"
    def set_temperature(self, celsius):
        self.regs[self.REG_TEMP] = c_to_word(celsius)

    # bus side (called by microbit.i2c)
    def i2c_write(self, data):
        if not data:
            return
        if data[0] & 0xFC:                 # P7..P2 must be 0
            raise OSError(19)              # stub: treat as NACK -> ENODEV like the firmware
        self.pointer = data[0] & 0x03
        if len(data) >= 3 and self.pointer != self.REG_TEMP:   # temperature is read-only
            self.regs[self.pointer] = (data[1] << 8) | data[2]
        elif len(data) == 2 and self.pointer != self.REG_TEMP:  # MSB-only update
            self.regs[self.pointer] = (data[1] << 8) | (self.regs[self.pointer] & 0xFF)

    def i2c_read(self, n):
        word = self.regs[self.pointer]
        out = bytes([(word >> 8) & 0xFF, word & 0xFF])
        return (out * ((n + 1) // 2))[:n]
