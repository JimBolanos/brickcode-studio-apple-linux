#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NXT sensors: the colour sensor and the named light and sound blocks.
Checks the NXC they generate and puts it through nbc."""

import os
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

import paths

WORK = tempfile.mkdtemp(prefix="nxts-")

def setsensor(port, t, nxt=""):
    return ('<block type="nxt_setsensor"><field name="S">%s</field><field name="T">%s</field>%s</block>'
            % (port, t, ("<next>%s</next>" % nxt) if nxt else ""))

def disp(line, val, nxt=""):
    return ('<block type="nxt_disp_num"><field name="LINE">%s</field><value name="VAL">%s</value>%s</block>'
            % (line, val, ("<next>%s</next>" % nxt) if nxt else ""))

XML = """<xml xmlns="https://developers.google.com/blockly/xml">
<block type="rcx_task_main" x="40" y="40"><statement name="DO">%s
</statement></block></xml>""" % setsensor(1, "COLOR", setsensor(2, "COLOR_LIGHT", setsensor(3, "LIGHT", setsensor(4, "SOUND",
 '<block type="rcx_if"><value name="COND"><block type="nxt_color_is"><field name="S">1</field>'
 '<field name="COLOR">INPUT_REDCOLOR</field></block></value>'
 '<statement name="DO">' + disp("LCD_LINE1", '<block type="nxt_light_level"><field name="S">3</field></block>',
   disp("LCD_LINE2", '<block type="nxt_sound_level"><field name="S">4</field></block>')) +
 '</statement></block>'))))

fails = []
def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok: fails.append(what)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 860})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1000)
    pg.get_by_text("NXC · NXT").click(); pg.wait_for_timeout(800)
    pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
        Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", XML)
    pg.wait_for_timeout(800)
    code = pg.evaluate("window.__nqc()")
    print(code)
    for want in ["SetSensorColorFull(IN_1);", "SetSensorColorRed(IN_2);", "SetSensorLight(IN_3);",
                 "SetSensorSound(IN_4);", "Sensor(IN_1) == INPUT_REDCOLOR", "Sensor(IN_3)", "Sensor(IN_4)"]:
        check(want in code, "generated: " + want)
    names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "els => els.map(e => e.textContent)")
    pg.locator(".blocklyToolboxCategory").nth(names.index("Sensors")).click(); pg.wait_for_timeout(900)
    flyout = pg.evaluate("""() => Blockly.getMainWorkspace().getFlyout().getWorkspace()
        .getTopBlocks().map(b => b.type)""")
    for t in ("nxt_color_is", "nxt_light_level", "nxt_sound_level"):
        check(t in flyout, "NXT Sensors flyout has " + t)
    pg.screenshot(path=paths.shot("nxt_sensors.png"))
    check(not errs, "no page errors %s" % errs)
    b.close()

src = os.path.join(WORK, "s.nxc"); out = os.path.join(WORK, "s.rxe")
open(src, "w").write(code)
r = subprocess.run([paths.compiler("nbc"), "-O=" + out, src], capture_output=True, text=True, cwd=WORK)
check(os.path.exists(out), "nbc compiles it" + ("" if os.path.exists(out) else " " +
      " | ".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("# Status"))[:300]))
print("\nnxt_sensors: %s" % ("FALLA" if fails else "todo bien"))
sys.exit(1 if fails else 0)
