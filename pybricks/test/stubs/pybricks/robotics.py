from . import LOG
from .ev3devices import Motor, _num, _stop
from .parameters import Stop


class DriveBase:
    def __init__(self, left_motor, right_motor, wheel_diameter, axle_track):
        for name, m in (("left_motor", left_motor), ("right_motor", right_motor)):
            if not isinstance(m, Motor):
                raise TypeError("%s must be a Motor, got %r" % (name, m))
        if left_motor is right_motor:
            raise ValueError("a drive base needs two different motors")
        _num("wheel_diameter", wheel_diameter, 1)
        _num("axle_track", axle_track, 1)
        self.left, self.right = left_motor.port, right_motor.port
        LOG.append(("DriveBase", self.left, self.right,
                    wheel_diameter, axle_track))

    def straight(self, distance, then=Stop.HOLD, wait=True):
        _num("distance", distance); _stop(then)
        LOG.append(("straight", distance, repr(then)))

    def turn(self, angle, then=Stop.HOLD, wait=True, absolute=False):
        _num("angle", angle); _stop(then)
        LOG.append(("turn", angle, repr(then)))

    def drive(self, speed, turn_rate):
        _num("speed", speed); _num("turn_rate", turn_rate)
        LOG.append(("drive", speed, turn_rate))

    def stop(self):  LOG.append(("drive_stop",))
    def brake(self): LOG.append(("drive_brake",))
    def hold(self):  LOG.append(("drive_hold",))
    def reset(self, distance=0, angle=0): LOG.append(("drive_reset",))
    def distance(self): LOG.append(("drive_distance",)); return 0
    def angle(self):    LOG.append(("drive_angle",)); return 0
    def state(self):    return (0, 0, 0, 0)
