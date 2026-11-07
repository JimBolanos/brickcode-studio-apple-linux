#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The NXT screen pictures and drawing blocks.

Every program is handed to the real nbc. Then the drawing calls it contains
are read back and painted onto a 100 x 64 screen (NXT counts y from the
bottom) and a few pixels of each picture are checked, the way the EV3 ones
are, so a picture that compiles but comes out wrong still fails.
"""

import os
import re
import subprocess
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

import paths

PAGE = paths.PAGE
WORK = tempfile.mkdtemp(prefix="nxtpics-")
OUT = os.path.join(paths.HERE, "out")
W, H = 100, 64

# picture -> [(x, y from the top, black?)]
PIX = {
    "happy":   [(50, 55, 1), (50, 48, 0), (37, 24, 1), (50, 15, 0)],
    "smile":   [(50, 52, 1), (50, 44, 0), (37, 27, 1), (50, 22, 0)],
    "wink":    [(37, 27, 1), (63, 27, 1), (63, 34, 0), (50, 52, 1)],
    "serious": [(37, 26, 1), (63, 26, 1), (50, 46, 1), (50, 36, 0)],
    "unsure":  [(37, 26, 1), (50, 48, 1), (50, 38, 0), (63, 26, 1)],
    "sad":     [(50, 42, 1), (50, 50, 0), (37, 27, 1), (50, 20, 0)],
    "open":    [(31, 32, 1), (18, 32, 1), (31, 24, 0), (69, 32, 1), (50, 32, 0)],
    "closed":  [(31, 40, 1), (31, 32, 0), (69, 40, 1), (50, 32, 0)],
    "heart":   [(34, 24, 1), (50, 50, 1), (50, 6, 0), (8, 55, 0)],
    "heart_small": [(43, 26, 1), (50, 40, 1), (50, 14, 0), (15, 40, 0)],
    "zzz":     [(23, 6, 1), (23, 21, 1), (23, 36, 1), (8, 20, 0)],
    "bubble":  [(50, 6, 1), (50, 18, 0), (34, 26, 1), (6, 25, 1), (50, 55, 0)],
    "thumbup": [(40, 20, 1), (12, 45, 1), (12, 20, 0), (75, 39, 0), (75, 36, 1)],
    "thumbdown": [(40, 44, 1), (12, 18, 1), (12, 44, 0), (75, 24, 0), (75, 27, 1)],
    "cross":   [(50, 32, 1), (50, 8, 0), (30, 32, 0), (26, 14, 1)],
    "check":   [(28, 44, 1), (60, 32, 1), (28, 20, 0), (75, 50, 0)],
    "question": [(50, 5, 1), (50, 20, 0), (50, 44, 1), (50, 58, 1), (35, 45, 0)],
    "stop":    [(50, 4, 1), (24, 4, 0), (50, 16, 0), (45, 30, 1), (35, 22, 0)],
    "teeth":   [(4, 30, 1), (50, 32, 1), (28, 20, 0), (35, 20, 1)],
    "teeth_small": [(19, 30, 1), (40, 28, 1), (35, 28, 0), (50, 32, 1)],
    "fangs":   [(20, 13, 1), (20, 30, 0), (28, 51, 1), (28, 34, 0), (50, 32, 0)],
    "up":      [(50, 10, 1), (30, 10, 0), (50, 55, 1), (30, 55, 0)],
    "down":    [(50, 55, 1), (30, 55, 0), (50, 10, 1), (30, 10, 0)],
    "left":    [(8, 32, 1), (8, 10, 0), (80, 32, 1), (80, 10, 0)],
    "right":   [(92, 32, 1), (92, 10, 0), (20, 32, 1), (20, 10, 0)],
}

CALL = re.compile(r"^\s*(ClearScreen|LineOut|RectOut|CircleOut|PointOut)\((.*)\);\s*$")


LOOP = re.compile(r"^\s*for \(int __y = (\d+); __y <= (\d+); __y\+\+\) "
                  r"LineOut\((\d+), __y, (\d+), __y\);\s*$")


def paint(code):
    """Paint every drawing call in the code, in order. Returns (image, bad)."""
    im = Image.new("L", (W, H), 255)
    px = im.load()
    bad = []

    def put(x, y, white):
        if 0 <= x < W and 0 <= y < H:
            px[x, H - 1 - y] = 255 if white else 0
        else:
            bad.append((x, y))

    def line(x1, y1, x2, y2, white):
        n = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(n + 1):
            put(round(x1 + (x2 - x1) * i / n), round(y1 + (y2 - y1) * i / n), white)

    for l in code.split("\n"):
        f = LOOP.match(l)
        if f:                       # the filled box: one line per row
            a, b, x1, x2 = (int(v) for v in f.groups())
            for yy in range(a, b + 1):
                line(x1, yy, x2, yy, False)
            continue
        m = CALL.match(l)
        if not m:
            continue
        name, args = m.group(1), [a.strip() for a in m.group(2).split(",")]
        # A real NXT ignores DRAW_OPT_CLEAR_PIXELS (seen on the screen), so
        # everything is painted black here, as it would come out on the brick.
        white = False
        nums = [int(a) for a in args if re.fullmatch(r"-?\d+", a)]
        if name == "ClearScreen":
            im.paste(255, (0, 0, W, H))
        elif name == "PointOut":
            put(nums[0], nums[1], white)
        elif name == "LineOut":
            line(nums[0], nums[1], nums[2], nums[3], white)
        elif name == "RectOut":
            x, y, w, h = nums[:4]
            line(x, y, x + w, y, white); line(x, y + h, x + w, y + h, white)
            line(x, y, x, y + h, white); line(x + w, y, x + w, y + h, white)
        elif name == "CircleOut":
            x, y, r = nums[:3]
            for i in range(720):
                import math
                a = i * math.pi / 360
                put(round(x + r * math.cos(a)), round(y + r * math.sin(a)), white)
    return im, bad


def compile_nxc(name, code):
    src = os.path.join(WORK, name + ".nxc")
    out = os.path.join(WORK, name + ".rxe")
    open(src, "w").write(code)
    r = subprocess.run([paths.compiler("nbc"), "-O=" + out, src],
                       capture_output=True, text=True, cwd=WORK)
    if os.path.exists(out):
        return True, "%d bytes" % os.path.getsize(out)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("# Status")]
    return False, "\n".join(errs[:8]) or "no output"


def chain(stack):
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


def main():
    bad = 0
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page()
        page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:200]))
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")
        page.click("#mNxc")
        page.wait_for_function("window.__mode() === 'nxc'")

        def run(name, stack):
            page.evaluate("""(x) => { window.__ws.clear();
                Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(x), window.__ws); }""",
                          chain(stack))
            page.wait_for_timeout(100)
            code = page.evaluate("window.__code()")
            ok, info = compile_nxc(name, code)
            return code, ok, info

        for pic, pts in PIX.items():
            code, ok, info = run("pic_" + pic, [("nxt_picture", {"PIC": pic})])
            if not ok:
                print("%-18s FAIL compile: %s" % (pic, info)); bad += 1
                continue
            if "DRAW_OPT" in code:
                print("%-18s FAIL uses a drawing option the NXT ignores" % pic); bad += 1
                continue
            im, off = paint(code)
            im.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(OUT, "nxt_%s.png" % pic))
            px = im.load()
            wrong = [(x, y, w) for x, y, w in pts if (px[x, y] == 0) != bool(w)]
            if off:
                print("%-18s FAIL outside the screen: %s" % (pic, off[:4])); bad += 1
            elif wrong:
                print("%-18s FAIL pixels: %s" % (pic, wrong)); bad += 1
            else:
                print("%-18s OK   %s, shape checked" % (pic, info))

        # the same picture twice: one function, two calls
        code, ok, info = run("twice", [("nxt_picture", {"PIC": "heart"}),
                                       ("nxt_picture", {"PIC": "heart"})])
        if ok and code.count("void draw_big_heart()") == 1 and code.count("draw_big_heart();") == 2:
            print("%-18s OK   one function, two calls" % "picture twice")
        else:
            print("%-18s FAIL\n%s" % ("picture twice", code)); bad += 1

        # the drawing blocks
        code, ok, info = run("draw", [
            ("nxt_disp_clear", {}),
            ("nxt_draw_pixel", {"X": "5", "Y": "5"}),
            ("nxt_draw_line", {"X1": "0", "Y1": "0", "X2": "99", "Y2": "63"}),
            ("nxt_draw_box", {"X1": "10", "Y1": "10", "X2": "60", "Y2": "40", "FILL": "FALSE"}),
            ("nxt_draw_box", {"X1": "62", "Y1": "12", "X2": "90", "Y2": "30", "FILL": "TRUE"}),
            ("nxt_draw_circle", {"X": "30", "Y": "30", "R": "10", "FILL": "FALSE"}),
            ("nxt_draw_circle", {"X": "75", "Y": "50", "R": "8", "FILL": "TRUE"}),
            ("rcx_wait", {"SECS": "2"}),
        ])
        if not ok:
            print("%-18s FAIL compile: %s\n%s" % ("draw blocks", info, code)); bad += 1
        else:
            im, off = paint(code)
            px = im.load()
            checks = [(5, 5, 1), (50, 32, 1), (10, 10, 1), (20, 35, 0),
                      (65, 25, 1), (75, 50, 1), (30, 20, 1), (30, 30, 0)]
            wrong = [(x, y, w) for x, y, w in checks if (px[x, y] == 0) != bool(w)]
            im.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(OUT, "nxt_draw.png"))
            if wrong or off:
                print("%-18s FAIL %s %s\n%s" % ("draw blocks", wrong, off[:3], code)); bad += 1
            else:
                print("%-18s OK   %s, y counted from the top" % ("draw blocks", info))
    print("\nFAILURES: %d" % bad)
    raise SystemExit(1 if bad else 0)


main()
