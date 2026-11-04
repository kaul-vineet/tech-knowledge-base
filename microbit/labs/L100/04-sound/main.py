# Lab 04 - sound: music melodies and pitch, V2 built-in sounds, a custom
# SoundEffect, and switching the V2 speaker on/off.
# A = melody, B = speaker on/off, touch logo (V2) = sound effect.
from microbit import *
import music

# Note format: NOTE[octave][:ticks]; octave/ticks carry over to later notes.
# pitch + duration: c4 = 261.63 Hz; 1 tick = 125 ms at the default tempo.
TUNE = ["c4:2", "e", "g", "c5:4", "r:2", "g4:2", "c5:6"]

# V2 only. Rising triangle-wave sweep, 0.4 s.
# frequency over time: one slide from freq_start to freq_end.
SWEEP = audio.SoundEffect(freq_start=400, freq_end=2000, duration=400,
                          waveform=audio.SoundEffect.WAVEFORM_TRIANGLE)


def start():
    audio.play(Sound.HELLO)       # V2 built-in sound
    music.pitch(440, 200)         # concert A (A4 = 440 Hz) for 200 ms
    print("sound ready")


def step():
    if button_a.was_pressed():
        music.play(TUNE)          # blocking playback: the loop waits 2.5 s for the tune
        print("tune played")
    if button_b.was_pressed():
        if speaker.is_on():
            speaker.off()         # output taps: speaker closed, pin 0 output still works
        else:
            speaker.on()
        print("speaker", "on" if speaker.is_on() else "off")
    if pin_logo.is_touched():
        audio.play(SWEEP)
        print("effect played")


def main():
    start()
    while True:
        step()
        sleep(50)


if __name__ == "__main__":
    main()
