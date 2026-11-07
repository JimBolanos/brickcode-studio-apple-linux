#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run one generated program against the stubs and print what it did.

Invoked as a subprocess by gen.py, with the program on stdin, so a program
that loops forever or blows up cannot take the test suite with it.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "stubs"))

import pybricks  # noqa: E402  (needs the path above)

source = sys.stdin.read()

try:
    code = compile(source, "<generated>", "exec")
except SyntaxError as e:
    print(json.dumps({"ok": False, "where": "syntax",
                      "error": "%s (line %s)" % (e.msg, e.lineno)}))
    raise SystemExit(0)

pybricks.reset_log()
try:
    exec(code, {"__name__": "__main__"})
except SystemExit:
    # "stop the program" generates this on purpose: a clean end, not a fault.
    pass
except Exception as e:                      # noqa: BLE001 - any failure is a result
    print(json.dumps({"ok": False, "where": "run",
                      "error": "%s: %s" % (type(e).__name__, e),
                      "log": [list(x) for x in pybricks.LOG]}))
    raise SystemExit(0)

print(json.dumps({"ok": True, "log": [list(x) for x in pybricks.LOG],
                  "draw": [list(x) for x in pybricks.DRAW]}))
