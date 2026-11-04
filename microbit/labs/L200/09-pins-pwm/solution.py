# Lab 09 - SOLUTION of the build task: potentiometer on pin0 sets the duty.
# Lab 09 - pins and PWM: a dimmer on the edge connector.
# Inputs:  touch logo = on/off, A/B = brightness level, touch pin0 = boost.
# Outputs: pin1 = on/off indicator (digital), pin2 = LED brightness (PWM).
from microbit import *

LEVELS = 4                      # brightness steps 0..LEVELS
PERIOD_MS = 20                  # PWM period: 20 ms = 50 Hz
USE_POT = True                  # build task: pin0 analog input (0..1023) replaces A/B + boost
pin2.set_analog_period(PERIOD_MS)


def duty_for(level):
    # write_analog takes 0 (0 % duty) .. 1023 (100 % duty)
    return level * 1023 // LEVELS


def new_state():
    return {"on": False, "level": 2, "logo_was": False, "last": None}


def step(state):
    # edge detect: is_touched() is a level ("touched now"), we want the moment it starts
    touched = pin_logo.is_touched()
    if touched and not state["logo_was"]:
        state["on"] = not state["on"]
    state["logo_was"] = touched
    if button_a.was_pressed():
        state["level"] = min(LEVELS, state["level"] + 1)
    if button_b.was_pressed():
        state["level"] = max(0, state["level"] - 1)
    duty = 0
    if state["on"] and USE_POT:
        duty = pin0.read_analog()   # build task: 0 V -> 0 .. 3.3 V -> 1023, same scale as PWM
    elif state["on"]:
        boost = pin0.is_touched()   # pin0..2 touch is resistive by default (touch GND too)
        duty = 1023 if boost else duty_for(state["level"])
    pin1.write_digital(1 if state["on"] else 0)    # digital output: 0 V or 3.3 V
    pin2.write_analog(duty)                        # PWM output: average voltage = duty/1023 * 3.3 V
    report = (state["on"], state["level"], duty)
    if report != state["last"]:                    # print only changes
        print("on={},level={},duty={}".format(int(state["on"]), state["level"], duty))
        state["last"] = report
    return duty


def main():
    print("logo = on/off, A/B = level, pin0 = boost")
    state = new_state()
    while True:
        step(state)
        sleep(50)


if __name__ == "__main__":
    main()
