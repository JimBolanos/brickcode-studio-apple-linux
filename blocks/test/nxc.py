#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Switch the editor to NXC, build programs out of blocks, and put every one
through the real nbc compiler. Nothing is trusted until it makes an .rxe."""

import os
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

import paths

PAGE = paths.PAGE
WORK = tempfile.mkdtemp(prefix="nxctest-")

# Each case drops a stack of blocks inside "when the program starts".
CASES = {
    "example": None,   # whatever the NXT example loads with

    "motors": [
        ("nxt_motor_for", {"M": "OUT_A", "AMT": "2", "UNIT": "ROT", "PCT": "80"}),
        ("nxt_motor_reset", {"M": "OUT_A"}),
        ("nxt_motor_on", {"M": "OUT_B", "PCT": "-60"}),
        ("nxt_motor_off", {"M": "OUT_B"}),
        ("nxt_motor_for", {"M": "OUT_C", "AMT": "90", "UNIT": "DEG", "PCT": "50"}),
        ("nxt_motor_for", {"M": "OUT_C", "AMT": "1.5", "UNIT": "SEC", "PCT": "0"}),
    ],

    "movement": [
        ("nxt_move_motors", {"PAIR": "AC"}),
        ("nxt_move_for", {"DIR": "FWD", "AMT": "3", "UNIT": "ROT", "PCT": "70"}),
        ("nxt_move_for", {"DIR": "REV", "AMT": "2", "UNIT": "SEC", "PCT": "40"}),
        ("nxt_turn", {"SIDE": "L", "SECS": "1", "PCT": "55"}),
        ("nxt_move_start", {"DIR": "FWD", "PCT": "100"}),
        ("nxt_move_stop", {}),
    ],

    "display_sound": [
        ("nxt_disp_clear", {}),
        ("nxt_disp_text", {"TXT": 'say "hi"\\there', "LINE": "LCD_LINE3"}),
        ("nxt_tone", {"HZ": "880", "SECS": "0.25"}),
        ("nxt_note", {"NOTE": "TONE_FS5", "SECS": "0.5"}),
        ("nxt_sound_stop", {}),
    ],

    "sensors": [
        ("nxt_setsensor", {"S": "1", "T": "TOUCH"}),
        ("nxt_setsensor", {"S": "2", "T": "LIGHT"}),
        ("nxt_setsensor", {"S": "3", "T": "LIGHT_AMB"}),
        ("nxt_setsensor", {"S": "4", "T": "US"}),
        ("nxt_timer_reset", {}),
    ],

    "control": [
        ("rcx_wait", {"SECS": "2"}),
        ("rcx_repeat", {"N": "5"}),
        ("rcx_forever", {}),
    ],
}


def xml_for(stack):
    """Wrap a flat list of (type, fields) into one chain inside task main."""
    if stack is None:
        return None
    body, closers = "", ""
    for t, fields in stack:
        body += '<block type="%s">' % t
        for k, v in fields.items():
            body += '<field name="%s">%s</field>' % (k, v)
        body += "<next>"
        closers = "</next></block>" + closers
    return ('<xml xmlns="https://developers.google.com/blockly/xml">'
            '<block type="rcx_task_main" x="40" y="40"><statement name="DO">'
            + body + closers + "</statement></block></xml>")


def compile_nxc(name, code):
    src = os.path.join(WORK, name + ".nxc")
    out = os.path.join(WORK, name + ".rxe")
    with open(src, "w") as f:
        f.write(code)
    r = subprocess.run([paths.compiler("nbc"), "-O=" + out, src],
                       capture_output=True, text=True, cwd=WORK)
    if os.path.exists(out):
        return True, "%d bytes" % os.path.getsize(out)
    errs = [l for l in (r.stdout + r.stderr).splitlines()
            if not l.startswith("# Status")]
    return False, "\n".join(errs[:8]) or "no output, exit %d" % r.returncode


def main():
    failures = 0
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page()
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")

        # the switch itself
        assert page.evaluate("window.__mode()") == "nqc", "should start on NQC"
        page.click("#mNxc")
        page.wait_for_function("window.__mode() === 'nxc'")
        assert page.evaluate("window.__mode()") == "nxc"
        print("switch        NQC -> NXC ok, title is %r"
              % page.inner_text("#title"))

        cats = page.evaluate(
            "Array.from(document.querySelectorAll('.blocklyToolboxCategory'))"
            ".map(e => e.textContent)")
        print("palette       %s" % " | ".join(cats))
        assert "Display" in cats, "the NXT needs a Display category"

        for name, stack in CASES.items():
            xml = xml_for(stack)
            if xml is not None:
                page.evaluate(
                    """(x) => { window.__ws.clear();
                        Blockly.Xml.domToWorkspace(
                          Blockly.utils.xml.textToDom(x), window.__ws); }""",
                    xml)
            else:
                page.evaluate("window.__ws.clear()")
                page.click("#btnMenu")
                page.wait_for_timeout(200)
                page.click("#miExample")
            page.wait_for_timeout(120)
            code = page.evaluate("window.__code()")
            ok, info = compile_nxc(name, code)
            print("%-14s %s  %s" % (name, "OK  " if ok else "FAIL", info))
            if not ok:
                failures += 1
                print("---- the program that failed ----")
                print(code)
                print("--------------------------------")

        # a pair of motors must never be written as an addition in NXC
        page.evaluate("window.__ws.clear()")
        page.evaluate(
            """(x) => Blockly.Xml.domToWorkspace(
                 Blockly.utils.xml.textToDom(x), window.__ws)""",
            xml_for(CASES["movement"]))
        page.wait_for_timeout(120)
        mv = page.evaluate("window.__code()")
        if "OUT_A + OUT_C" in mv:
            print("pairs          FAIL  OUT_A + OUT_C means OUT_C in NXC")
            failures += 1
        elif "OUT_AC" in mv:
            print("pairs          OK    written as OUT_AC, one token")
        else:
            print("pairs          FAIL  no motor pair in the output")
            failures += 1

        # and switching back has to restore the RCX side
        page.click("#mNqc")
        page.wait_for_function("window.__mode() === 'nqc'")
        back = page.evaluate("window.__code()")
        if "OUT_A + OUT_C" in back:
            print("back to NQC    OK    bit mask again, OUT_A + OUT_C")
        else:
            print("back to NQC    FAIL  expected the NQC addition form")
            failures += 1

    print("\nworkspace: %s" % WORK)
    print("FAILURES: %d" % failures)
    raise SystemExit(1 if failures else 0)


main()
