#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The parts of the NXC side that the first test does not reach: variables,
My Blocks that give a value back (NXC can, NQC cannot), parallel tasks, the
timer and the brick buttons. Compiled with nbc, like everything else."""

import os
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

import paths

PAGE = paths.PAGE
WORK = tempfile.mkdtemp(prefix="nxc2-")

PROGRAM = """
<xml xmlns="https://developers.google.com/blockly/xml">
  <variables><variable id="v1">my score</variable></variables>

  <block type="rcx_task_main" x="40" y="40"><statement name="DO">
    <block type="variables_set"><field name="VAR" id="v1">my score</field>
      <value name="VALUE"><block type="math_number"><field name="NUM">5</field></block></value>
    <next>
    <block type="math_change"><field name="VAR" id="v1">my score</field>
      <value name="DELTA"><block type="math_number"><field name="NUM">1</field></block></value>
    <next>
    <block type="nxt_timer_reset"><next>
    <block type="rcx_if">
      <value name="COND"><block type="nxt_button"><field name="B">BTNCENTER</field></block></value>
      <statement name="DO">
        <block type="nxt_disp_num"><field name="LINE">LCD_LINE2</field>
          <value name="VAL"><block type="nxt_timer"/></value>
        <next>
        <block type="nxt_disp_num"><field name="LINE">LCD_LINE3</field>
          <value name="VAL"><block type="procedures_callreturn"><mutation name="doble"/></block></value>
        </block></next></block>
      </statement>
    <next>
    <block type="rcx_parallel">
      <statement name="A">
        <block type="nxt_motor_on"><field name="M">OUT_A</field><field name="PCT">50</field></block>
      </statement>
      <statement name="B">
        <block type="rcx_wait"><field name="SECS">1</field></block>
      </statement>
    </block>
    </next></block></next></block></next></block></next></block>
  </statement></block>

  <block type="procedures_defreturn" x="520" y="40">
    <field name="NAME">doble</field>
    <value name="RETURN">
      <block type="rcx_arith"><field name="OP">*</field>
        <value name="A"><block type="variables_get"><field name="VAR" id="v1">my score</field></block></value>
        <value name="B"><block type="math_number"><field name="NUM">2</field></block></value>
      </block>
    </value>
  </block>
</xml>
"""


# The same shape of program, but with RCX hardware, so the NQC generator gets
# something it can actually answer. Feeding it nxt_ blocks would only prove
# that it refuses them.
PROGRAM_NQC = PROGRAM \
    .replace('<block type="nxt_timer_reset"/>', "") \
    .replace('<block type="nxt_timer_reset">', '<block type="rcx_clearsensor">'
             '<field name="S">SENSOR_1</field>') \
    .replace('<block type="nxt_button"><field name="B">BTNCENTER</field></block>',
             '<block type="rcx_touched"><field name="S">SENSOR_1</field></block>') \
    .replace('<block type="nxt_disp_num"><field name="LINE">LCD_LINE2</field>',
             '<block type="variables_set"><field name="VAR" id="v1">my score</field>') \
    .replace('<block type="nxt_disp_num"><field name="LINE">LCD_LINE3</field>',
             '<block type="variables_set"><field name="VAR" id="v1">my score</field>') \
    .replace('<value name="VAL">', '<value name="VALUE">') \
    .replace('<block type="nxt_timer"/>', '<block type="math_number">'
             '<field name="NUM">7</field></block>') \
    .replace('<block type="nxt_motor_on"><field name="M">OUT_A</field>'
             '<field name="PCT">50</field></block>',
             '<block type="rcx_onfwd"><field name="MOTOR">OUT_A</field></block>')


def compile_it(mode, code):
    """Put the generated text through the real compiler for that brick."""
    src = os.path.join(WORK, "prog_" + mode + ("." + mode))
    out = src + (".rxe" if mode == "nxc" else ".rcx")
    with open(src, "w") as f:
        f.write(code)
    cmd = ([paths.compiler("nbc"), "-O=" + out, src] if mode == "nxc"
           else [paths.compiler("nqc"), "-TRCX2", "-O" + out, src])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=WORK)
    if os.path.exists(out):
        return True, "%d bytes" % os.path.getsize(out)
    errs = [l for l in (r.stdout + r.stderr).splitlines()
            if l.strip() and not l.startswith("# Status")
            and not l.startswith("#---")]
    return False, " | ".join(errs[:6]) or "no output, exit %d" % r.returncode


def main():
    bad = 0
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page()
        page.on("pageerror", lambda e: print("PAGEERROR", str(e)[:300]))
        page.goto(PAGE)
        page.wait_for_function("window.__ready === true")

        for mode, prog in (("nxc", PROGRAM), ("nqc", PROGRAM_NQC)):
            page.click("#mNxc" if mode == "nxc" else "#mNqc")
            page.wait_for_function("window.__mode() === '%s'" % mode)
            page.evaluate("window.__ws.clear()")
            page.evaluate(
                """(x) => Blockly.Xml.domToWorkspace(
                     Blockly.utils.xml.textToDom(x), window.__ws)""", prog)
            page.wait_for_timeout(200)
            code = page.evaluate("window.__code()")

            print("=" * 68)
            print("%s:" % mode.upper())
            print(code)
            print("-" * 68)

            if "generator error" in code:
                print("generator   FAIL  %s" % code.strip()[:120])
                bad += 1
                continue

            # identifiers have to be legal C in both languages
            if "my score" in code:
                print('names       FAIL  "my score" was not sanitised')
                bad += 1
            else:
                print("names       OK    my score -> my_score")

            if "start side1a;" in code and "task side1a()" in code:
                print("parallel    OK    two real tasks")
            else:
                print("parallel    FAIL  parallel did not become tasks")
                bad += 1

            if mode == "nxc":
                if "int doble()" in code and "return" in code:
                    print("my blocks   OK    NXC gives a value back: int doble()")
                else:
                    print("my blocks   FAIL  expected int doble() with a return")
                    bad += 1
                # the definition has to come before the call, or nbc rejects it
                if code.index("int doble()") < code.index("task main()"):
                    print("order       OK    doble() defined above task main")
                else:
                    print("order       FAIL  NXC needs the definition first")
                    bad += 1
                if "__t0 = CurrentTick();" in code and "long __t0;" in code:
                    print("timer       OK    declared and reset")
                else:
                    print("timer       FAIL  timer plumbing missing")
                    bad += 1
            else:
                if "cannot" in code:
                    print("my blocks   OK    NQC is told it cannot return a value")
                else:
                    print("my blocks   FAIL  NQC should refuse the return block")
                    bad += 1

            ok, info = compile_it(mode, code)
            print("compile     %s  %s" % ("OK  " if ok else "FAIL", info))
            if not ok:
                bad += 1

    print("\nworkspace: %s" % WORK)
    print("FAILURES: %d" % bad)
    raise SystemExit(1 if bad else 0)


main()
