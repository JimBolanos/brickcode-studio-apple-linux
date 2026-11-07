from . import LOG

# One shared board stands in for "the other EV3": what a mailbox sends is what
# the same-named mailbox reads back.
_BOARD = {}


class BluetoothMailboxServer:
    def __init__(self):
        LOG.append(("BluetoothMailboxServer",))
    def wait_for_connection(self, count=1):
        LOG.append(("wait_for_connection", count))
    def close(self):
        LOG.append(("bt_close",))


class BluetoothMailboxClient:
    def __init__(self):
        LOG.append(("BluetoothMailboxClient",))
    def connect(self, brick):
        if not isinstance(brick, str):
            raise TypeError("connect() takes the name of the other brick as a string")
        LOG.append(("connect", brick))
    def close(self):
        LOG.append(("bt_close",))


class NumericMailbox:
    def __init__(self, name, connection):
        if not isinstance(name, str):
            raise TypeError("a mailbox name is a string")
        if not isinstance(connection, (BluetoothMailboxServer, BluetoothMailboxClient)):
            raise TypeError("a mailbox needs a Bluetooth connection, got %r" % (connection,))
        self.name = name
        LOG.append(("NumericMailbox", name))
    def send(self, value, brick=None):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("a numeric mailbox only sends numbers, got %r" % (value,))
        _BOARD[self.name] = value
        LOG.append(("mbox_send", self.name, value))
    def read(self):
        LOG.append(("mbox_read", self.name))
        return _BOARD.get(self.name)
    def wait_new(self):
        LOG.append(("mbox_wait_new", self.name))
        return _BOARD.get(self.name, 0)
    def wait(self):
        LOG.append(("mbox_wait", self.name))
