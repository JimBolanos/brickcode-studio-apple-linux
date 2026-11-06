from . import LOG
from .parameters import Port, Stop, Direction, _Enum


def _num(name, v, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise TypeError("%s must be a number, got %r" % (name, v))
    if lo is not None and v < lo:
        raise ValueError("%s must be at least %s, got %r" % (name, lo, v))
    if hi is not None and v > hi:
        raise ValueError("%s must be at most %s, got %r" % (name, hi, v))
    return v


def _sport(port):
    name = repr(port)
    if not isinstance(port, _Enum) or not name.startswith("Port.S"):
        raise ValueError("a sensor needs Port.S1 to Port.S4, got %r" % (port,))
    return name[5:]


def _stop(v):
    if v not in (Stop.COAST, Stop.BRAKE, Stop.HOLD):
        raise TypeError("then= must be a Stop, got %r" % (v,))
    return v


class Motor:
    def __init__(self, port, positive_direction=Direction.CLOCKWISE, gears=None):
        if not isinstance(port, _Enum) or repr(port)[5:] not in Port._MOTORS:
            raise ValueError("a motor needs Port.A to Port.D, got %r" % (port,))
        self.port = repr(port)[5:]
        self._angle = 0
        LOG.append(("Motor", self.port))

    def run(self, speed):
        LOG.append(("run", self.port, _num("speed", speed)))

    def run_time(self, speed, time, then=Stop.HOLD, wait=True):
        _num("speed", speed); _num("time", time, 0); _stop(then)
        LOG.append(("run_time", self.port, speed, time, repr(then)))

    def run_angle(self, speed, rotation_angle, then=Stop.HOLD, wait=True):
        _num("speed", speed); _num("rotation_angle", rotation_angle); _stop(then)
        self._angle += rotation_angle
        LOG.append(("run_angle", self.port, speed, rotation_angle, repr(then)))

    def run_target(self, speed, target_angle, then=Stop.HOLD, wait=True):
        _num("speed", speed); _num("target_angle", target_angle); _stop(then)
        self._angle = target_angle
        LOG.append(("run_target", self.port, speed, target_angle, repr(then)))

    def run_until_stalled(self, speed, then=Stop.COAST, duty_limit=None):
        _num("speed", speed); _stop(then)
        if duty_limit is not None:
            _num("duty_limit", duty_limit, 0, 100)
        LOG.append(("run_until_stalled", self.port, speed, repr(then)))
        return self._angle

    def dc(self, duty):
        _num("duty", duty, -100, 100)
        LOG.append(("dc", self.port, duty))

    def stop(self):
        LOG.append(("stop", self.port))

    def brake(self):
        LOG.append(("brake", self.port))

    def hold(self):
        LOG.append(("hold", self.port))

    def angle(self):
        LOG.append(("angle", self.port))
        return self._angle

    def reset_angle(self, angle):
        _num("angle", angle)
        self._angle = angle
        LOG.append(("reset_angle", self.port, angle))

    def speed(self):
        LOG.append(("speed", self.port))
        return 0


class TouchSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("TouchSensor", self.port))
    def pressed(self):
        LOG.append(("pressed", self.port)); return False


class ColorSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("ColorSensor", self.port))
    def color(self):
        LOG.append(("color", self.port)); return None
    def reflection(self):
        LOG.append(("reflection", self.port)); return 0
    def ambient(self):
        LOG.append(("ambient", self.port)); return 0
    def rgb(self):
        LOG.append(("rgb", self.port)); return (0, 0, 0)


class UltrasonicSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("UltrasonicSensor", self.port))
    def distance(self, silent=False):
        LOG.append(("distance", self.port)); return 0
    def presence(self):
        LOG.append(("presence", self.port)); return False


class GyroSensor:
    # The rendered v2 docs call this positive_direction; the API source
    # calls it direction, and the API source is what runs.
    def __init__(self, port, direction=Direction.CLOCKWISE):
        self.port = _sport(port); LOG.append(("GyroSensor", self.port))
    def angle(self):
        LOG.append(("gyro_angle", self.port)); return 0
    def speed(self):
        LOG.append(("gyro_speed", self.port)); return 0
    def reset_angle(self, angle):
        _num("angle", angle); LOG.append(("gyro_reset", self.port, angle))


class InfraredSensor:
    def __init__(self, port):
        self.port = _sport(port); LOG.append(("InfraredSensor", self.port))
    def distance(self):
        LOG.append(("ir_distance", self.port)); return 0
    def beacon(self, channel):
        LOG.append(("beacon", self.port, channel)); return (None, None)
    def buttons(self, channel):
        LOG.append(("ir_buttons", self.port, channel)); return []
    def keypad(self):
        LOG.append(("keypad", self.port)); return []
