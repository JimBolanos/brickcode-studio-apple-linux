#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IR Messages: the four blocks generate the NQC the compiler expects, they
sit in their own palette category on the RCX page (not on the NXT one), and
the result compiles for RCX, RCX 2 and Scout."""

import os
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

import paths

WORK = tempfile.mkdtemp(prefix="ir-")

def num(n): return '<block type="math_number"><field name="NUM">%s</field></block>' % n

XML = """<xml xmlns="https://developers.google.com/blockly/xml">
<block type="rcx_task_main" x="40" y="40"><statement name="DO">
 <block type="rcx_ir_power"><field name="LVL">TX_POWER_LO</field><next>
 <block type="rcx_ir_send"><value name="MSG">%s</value><next>
 <block type="rcx_ir_clear"><next>
 <block type="rcx_wait_until"><value name="COND"><block type="rcx_compare">
    <value name="A"><block type="rcx_ir_receive"></block></value>
    <field name="OP">==</field><value name="B">%s</value></block></value><next>
 <block type="rcx_if"><value name="COND"><block type="rcx_compare">
    <value name="A"><block type="rcx_ir_receive"></block></value>
    <field name="OP">&gt;</field><value name="B">%s</value></block></value>
   <statement name="DO"><block type="rcx_playsound"><field name="SND">SOUND_UP</field></block></statement><next>
 <block type="rcx_ir_power"><field name="LVL">TX_POWER_HI</field>
 </block></next></block></next></block></next></block></next></block></next></block></next></block>
</statement></block></xml>""" % (num(42), num(42), num(0))

fails = []
def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok: fails.append(what)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 860})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "els => els.map(e => e.textContent)")
    check("IR Messages" in names, "RCX palette has an IR Messages category: %s" % names)
    check(names.index("IR Messages") == names.index("Sound") + 1, "IR Messages comes right after Sound")
    # open it and see that the four blocks and the 42 shadow are in the flyout
    pg.locator(".blocklyToolboxCategory").nth(names.index("IR Messages")).click(); pg.wait_for_timeout(900)
    flyout = pg.evaluate("""() => Blockly.getMainWorkspace().getFlyout().getWorkspace()
        .getTopBlocks().map(b => b.type)""")
    check(flyout == ["rcx_ir_power", "rcx_ir_send", "rcx_ir_clear", "rcx_ir_receive"],
          "flyout blocks: %s" % flyout)
    shadow = pg.evaluate("""() => { const s = Blockly.getMainWorkspace().getFlyout().getWorkspace()
        .getTopBlocks().find(b => b.type === 'rcx_ir_send').getInputTargetBlock('MSG');
        return s && s.type + ':' + s.getFieldValue('NUM'); }""")
    check(shadow == "math_number:42", "send block carries a 42 shadow: %s" % shadow)
    pg.screenshot(path=paths.shot("ir.png"))

    pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
        Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", XML)
    pg.wait_for_timeout(800)
    code = pg.evaluate("window.__nqc()")
    print(code)
    for want in ["SetTxPower(TX_POWER_LO);", "SendMessage(42);", "ClearMessage();",
                 "until (Message() == 42);", "if (Message() > 0)", "SetTxPower(TX_POWER_HI);"]:
        check(want in code, "generated: " + want)
    check(not errs, "no page errors %s" % errs)
    b.close()

src = os.path.join(WORK, "ir.nqc")
open(src, "w").write(code)
nqc = paths.which("nqc") if hasattr(paths, "which") else None
nqc = nqc or "nqc"
for target in ("RCX", "RCX2", "Scout"):
    r = subprocess.run([nqc, "-T" + target, "-O" + os.path.join(WORK, "ir." + target), src],
                       capture_output=True, text=True)
    check(r.returncode == 0, "nqc compiles it for %s %s" % (target, (r.stdout + r.stderr)[-200:] if r.returncode else ""))

print("\nIR: %s" % ("FALLA" if fails else "todo bien"))
sys.exit(1 if fails else 0)
