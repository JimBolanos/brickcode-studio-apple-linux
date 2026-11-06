from . import LOG


def wait(time):
    if not isinstance(time, (int, float)) or isinstance(time, bool):
        raise TypeError("wait() takes a number of milliseconds, got %r" % (time,))
    if time < 0:
        raise ValueError("wait() cannot take a negative time: %r" % (time,))
    LOG.append(("wait", time))


class StopWatch:
    def __init__(self):
        self._t = 0
    def time(self):
        return self._t
    def reset(self):
        self._t = 0
