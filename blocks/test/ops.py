from playwright.sync_api import sync_playwright

import paths

def num(n): return '<block type="math_number"><field name="NUM">%s</field></block>' % n
def sens(s): return '<block type="rcx_sensor_value"><field name="S">%s</field></block>' % s

XML = """<xml xmlns="https://developers.google.com/blockly/xml">
<block type="rcx_task_main" x="40" y="40"><statement name="DO">
 <block type="rcx_move_speed"><field name="PCT">100</field><next>
 <block type="rcx_wait"><field name="SECS">1</field><next>
 <block type="rcx_if">
  <value name="COND"><block type="rcx_and">
    <value name="A"><block type="rcx_touched"><field name="S">SENSOR_1</field></block></value>
    <value name="B"><block type="rcx_not"><value name="A">
      <block type="rcx_touched"><field name="S">SENSOR_2</field></block></value></block></value>
  </block></value>
  <statement name="DO"><block type="rcx_move_start"><field name="DIR">FWD</field></block></statement><next>
 <block type="rcx_if">
  <value name="COND"><block type="rcx_between">
    <value name="X">__SENS__</value>
    <value name="LO">__LO__</value>
    <value name="HI">__HI__</value></block></value>
  <statement name="DO"><block type="rcx_turn"><field name="SIDE">L</field><field name="SECS">1</field></block></statement><next>
 <block type="rcx_if">
  <value name="COND"><block type="rcx_compare">
    <value name="A"><block type="rcx_arith">
      <value name="A">__R__</value><field name="OP">*</field><value name="B">__TWO__</value></block></value>
    <field name="OP">&gt;</field>
    <value name="B">__TEN__</value></block></value>
  <statement name="DO"><block type="rcx_move_stop"></block></statement>
 </block></next></block></next></block></next></block></next></block>
</statement></block></xml>"""

RAND = ('<block type="rcx_random"><value name="FROM">%s</value>'
        '<value name="TO">%s</value></block>') % (num(1), num(6))
XML = (XML.replace("__SENS__", sens("SENSOR_3")).replace("__LO__", num(30))
          .replace("__HI__", num(70)).replace("__R__", RAND)
          .replace("__TWO__", num(2)).replace("__TEN__", num(10)))

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 820})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
        Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", XML)
    pg.wait_for_timeout(900)
    code = pg.evaluate("window.__nqc()")
    open("/tmp/nqccheck/ops_gen.nqc", "w").write(code)
    print(code)
    print("=== errors:", errs or "(none)")
    b.close()
