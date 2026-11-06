class _Enum:
    def __init__(self, name, value):
        self._name, self._value = name, value
    def __repr__(self):
        return self._name


class Port:
    A = _Enum("Port.A", "A"); B = _Enum("Port.B", "B")
    C = _Enum("Port.C", "C"); D = _Enum("Port.D", "D")
    S1 = _Enum("Port.S1", "S1"); S2 = _Enum("Port.S2", "S2")
    S3 = _Enum("Port.S3", "S3"); S4 = _Enum("Port.S4", "S4")
    _MOTORS = ("A", "B", "C", "D")


class Stop:
    COAST = _Enum("Stop.COAST", "coast")
    BRAKE = _Enum("Stop.BRAKE", "brake")
    HOLD = _Enum("Stop.HOLD", "hold")


class Direction:
    CLOCKWISE = _Enum("Direction.CLOCKWISE", 1)
    COUNTERCLOCKWISE = _Enum("Direction.COUNTERCLOCKWISE", -1)


class Color:
    NONE = _Enum("Color.NONE", None); BLACK = _Enum("Color.BLACK", "black")
    GRAY = _Enum("Color.GRAY", "gray"); WHITE = _Enum("Color.WHITE", "white")
    RED = _Enum("Color.RED", "red"); ORANGE = _Enum("Color.ORANGE", "orange")
    BROWN = _Enum("Color.BROWN", "brown"); YELLOW = _Enum("Color.YELLOW", "yellow")
    GREEN = _Enum("Color.GREEN", "green"); CYAN = _Enum("Color.CYAN", "cyan")
    BLUE = _Enum("Color.BLUE", "blue"); VIOLET = _Enum("Color.VIOLET", "violet")
    MAGENTA = _Enum("Color.MAGENTA", "magenta")


class Button:
    LEFT = _Enum("Button.LEFT", "left"); RIGHT = _Enum("Button.RIGHT", "right")
    CENTER = _Enum("Button.CENTER", "center")
    UP = _Enum("Button.UP", "up"); DOWN = _Enum("Button.DOWN", "down")
    BEACON = _Enum("Button.BEACON", "beacon")
