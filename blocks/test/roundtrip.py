#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Save a program, open it again, and demand that both the code and the
blocks come back identical - in both languages. Then check that a file we
did not write is handled honestly instead of being guessed at."""

import os
import re
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

import paths

PAGE = paths.PAGE
WORK = tempfile.mkdtemp(prefix="rt-")
MARK = "brickcode-blocks:1:"

FOREIGN_NQC = """// hand written, never near a block
int n;
task main()
{
    SetSensor(SENSOR_1, SENSOR_TOUCH);
    n = 0;
    while (true) {
        until (SENSOR_1 == 1);
        n += 1;
        PlaySound(SOUND_CLICK);
        until (SENSOR_1 == 0);
    }
}
"""


def compiles(mode, code):
    src = os.path.join(WORK, "c." + mode)
    out = src + ".bin"
    if os.path.exists(out):
        os.remove(out)
    open(src, "w").write(code)
    cmd = ([paths.compiler("nbc"), "-O=" + out, src] if mode == "nxc"
           else [paths.compiler("nqc"), "-TRCX2", "-O" + out, src])
    subprocess.run(cmd, capture_output=True, text=True, cwd=WORK)
    return os.path.getsize(out) if os.path.exists(out) else None


def main():
    bad = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page()
        page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:300]))
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")
        page.wait_for_timeout(300)

        # nothing has been opened, so the banner must not be on screen
        if page.is_visible("#banner"):
            print("start     FAIL  the banner shows with nothing opened")
            bad += 1
        else:
            print("start     OK    no banner until a file is opened")

        for mode in ("nqc", "nxc"):
            page.click("#mNxc" if mode == "nxc" else "#mNqc")
            page.wait_for_function("window.__mode() === '%s'" % mode)
            page.wait_for_timeout(250)

            before_code = page.evaluate("window.__code()")
            before_xml = page.evaluate(
                "Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.__ws))")
            saved = page.evaluate("window.__saved()")

            # the marker must be there, and the file must still compile
            if MARK not in saved:
                print("%s  marker     FAIL  nothing embedded" % mode.upper())
                bad += 1
                continue
            size_plain = compiles(mode, before_code)
            size_saved = compiles(mode, saved)
            if size_plain is None or size_saved is None:
                print("%s  compile    FAIL  plain=%s saved=%s"
                      % (mode.upper(), size_plain, size_saved))
                bad += 1
            elif size_plain != size_saved:
                print("%s  compile    FAIL  marker changed the output, %d vs %d"
                      % (mode.upper(), size_plain, size_saved))
                bad += 1
            else:
                print("%s  compile    OK    %d bytes, identical with the marker"
                      % (mode.upper(), size_saved))

            # wipe the workspace, then open what we saved
            page.evaluate("window.__ws.clear()")
            page.wait_for_timeout(150)
            page.evaluate("([t, n]) => window.__open(t, n)",
                          [saved, "program." + mode])
            page.wait_for_timeout(400)

            after_code = page.evaluate("window.__code()")
            after_xml = page.evaluate(
                "Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.__ws))")

            print("%s  code       %s" % (mode.upper(),
                  "OK    came back identical" if after_code == before_code
                  else "FAIL  code differs after the round trip"))
            if after_code != before_code:
                bad += 1
                print("    antes:", before_code[:160])
                print("    desp :", after_code[:160])
            print("%s  blocks     %s" % (mode.upper(),
                  "OK    workspace restored exactly" if after_xml == before_xml
                  else "FAIL  the workspace changed"))
            if after_xml != before_xml:
                bad += 1
            print("%s  mode       %s" % (mode.upper(),
                  "OK" if page.evaluate("window.__mode()") == mode
                  else "FAIL  wrong language after opening"))

        # a file from somewhere else: shown, never guessed at
        page.evaluate("([t, n]) => window.__open(t, n)",
                      [FOREIGN_NQC, "ajeno.nqc"])
        page.wait_for_timeout(350)
        viewing = page.evaluate("window.__viewing()")
        blocks = page.evaluate("window.__ws.getAllBlocks(false).length")
        shown = page.inner_text("#out")
        visible = page.is_visible("#banner")
        ok = (viewing is not None and visible
              and "SetSensor" in shown and blocks == 0)
        print("foreign   %s  banner=%s blocks_invented=%d"
              % ("OK  " if ok else "FAIL", visible, blocks))
        if not ok:
            bad += 1

        # and going back to the blocks must restore the generated view
        page.click("#btnDrop")
        page.wait_for_timeout(300)
        back = page.evaluate("window.__viewing()")
        print("dismiss   %s" % ("OK    back to the generated code"
                                if back is None else "FAIL  still viewing"))
        if back is not None:
            bad += 1

        br.close()

    print("\nFAILURES: %d" % bad)
    raise SystemExit(1 if bad else 0)


main()
