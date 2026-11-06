"""The NXT sensors, as the real pybricks.nxtdevices has them.

Signatures are from pybricks/pybricks-api src/pybricks/nxtdevices.py. The log
names carry an nxt prefix because the NXT touch, colour and ultrasonic
sensors share their names with the EV3 ones, and a test has to be able to
tell which of the two a generated program actually built.
"""

from . import LOG
from .ev3devices import _sport


class TouchSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("NXTTouchSensor", self.port))
    def pressed(self):
        LOG.append(("nxt_pressed", self.port)); return False


class LightSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("NXTLightSensor", self.port))
    def reflection(self):
        LOG.append(("nxt_reflection", self.port)); return 0
    def ambient(self):
        LOG.append(("nxt_ambient", self.port)); return 0


class ColorSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("NXTColorSensor", self.port))
    def color(self):
        LOG.append(("nxt_color", self.port)); return None
    def reflection(self):
        LOG.append(("nxt_color_reflection", self.port)); return 0
    def ambient(self):
        LOG.append(("nxt_color_ambient", self.port)); return 0
    def rgb(self):
        LOG.append(("nxt_rgb", self.port)); return (0, 0, 0)


class UltrasonicSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("NXTUltrasonicSensor", self.port))
    def distance(self):
        LOG.append(("nxt_distance", self.port)); return 0


class SoundSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("NXTSoundSensor", self.port))
    def intensity(self, audible_only=True):
        LOG.append(("nxt_intensity", self.port)); return 0
