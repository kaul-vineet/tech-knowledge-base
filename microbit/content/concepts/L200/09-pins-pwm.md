# Concept: digital, analog and PWM on the edge connector

## Why it matters
LEDs, motors, switches and potentiometers connect to the gold pins. You must know what a pin can do, what number it takes or gives, and whether an input is a level or an event.

## Mental model
A pin is a **light switch you can flick very fast**. Digital: on (3.3 V) or off (0 V). PWM: flick it on and off every period; the fraction of time "on" (duty) is what a LED or motor feels.

```
write_analog(511), period 20 ms:   ▇▇▇▇▇_____▇▇▇▇▇_____   on 9.99 ms / 20 ms = 50 % ≈ 1.65 V average
write_digital(1):                  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇   3.3 V
```

## How it works
1. **Digital output.** `pin1.write_digital(1)` drives 3.3 V, `0` drives 0 V: the on/off indicator → see lab step 2
2. **PWM output.** `pin2.write_analog(0..1023)` sets the duty; `set_analog_period(20)` sets 20 ms (50 Hz). The lab maps level 0-4 to duty `level * 1023 // 4` → see lab step 3
3. **Touch is a level; you want the edge.** `is_touched()` is True for as long as the finger stays, so the lab compares with the previous poll to toggle once. The logo is capacitive; pins 0-2 are resistive by default (touch GND too) → see lab step 2
4. **Analog input.** `read_analog()` returns 0 (0 V) to 1023 (3.3 V) on pins 0-4 and 10; the simulator's pins only take touch values 0/1 today → see lab step 6

Worked example (`research/concept_examples_l200.py`): levels 0-4 give duty 0, 255, 511, 767, 1023, that is 0, 25, 50, 75 and 100 %, averaging 0.00, 0.82, 1.65, 2.47 and 3.30 V; at 50 % the pin is on 9.99 ms of every 20 ms.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| PWM: LED brightness, motor speed, servo pulses | You need a clean analog voltage or audio waveform |
| Digital: on/off loads and indicators | The load needs more current than a pin gives |
| Touch: foil pads or the logo | Robust switches matter: use a real button |

## Common mistakes
- Toggling on `is_touched()` without edge detection, so holding flips state every poll.
- Expecting `read_analog()` values from the simulator's pin buttons.
- Using a display column pin (V2: 3, 4, 6, 7, 10) while the display is on.
