"""Stub of the micro:bit MicroPython `music` module: records calls, makes no sound.

API per https://microbit-micropython.readthedocs.io/en/v2-docs/music.html
"""
import microbit

_ticks, _bpm = 4, 120
played = []    # list of ("play", notes) / ("pitch", (freq, duration)) / ("stop", None)

# Built-in tunes exist on the device; here they are placeholder note lists.
BA_DING = ["b5:1", "e6:3"]
POWER_UP = ["g4:1", "c5", "e", "g:2", "e:1", "g:3"]
JUMP_UP = ["c5:1", "d", "e", "f", "g"]


def _record(kind, payload):
    played.append((kind, payload))
    microbit.sound_log.append(("music", (kind, payload), microbit.speaker.is_on()))


def set_tempo(ticks=4, bpm=120):
    global _ticks, _bpm
    _ticks, _bpm = ticks, bpm


def get_tempo():
    return (_ticks, _bpm)


def play(music, pin=None, wait=True, loop=False):
    notes = [music] if isinstance(music, str) else list(music)
    _record("play", notes)


def pitch(frequency, duration=-1, pin=None, wait=True):
    _record("pitch", (int(frequency), duration))


def stop(pin=None):
    _record("stop", None)


def reset():
    set_tempo()


def _reset():
    reset()
    del played[:]
