"""Stand-in for Pybricks, so generated programs can be run and checked.

There is no compiler to hand a Pybricks program to, the way nqc and nbc
check the RCX and NXT ones. These modules are the substitute: a generated
program imports them, runs, and every call is recorded with its arguments.
A wrong method name, a missing argument or a value of the wrong kind
raises here, the way the compiler would have complained there.
"""

LOG = []
DRAW = []      # every screen drawing call, with colour, fill and width


def reset_log():
    del LOG[:]
    del DRAW[:]
