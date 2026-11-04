# Concept: registers over a two-wire bus

## Why it matters
Most add-on sensors (temperature, pressure, light, motion) talk I2C. Using one means reading its datasheet: the address, the register map and how bytes become a number. Getting one bit wrong gives confident nonsense, like 231 °C.

## Mental model
A **block of numbered mailboxes at a street address**. The address (0x48) picks the device; you first write which mailbox you want (the pointer register), then read its bytes.

```
micro:bit (controller)                       TMP102 at 0x48 (target)
i2c.write(0x48, b"\x00")   ── pointer = 0 (temperature) ─►
i2c.read(0x48, 2)          ◄── 0x15 0x80 ──  (12-bit value, MSB first)
decode: (0x15 << 4) | (0x80 >> 4) = 0x158 = 344 × 0.0625 = 21.5 °C
```

## How it works
1. **7-bit address.** The TMP102 answers at 0x48 with ADD0 to GND; `i2c.scan()` lists who answers → see lab step 1
2. **Write the pointer, then read.** One write of the register number, one read of two bytes, most significant first → see lab step 2
3. **Decode per datasheet.** 12 bits, left-justified, 0.0625 °C per step, two's complement for negatives → see lab step 3
4. **Errors are `OSError`.** The V2 firmware raises `OSError` 19 (`ENODEV`) when nothing answers; the lab prints it instead of crashing → see lab step 1
5. **Writing a register** is the same pointer byte followed by data bytes → see lab step 5

Worked example (`research/concept_examples_l200.py`): 21.5 °C travels as `0x15 0x80`. For −25 °C the bytes are `0xE7 0x00`, raw `0xE70` = 3696; subtracting 4096 gives −400 × 0.0625 = −25.0. Skip the sign step and you print 231.0.

**Simulator vs stub.** The browser simulator cannot attach I2C devices. The TMP102 here is a Python model in `labs/sim_stub/i2c_devices.py`, built from TI's register map and used only by unit tests.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Several sensors share two wires (pins 19/20) | Long cables or noisy places (I2C is board-level) |
| The device has a datasheet with a register map | You need high-speed streaming |
| You can decode and unit-test bytes first | The address clashes with another device |

## Common mistakes
- Using an 8-bit address (0x90) where MicroPython expects 7-bit (0x48).
- Forgetting the pointer write, so you read whichever register was last selected.
- Ignoring the sign bit.
