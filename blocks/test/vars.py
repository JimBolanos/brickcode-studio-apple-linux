from playwright.sync_api import sync_playwright

import paths

XML = """<xml xmlns="https://developers.google.com/blockly/xml">
<variables><variable id="v1">laps</variable></variables>
<block type="procedures_defnoreturn" x="520" y="40">
  <field name="NAME">beep</field>
  <statement name="STACK"><block type="rcx_playsound"><field name="SND">SOUND_CLICK</field></block></statement>
</block>
<block type="rcx_task_main" x="40" y="40"><statement name="DO">
 <block type="rcx_move_motors"><field name="PAIR">BC</field><next>
 <block type="variables_set"><field name="VAR" id="v1">laps</field>
   <value name="VALUE"><block type="math_number"><field name="NUM">0</field></block></value><next>
 <block type="rcx_repeat"><field name="N">4</field>
   <statement name="DO">
     <block type="rcx_move_for"><field name="DIR">FWD</field><field name="SECS">1</field><next>
     <block type="rcx_turn"><field name="SIDE">R</field><field name="SECS">1</field><next>
     <block type="math_change"><field name="VAR" id="v1">laps</field>
       <value name="DELTA"><block type="math_number"><field name="NUM">1</field></block></value><next>
     <block type="procedures_callnoreturn"><mutation name="beep"></mutation></block>
     </next></block></next></block></next></block>
   </statement><next>
 <block type="rcx_if">
   <value name="COND"><block type="rcx_compare">
     <value name="A"><block type="variables_get"><field name="VAR" id="v1">laps</field></block></value>
     <field name="OP">==</field>
     <value name="B"><block type="math_number"><field name="NUM">4</field></block></value></block></value>
   <statement name="DO"><block type="rcx_playsound"><field name="SND">SOUND_UP</field></block></statement>
 </block></next></block></next></block></next></block>
</statement></block></xml>"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 860})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
        Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", XML)
    pg.wait_for_timeout(1000)
    code = pg.evaluate("window.__nqc()")
    open("/tmp/nqccheck/vars_gen.nqc", "w").write(code)
    print(code)
    print("=== errors:", errs or "(none)")
    names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "e=>e.map(x=>x.textContent)")
    print("=== categories:", names)
    b.close()
