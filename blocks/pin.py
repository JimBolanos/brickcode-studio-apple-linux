#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write a copy of the built page pinned to one language.

    python3 pin.py nqc-only /path/to/brickcode-blocks.html

The pin rides inside the file, on <html data-pin="...">, instead of in a
URL fragment. A host that can compile only one of the two languages can
then ship this copy and be certain the editor comes up in that language
with the switch gone, however it happens to open the page: the Windows
edition opens it through ShellExecute, which hands the browser a plain
path and loses everything after the "#".
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brickcode-blocks.html")

PINS = ("nqc", "nxc", "nqc-only", "nxc-only")


def main(argv):
    if len(argv) != 3 or argv[1] not in PINS:
        raise SystemExit("uso: pin.py {%s} destino.html" % "|".join(PINS))
    want, dest = argv[1], argv[2]

    s = io.open(SRC, encoding="utf-8").read()
    tag = '<html lang="en">'
    if tag not in s:
        raise SystemExit("no encuentro %s en %s" % (tag, SRC))
    s = s.replace(tag, '<html lang="en" data-pin="%s">' % want, 1)

    io.open(dest, "w", encoding="utf-8").write(s)
    print("pinned a %s: %s - %d KB"
          % (want, dest, round(os.path.getsize(dest) / 1024)))


main(sys.argv)
