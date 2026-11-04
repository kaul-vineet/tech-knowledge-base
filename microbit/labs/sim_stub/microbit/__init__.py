"""Minimal CPython stub of the BBC micro:bit MicroPython V2 `microbit` module.

Purpose: run lab logic with `python -m unittest` on a PC. It is NOT the
simulator and NOT the device: no timing, no font rendering, no audio, no
real sensors. Only the API surface used by the L100/L200 labs is implemented,
following https://microbit-micropython.readthedocs.io/en/v2-docs/.

Test helpers (not part of the real API) start with an underscore or live on
the stub objects as `inject_*` / `press` / `release` / `click` methods.
Call `microbit._reset()` between tests: it mutates objects in place, so
names bound by `from microbit import *` stay valid.

L200 additions: full pin set (digital/analog/PWM/touch), `i2c` with simulated
devices (i2c_devices.py), and the sibling stub modules `radio` and `log`.
Two independent boards for radio tests: labtest.load_boards().

L300 additions: a timeline of scheduled inputs (`_at(t_ms, fn)`; `sleep()` and
the test helper `_advance(ms)` fire due events in time order), the `power`
stub (deep sleep), and seeded radio faults (`radio.Air(loss=..., seed=...)`).
"""

__all__ = [
    "display", "Image", "button_a", "button_b",
    "pin0", "pin1", "pin2", "pin3", "pin4", "pin5", "pin6", "pin7", "pin8", "pin9",
    "pin10", "pin11", "pin12", "pin13", "pin14", "pin15", "pin16", "pin19", "pin20",
    "pin_logo", "pin_speaker", "i2c", "accelerometer", "speaker", "audio", "Sound",
    "sleep", "running_time", "temperature", "set_volume", "scale",
]

_clock_ms = 0
_temperature_c = 20
_volume = 255


# ---------------------------------------------------------------- Image
class Image:
    """5x5 (or w x h) image; pixel brightness 0 (off) .. 9 (bright)."""

    def __init__(self, *args):
        self._readonly = False
        if not args:
            self._w, self._h = 5, 5
            self._px = [0] * 25
        elif len(args) == 1 and isinstance(args[0], str):
            rows = [r for r in args[0].replace("\n", ":").split(":") if r]
            self._h = len(rows)
            self._w = max(len(r) for r in rows)
            self._px = []
            for r in rows:
                self._px += [int(c) for c in r.ljust(self._w, "0")]
        elif len(args) in (2, 3):
            self._w, self._h = int(args[0]), int(args[1])
            buf = args[2] if len(args) == 3 else [0] * (self._w * self._h)
            self._px = [int(v) for v in buf]
        else:
            raise TypeError("unsupported Image() arguments")

    def width(self):
        return self._w

    def height(self):
        return self._h

    def get_pixel(self, x, y):
        return self._px[y * self._w + x]

    def set_pixel(self, x, y, value):
        if self._readonly:
            raise TypeError("image cannot be modified (try copying first)")
        if not 0 <= value <= 9:
            raise ValueError("brightness out of bounds")
        self._px[y * self._w + x] = value

    def fill(self, value):
        if self._readonly:
            raise TypeError("image cannot be modified (try copying first)")
        if not 0 <= value <= 9:
            raise ValueError("brightness out of bounds")
        self._px = [value] * (self._w * self._h)

    def copy(self):
        return Image(self._w, self._h, list(self._px))

    def invert(self):
        return Image(self._w, self._h, [9 - v for v in self._px])

    def __mul__(self, n):
        return Image(self._w, self._h, [max(0, min(9, round(v * n))) for v in self._px])

    def __add__(self, other):
        return Image(self._w, self._h,
                     [min(9, a + b) for a, b in zip(self._px, other._px)])

    def __eq__(self, other):
        return (isinstance(other, Image) and self._w == other._w
                and self._h == other._h and self._px == other._px)

    def __repr__(self):
        rows = ["".join(str(v) for v in self._px[i * self._w:(i + 1) * self._w])
                for i in range(self._h)]
        return "Image('" + ":".join(rows) + ":')"


def _builtin(s):
    img = Image(s)
    img._readonly = True
    return img


# A subset of the built-in images. Bitmaps are illustrative; tests compare
# against these same objects, never against hard-coded pixel data.
Image.HEART = _builtin("09090:99999:99999:09990:00900")
Image.HEART_SMALL = _builtin("00000:09090:09990:00900:00000")
Image.HAPPY = _builtin("00000:09090:00000:90009:09990")
Image.SAD = _builtin("00000:09090:00000:09990:90009")
Image.SURPRISED = _builtin("09090:00000:00900:09090:00900")
Image.ASLEEP = _builtin("00000:99099:00000:09990:00000")
Image.YES = _builtin("00000:00009:00090:90900:09000")
Image.NO = _builtin("90009:09090:00900:09090:90009")
Image.ARROW_N = _builtin("00900:09990:90909:00900:00900")
Image.ARROW_S = _builtin("00900:00900:90909:09990:00900")
Image.ARROW_E = _builtin("00900:00090:99999:00090:00900")
Image.ARROW_W = _builtin("00900:09000:99999:09000:00900")
Image.MUSIC_QUAVER = _builtin("00900:00990:00909:99900:99900")
Image.SQUARE = _builtin("99999:90009:90009:90009:99999")
Image.SQUARE_SMALL = _builtin("00000:09990:09090:09990:00000")
Image.TARGET = _builtin("00900:09990:99099:09990:00900")
Image.ANGRY = _builtin("90009:09090:00000:99999:90909")
Image.SKULL = _builtin("09990:90909:99999:09990:09990")


# ---------------------------------------------------------------- display
class _Display:
    def __init__(self):
        self._reset()

    def _reset(self):
        self._buf = Image()
        self.history = []          # [("show"|"scroll"|"clear", value)]
        self.last_text = None      # last str/int shown or scrolled
        self._on = True
        self._light = 127

    # real API
    def show(self, image, delay=400, *, wait=True, loop=False, clear=False):
        self.history.append(("show", image))
        if isinstance(image, Image):
            self._buf = image.copy()
        else:
            self.last_text = str(image)
        if clear:
            self.clear()

    def scroll(self, text, delay=150, *, wait=True, loop=False, monospace=False):
        self.history.append(("scroll", str(text)))
        self.last_text = str(text)

    def clear(self):
        self.history.append(("clear", None))
        self._buf = Image()

    def get_pixel(self, x, y):
        return self._buf.get_pixel(x, y)

    def set_pixel(self, x, y, value):
        if not 0 <= value <= 9:
            raise ValueError("brightness out of bounds")
        self._buf._px[y * 5 + x] = value

    def on(self):
        self._on = True

    def off(self):
        self._on = False

    def is_on(self):
        return self._on

    def read_light_level(self):
        return self._light

    # test helpers
    def current_image(self):
        return self._buf.copy()

    def inject_light_level(self, value):
        if not 0 <= value <= 255:
            raise ValueError("light level is 0..255")
        self._light = value


display = _Display()


# ---------------------------------------------------------------- buttons
class _Button:
    def __init__(self, name):
        self.name = name
        self._reset()

    def _reset(self):
        self._down = False
        self._was = False
        self._presses = 0

    # real API
    def is_pressed(self):
        return self._down

    def was_pressed(self):
        was, self._was = self._was, False
        return was

    def get_presses(self):
        n, self._presses = self._presses, 0
        return n

    # test helpers
    def press(self):
        if not self._down:
            self._down = True
            self._was = True
            self._presses += 1

    def release(self):
        self._down = False

    def click(self, times=1):
        for _ in range(times):
            self.press()
            self.release()


button_a = _Button("A")
button_b = _Button("B")


# ---------------------------------------------------------------- pins
# Pin model per https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html
# (classes MicroBitDigitalPin / MicroBitAnalogDigitalPin / MicroBitTouchPin).
# Inputs are injected by tests (inject_digital / inject_analog / inject_touch);
# outputs are recorded (digital_out, duty, period_us, history).
_ANALOG_PINS = (0, 1, 2, 3, 4, 10)
_TOUCH_PINS = (0, 1, 2)
_MODES = ("unused", "analog", "read_digital", "write_digital", "display", "button",
          "music", "audio", "touch", "i2c", "spi")


class _DigitalPin:
    PULL_UP, PULL_DOWN, NO_PULL = 1, 0, 2       # stub values; only the names are documented
    RESISTIVE, CAPACITIVE = 0, 1

    def __init__(self, name):
        self.name = name
        self._reset()

    def _reset(self):
        self._mode = "unused"
        self._pull = self.NO_PULL
        self._digital_in = 0
        self._analog_in = 0
        self._touched = False
        self._touch_mode = self.RESISTIVE
        self.digital_out = None
        self.duty = None
        self.period_us = 20000      # stub default; the docs do not state the device default
        self.history = []           # [("digital", 0|1) | ("analog", duty)]

    # MicroBitDigitalPin
    def read_digital(self):
        self._mode, self._pull = "read_digital", self.PULL_DOWN   # documented default pull
        return self._digital_in

    def write_digital(self, value):
        if value not in (0, 1):     # True/False compare equal to 1/0
            raise ValueError("value must be 0 or 1")
        self._mode, self.digital_out, self.duty = "write_digital", int(value), None
        self.history.append(("digital", int(value)))

    def set_pull(self, value):
        self._mode, self._pull = "read_digital", value

    def get_pull(self):
        return self._pull

    def get_mode(self):
        return self._mode

    def write_analog(self, value):
        if not 0 <= value <= 1023:
            raise ValueError("value must be between 0 and 1023")
        self._mode, self.duty, self.digital_out = "analog", value, None
        self.history.append(("analog", value))

    def set_analog_period(self, period):
        if period < 1:
            raise ValueError("invalid period")
        self.period_us = int(period) * 1000

    def set_analog_period_microseconds(self, period):
        if period < 256:
            raise ValueError("invalid period")
        self.period_us = int(period)

    def get_analog_period_microseconds(self):
        return self.period_us

    # test helpers
    def inject_digital(self, level):
        self._digital_in = 1 if level else 0

    def inject_touch(self, touched=True):
        self._touched = bool(touched)


class _AnalogDigitalPin(_DigitalPin):
    def read_analog(self):
        self._mode, self._pull = "analog", self.NO_PULL
        return self._analog_in

    def inject_analog(self, value):
        if not 0 <= value <= 1023:
            raise ValueError("analog input is 0..1023")
        self._analog_in = int(value)


class _TouchPin(_AnalogDigitalPin):
    def is_touched(self):
        self._mode, self._pull = "touch", self.PULL_UP
        return self._touched

    def set_touch_mode(self, value):
        self._touch_mode = value


class _LogoPin:
    """pin_logo (V2): touch only, capacitive by default."""
    RESISTIVE, CAPACITIVE = 0, 1

    def __init__(self, name):
        self.name = name
        self._reset()

    def _reset(self):
        self._touched = False
        self._touch_mode = self.CAPACITIVE

    def is_touched(self):
        return self._touched

    def set_touch_mode(self, value):
        self._touch_mode = value

    def inject_touch(self, touched=True):
        self._touched = bool(touched)


def _make_pin(n):
    if n in _TOUCH_PINS:
        return _TouchPin("pin%d" % n)
    if n in _ANALOG_PINS:
        return _AnalogDigitalPin("pin%d" % n)
    return _DigitalPin("pin%d" % n)


_PIN_NUMBERS = tuple(range(17)) + (19, 20)   # pins 17 and 18 do not exist
_PINS = {n: _make_pin(n) for n in _PIN_NUMBERS}
pin0, pin1, pin2, pin3, pin4, pin5, pin6, pin7, pin8 = (_PINS[n] for n in range(9))
pin9, pin10, pin11, pin12, pin13, pin14, pin15, pin16 = (_PINS[n] for n in range(9, 17))
pin19, pin20 = _PINS[19], _PINS[20]
pin_logo = _LogoPin("pin_logo")
pin_speaker = _DigitalPin("pin_speaker")     # PWM only on the device


# ---------------------------------------------------------------- i2c
# API per https://microbit-micropython.readthedocs.io/en/v2-docs/i2c.html.
# Errors follow micropython-microbit-v2 src/codal_port/microbit_i2c.c:
# a failed read/write raises OSError(ENODEV = 19) ("assume ... no I2C device").
# SIMULATED DEVICES ONLY: the browser simulator cannot attach I2C devices; tests
# attach Python models (see i2c_devices.py) with i2c._attach(addr, device).
ENODEV = 19


class _I2C:
    def __init__(self):
        self._devices = {}
        self._reset()

    def _reset(self):
        self._devices.clear()
        self.freq, self.sda, self.scl = 100000, pin20, pin19
        self.transactions = []      # [("write", addr, bytes) | ("read", addr, bytes)]

    def init(self, freq=100000, sda=pin20, scl=pin19):
        self.freq, self.sda, self.scl = freq, sda, scl

    def scan(self):
        # 7-bit addresses 0x08..0x77 (0b0000xxx and 0b1111xxx are reserved)
        return [a for a in range(0x08, 0x78) if a in self._devices]

    def read(self, addr, n, repeat=False):
        dev = self._devices.get(addr)
        if dev is None:
            raise OSError(ENODEV)
        data = bytes(dev.i2c_read(n))
        self.transactions.append(("read", addr, data))
        return data

    def write(self, addr, buf, repeat=False):
        data = bytes(buf)
        dev = self._devices.get(addr)
        if dev is None:
            raise OSError(ENODEV)
        self.transactions.append(("write", addr, data))
        dev.i2c_write(data)

    # test helpers
    def _attach(self, addr, device):
        if not 0 <= addr <= 0x7F:
            raise ValueError("7-bit address expected")
        self._devices[addr] = device

    def _detach(self, addr):
        self._devices.pop(addr, None)


i2c = _I2C()


# ---------------------------------------------------------------- accelerometer
_GESTURES = ("up", "down", "left", "right", "face up", "face down",
             "freefall", "3g", "6g", "8g", "shake")


class _Accelerometer:
    def __init__(self):
        self._reset()

    def _reset(self):
        self._xyz = [0, 0, -1024]
        self._current = ""
        self._since_last = set()
        self._history = []

    # real API
    def get_x(self):
        return self._xyz[0]

    def get_y(self):
        return self._xyz[1]

    def get_z(self):
        return self._xyz[2]

    def get_values(self):
        return tuple(self._xyz)

    def get_strength(self):
        return int(sum(v * v for v in self._xyz) ** 0.5)

    def current_gesture(self):
        return self._current

    def is_gesture(self, name):
        return self._current == name

    def was_gesture(self, name):
        hit = name in self._since_last
        self._since_last.discard(name)
        return hit

    def get_gestures(self):
        h, self._history = tuple(self._history), []
        return h

    # test helpers
    def inject_axes(self, x=None, y=None, z=None):
        for i, v in enumerate((x, y, z)):
            if v is not None:
                self._xyz[i] = int(v)

    def inject_gesture(self, name):
        if name and name not in _GESTURES:
            raise ValueError("unknown gesture: %r" % name)
        self._current = name
        if name:
            self._since_last.add(name)
            self._history.append(name)


accelerometer = _Accelerometer()


# ---------------------------------------------------------------- sound
sound_log = []   # shared recorder: (source, payload, speaker_on)


class _Speaker:
    def __init__(self):
        self._reset()

    def _reset(self):
        self._on = True

    def on(self):
        self._on = True

    def off(self):
        self._on = False

    def is_on(self):
        return self._on


speaker = _Speaker()


class Sound:
    GIGGLE = "giggle"
    HAPPY = "happy"
    HELLO = "hello"
    MYSTERIOUS = "mysterious"
    SAD = "sad"
    SLIDE = "slide"
    SOARING = "soaring"
    SPRING = "spring"
    TWINKLE = "twinkle"
    YAWN = "yawn"


class _SoundEffect:
    # Only the defaults (WAVEFORM_SQUARE=3, FX_NONE=0, SHAPE_LOG=18) match the
    # repr() shown in the docs; other numeric values are placeholders.
    WAVEFORM_SINE, WAVEFORM_SAWTOOTH, WAVEFORM_TRIANGLE, WAVEFORM_SQUARE, WAVEFORM_NOISE = 0, 1, 2, 3, 4
    SHAPE_LINEAR, SHAPE_CURVE, SHAPE_LOG = 1, 2, 18
    FX_NONE, FX_TREMOLO, FX_VIBRATO, FX_WARBLE = 0, 2, 1, 3

    def __init__(self, freq_start=500, freq_end=2500, duration=500, vol_start=255,
                 vol_end=0, waveform=3, fx=0, shape=18):
        for name, val, hi in (("freq_start", freq_start, 9999), ("freq_end", freq_end, 9999),
                              ("duration", duration, 9999), ("vol_start", vol_start, 255),
                              ("vol_end", vol_end, 255)):
            if not 0 <= val <= hi:
                raise ValueError("%s out of range" % name)
        self.freq_start, self.freq_end, self.duration = freq_start, freq_end, duration
        self.vol_start, self.vol_end = vol_start, vol_end
        self.waveform, self.fx, self.shape = waveform, fx, shape

    def copy(self):
        return _SoundEffect(self.freq_start, self.freq_end, self.duration, self.vol_start,
                            self.vol_end, self.waveform, self.fx, self.shape)


class _Audio:
    SoundEffect = _SoundEffect

    def __init__(self):
        self._reset()

    def _reset(self):
        self.played = []

    def play(self, source, wait=True, pin=None, return_pin=None):
        self.played.append(source)
        sound_log.append(("audio", source, speaker.is_on()))

    def is_playing(self):
        return False

    def stop(self):
        pass


audio = _Audio()


# ---------------------------------------------------------------- misc
# L300: a timeline of scheduled input changes (test helper). sleep() fires every
# event whose time falls inside the sleep, in time order, so a 150 ms button tap
# that starts and ends during sleep(1000) really happens while the program waits.
_timeline = []      # heap of (t_ms, seq, fn)
_seq = [0]


def _at(t_ms, fn):
    """Schedule fn() to run when the stub clock reaches t_ms (test helper)."""
    import heapq
    _seq[0] += 1
    heapq.heappush(_timeline, (int(t_ms), _seq[0], fn))


def _advance_to(target, stop=None):
    """Move the clock to target, firing due events; stop() -> True ends early."""
    import heapq
    global _clock_ms
    while _timeline and _timeline[0][0] <= target:
        t, _, fn = heapq.heappop(_timeline)
        _clock_ms = max(_clock_ms, t)
        fn()
        if stop is not None and stop():
            return _clock_ms
    _clock_ms = max(_clock_ms, int(target))
    return _clock_ms


def _advance(ms):
    """Let time pass without the program calling sleep() (busy loop, test helper)."""
    _advance_to(_clock_ms + int(ms))


def sleep(ms):
    _advance_to(_clock_ms + int(ms))


def running_time():
    return _clock_ms


def temperature():
    return _temperature_c


def set_volume(volume):
    global _volume
    if not 0 <= volume <= 255:
        raise ValueError("volume is 0..255")
    _volume = volume


def scale(value, from_, to):
    (a, b), (c, d) = from_, to
    out = c + (value - a) * (d - c) / (b - a)
    return out if isinstance(c, float) or isinstance(d, float) else int(round(out))


# ---------------------------------------------------------------- test helpers
def _inject_temperature(celsius):
    global _temperature_c
    _temperature_c = int(celsius)


def _reset():
    """Reset all stub state in place (call in unittest setUp)."""
    global _clock_ms, _temperature_c, _volume
    _clock_ms, _temperature_c, _volume = 0, 20, 255
    del _timeline[:]
    for obj in (display, button_a, button_b, pin_logo, pin_speaker,
                accelerometer, speaker, audio, i2c):
        obj._reset()
    for pin in _PINS.values():
        pin._reset()
    del sound_log[:]
    import sys
    for name in ("music", "radio", "log", "power"):   # sibling stubs, reset only if imported
        mod = sys.modules.get(name)
        if mod is not None and hasattr(mod, "_reset"):
            mod._reset()
    try:
        import music
        music._reset()
    except ImportError:
        pass
