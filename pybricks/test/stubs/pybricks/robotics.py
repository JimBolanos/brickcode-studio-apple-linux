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

    def settings(self, straight_speed=None, straight_acceleration=None,
                 turn_rate=None, turn_acceleration=None):
        for k, v in (("straight_speed", straight_speed),
                     ("straight_acceleration", straight_acceleration),
                     ("turn_rate", turn_rate),
                     ("turn_acceleration", turn_acceleration)):
            if v is not None:
                _num(k, v, 1)
        LOG.append(("drive_settings", straight_speed, straight_acceleration,
                    turn_rate, turn_acceleration))

    def stop(self):  LOG.append(("drive_stop",))
    def brake(self): LOG.append(("drive_brake",))
    def hold(self):  LOG.append(("drive_hold",))
    def reset(self, distance=0, angle=0): LOG.append(("drive_reset",))
    def distance(self): LOG.append(("drive_distance",)); return 0
    def angle(self):    LOG.append(("drive_angle",)); return 0
    def state(self):    return (0, 0, 0, 0)


class Car:
    """Added to Pybricks in 3.4. Two different motors: one steers, one
    drives."""
    def __init__(self, steer_motor, drive_motors, torque_limit=100):
        if not isinstance(steer_motor, Motor):
            raise TypeError("steer_motor must be a Motor, got %r" % (steer_motor,))
        ms = drive_motors if isinstance(drive_motors, (tuple, list)) else (drive_motors,)
        for m in ms:
            if not isinstance(m, Motor):
                raise TypeError("drive_motors must be Motors, got %r" % (m,))
            if m is steer_motor:
                raise ValueError("a car needs two different motors")
        LOG.append(("Car", steer_motor.port, tuple(m.port for m in ms)[0]))

    def steer(self, percentage):
        _num("percentage", percentage, -100, 100)
        LOG.append(("car_steer", percentage))

    def drive_power(self, power):
        _num("power", power, -100, 100)
        LOG.append(("car_power", power))

    def drive_speed(self, speed):
        _num("speed", speed)
        LOG.append(("car_speed", speed))
