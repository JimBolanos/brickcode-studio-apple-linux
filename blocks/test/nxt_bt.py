#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NXT Bluetooth blocks: the leader and the follower generate different calls
for the same blocks, the category is on the NXT page only, and both programs
go through nbc."""

import os
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

import paths

WORK = tempfile.mkdtemp(prefix="nxtbt-")

def num(n): return '<block type="math_number"><field name="NUM">%s</field></block>' % n

def program(role):
    return """<xml xmlns="https://developers.google.com/blockly/xml">
<block type="rcx_task_main" x="40" y="40"><statement name="DO">
 <block type="nxt_bt_role"><field name="ROLE">%s</field><next>
 <block type="rcx_wait_until"><value name="COND"><block type="nxt_bt_connected"></block></value><next>
 <block type="nxt_bt_send"><field name="CH">MAILBOX2</field><value name="NUM">%s</value><next>
 <block type="rcx_forever"><statement name="DO">
  <block type="rcx_if"><value name="COND"><block type="rcx_compare">
     <value name="A"><block type="nxt_bt_last"><field name="CH">MAILBOX2</field></block></value>
     <field name="OP">==</field><value name="B">%s</value></block></value>
   <statement name="DO"><block type="nxt_disp_num"><field name="LINE">LCD_LINE1</field>
     <value name="VAL"><block type="nxt_bt_last"><field name="CH">MAILBOX2</field></block></value></block></statement>
   <next><block type="rcx_wait"><field name="SECS">0.1</field></block></next></block>
 </statement></block></next></block></next></block></next></block>
</statement></block></xml>""" % (role, num(42), num(7))

fails = []
def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok: fails.append(what)

codes = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 860})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1000)
    rcx_names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "els => els.map(e => e.textContent)")
    check("Bluetooth" not in rcx_names, "RCX palette has no Bluetooth category")
    pg.get_by_text("NXC · NXT").click(); pg.wait_for_timeout(800)
    names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "els => els.map(e => e.textContent)")
    check("Bluetooth" in names and names.index("Bluetooth") == names.index("Sound") + 1,
          "NXT palette has Bluetooth after Sound: %s" % names)
    pg.locator(".blocklyToolboxCategory").nth(names.index("Bluetooth")).click(); pg.wait_for_timeout(900)
    flyout = pg.evaluate("""() => Blockly.getMainWorkspace().getFlyout().getWorkspace()
        .getTopBlocks().map(b => b.type)""")
    check(flyout == ["nxt_bt_role", "nxt_bt_connected", "nxt_bt_send", "nxt_bt_last"], "flyout: %s" % flyout)
    pg.screenshot(path=paths.shot("nxt_bt.png"))
    for role in ("LEADER", "FOLLOWER"):
        pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
            Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", program(role))
        pg.wait_for_timeout(800)
        codes[role] = pg.evaluate("window.__nqc()")
        print(codes[role])
    check(not errs, "no page errors %s" % errs)
    b.close()

L, F = codes["LEADER"], codes["FOLLOWER"]
for want in ["SendRemoteNumber(1, MAILBOX2, 42);", "BluetoothStatus(1) == NO_ERR", "__btLast(MAILBOX2)",
             "long __btNum[10];", "ReceiveRemoteNumber(q, true, v)"]:
    check(want in L, "leader: " + want)
for want in ["SendResponseNumber(MAILBOX2, 42);", "BluetoothStatus(0) == NO_ERR", "__btLast(MAILBOX2)"]:
    check(want in F, "follower: " + want)
check("SendRemoteNumber" not in F, "follower never calls SendRemoteNumber")
check("SendResponseNumber" not in L, "leader never calls SendResponseNumber")
check(L.index("long __btLast") < L.index("task main"), "helper is above task main")

for role, code in codes.items():
    src = os.path.join(WORK, role + ".nxc"); out = os.path.join(WORK, role + ".rxe")
    open(src, "w").write(code)
    r = subprocess.run([paths.compiler("nbc"), "-O=" + out, src], capture_output=True, text=True, cwd=WORK)
    msg = "" if os.path.exists(out) else " " + " | ".join(
        l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("# Status"))[:300]
    check(os.path.exists(out), "nbc compiles the %s program%s" % (role.lower(), msg))

print("\nnxt_bt: %s" % ("FALLA" if fails else "todo bien"))
sys.exit(1 if fails else 0)
