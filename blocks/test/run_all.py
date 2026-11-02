#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the suite that has to pass before the editor is shipped.

    python3 run_all.py              everything
    python3 run_all.py nxc pin      only those

Needs playwright with chromium, and nqc and nbc on PATH (or NQC= / NBC=
pointing at them). The screenshot tests are not in here: they produce
pictures for a human to look at, and there is nothing for them to assert.
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

SUITE = ["run", "net", "control", "sensors", "ops", "vars", "pal",
         "nxc", "nxc2", "roundtrip", "saveas", "pin"]


def main(argv):
    want = argv[1:] or SUITE
    unknown = [w for w in want if w not in SUITE]
    if unknown:
        raise SystemExit("no conozco: %s\nhay: %s"
                         % (", ".join(unknown), ", ".join(SUITE)))

    failed = []
    for name in want:
        sys.stdout.write("%-12s " % name)
        sys.stdout.flush()
        t0 = time.time()
        # Plain python3, not -I: the tests import paths.py from this folder,
        # and isolated mode is exactly what keeps it off sys.path.
        r = subprocess.run([sys.executable, os.path.join(HERE, name + ".py")],
                           capture_output=True, text=True, cwd=HERE)
        secs = time.time() - t0
        if r.returncode == 0:
            print("OK    %4.1fs" % secs)
        else:
            print("FALLO %4.1fs" % secs)
            failed.append(name)
            tail = (r.stdout + r.stderr).rstrip().split("\n")[-8:]
            for line in tail:
                print("             " + line)

    print()
    if failed:
        print("FALLARON %d de %d: %s" % (len(failed), len(want), ", ".join(failed)))
        return 1
    print("las %d pasaron" % len(want))
    return 0


raise SystemExit(main(sys.argv))
