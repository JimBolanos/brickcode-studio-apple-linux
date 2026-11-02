from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 820}, accept_downloads=True)
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000)
    pg.wait_for_timeout(1200)
    pg.screenshot(path=paths.shot("shot-claro.png"))

    with pg.expect_download() as dl:
        pg.click("#btnMenu"); pg.wait_for_timeout(200); pg.click("#miSave")
    d = dl.value
    path = "/tmp/descargado.nqc"
    d.save_as(path)
    print("descargado como:", d.suggested_filename)
    print("--- contenido ---")
    print(open(path).read())

    # cambia un bloque y comprueba que el codigo se regenera
    pg.evaluate("""() => {
        const b = Blockly.getMainWorkspace().getAllBlocks(false).find(x => x.type === 'rcx_wait');
        b.setFieldValue(5, 'SECS');
    }""")
    pg.wait_for_timeout(600)
    print("--- tras cambiar el primer Wait a 5 s ---")
    print(pg.evaluate("window.__nqc()").split("\n")[4])
    b.close()
