from playwright.sync_api import sync_playwright

import paths

XML = """<xml xmlns="https://developers.google.com/blockly/xml">
<block type="rcx_task_main" x="40" y="40"><statement name="DO">
 <block type="rcx_setsensor"><field name="S">SENSOR_1</field><field name="T">SENSOR_ROTATION</field><next>
 <block type="rcx_setsensor"><field name="S">SENSOR_2</field><field name="T">SENSOR_CELSIUS</field><next>
 <block type="rcx_setsensor"><field name="S">SENSOR_3</field><field name="T">SENSOR_PULSE</field><next>
 <block type="rcx_clearsensor"><field name="S">SENSOR_1</field><next>
 <block type="rcx_onfwd"><field name="MOTOR">OUT_A</field><next>
 <block type="rcx_wait_until">
   <value name="COND"><block type="rcx_compare">
     <value name="A"><block type="rcx_sensor_value"><field name="S">SENSOR_1</field></block></value>
     <field name="OP">&gt;</field>
     <value name="B"><block type="math_number"><field name="NUM">48</field></block></value></block></value><next>
 <block type="rcx_off"><field name="MOTOR">OUT_A</field><next>
 <block type="rcx_if">
   <value name="COND"><block type="rcx_compare">
     <value name="A"><block type="rcx_sensor_value"><field name="S">SENSOR_2</field></block></value>
     <field name="OP">&lt;</field>
     <value name="B"><block type="math_number"><field name="NUM">20</field></block></value></block></value>
   <statement name="DO"><block type="rcx_playsound"><field name="SND">SOUND_DOWN</field></block></statement><next>
 <block type="rcx_if">
   <value name="COND"><block type="rcx_compare">
     <value name="A"><block type="rcx_sensor_raw"><field name="S">SENSOR_3</field></block></value>
     <field name="OP">&gt;</field>
     <value name="B"><block type="math_number"><field name="NUM">500</field></block></value></block></value>
   <statement name="DO"><block type="rcx_playsound"><field name="SND">SOUND_CLICK</field></block></statement>
 </block></next></block></next></block></next></block></next></block></next></block></next></block></next></block>
</statement></block></xml>"""

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 820})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    pg.evaluate("""(xml) => { const ws = window.__ws; ws.clear();
        Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(xml), ws); }""", XML)
    pg.wait_for_timeout(900)
    code = pg.evaluate("window.__nqc()")
    open("/tmp/nqccheck/sensors_gen.nqc", "w").write(code)
    print(code)
    print("=== errors:", errs or "(none)")
    pg.locator(".blocklyToolboxCategory").nth(4).click(); pg.wait_for_timeout(1000)
    pg.screenshot(path=paths.shot("sensors.png"))
    b.close()
