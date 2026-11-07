from . import LOG
from .ev3devices import _num
from .parameters import Color, _Enum


def _color(c):
    if not isinstance(c, _Enum) or not repr(c).startswith("Color."):
        raise TypeError("expected a Color, got %r" % (c,))
    return c


class _Light:
    def on(self, color):  LOG.append(("light_on", repr(_color(color))))
    def off(self):        LOG.append(("light_off",))


class _Speaker:
    def beep(self, frequency=500, duration=100):
        _num("frequency", frequency, 0); _num("duration", duration)
        LOG.append(("beep", frequency, duration))

    def play_notes(self, notes, tempo=120):
        notes = list(notes)
        for n in notes:
            if not isinstance(n, str):
                raise TypeError("every note must be a string, got %r" % (n,))
        _num("tempo", tempo, 1)
        LOG.append(("play_notes", notes, tempo))

    def say(self, text):
        LOG.append(("say", str(text)))

    def volume(self, *args):
        if args:
            _num("volume", args[0], 0, 100)
            LOG.append(("volume", args[0]))
            return None
        return 100


class _Screen:
    width, height = 178, 128

    def clear(self):
        LOG.append(("screen_clear",))

    def print(self, *args, **kw):
        LOG.append(("screen_print",) + tuple(str(a) for a in args))

    def draw_text(self, x, y, text, text_color=Color.BLACK, background_color=None):
        _num("x", x); _num("y", y)
        LOG.append(("draw_text", x, y, str(text)))

    def draw_box(self, x1, y1, x2, y2, r=0, fill=False, color=Color.BLACK):
        for n, v in (("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)):
            _num(n, v)
        LOG.append(("draw_box", x1, y1, x2, y2, bool(fill)))

    def draw_circle(self, x, y, r, fill=False, color=Color.BLACK):
        _num("x", x); _num("y", y); _num("r", r, 0)
        LOG.append(("draw_circle", x, y, r, bool(fill)))

    def draw_line(self, x1, y1, x2, y2, width=1, color=Color.BLACK):
        for n, v in (("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)):
            _num(n, v)
        LOG.append(("draw_line", x1, y1, x2, y2))

    def draw_pixel(self, x, y, color=Color.BLACK):
        LOG.append(("draw_pixel", x, y))


class _Keypad:
    def pressed(self):
        LOG.append(("buttons_pressed",))
        return set()


class _Battery:
    def voltage(self): return 8000
    def current(self): return 100


class EV3Brick:
    def __init__(self):
        self.light = _Light(); self.speaker = _Speaker()
        self.screen = _Screen(); self.buttons = _Keypad()
        self.battery = _Battery()
        LOG.append(("EV3Brick",))
