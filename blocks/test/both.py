from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":820})
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000)
    pg.wait_for_timeout(1400)
    pg.screenshot(path=paths.shot("scratch-claro.png"))
    pg.click("#btnTheme"); pg.wait_for_timeout(1000)
    pg.screenshot(path=paths.shot("scratch-oscuro.png"))
    print("NQC sigue saliendo bien:", "task main()" in pg.evaluate("window.__nqc()"))
    print("errores:", errs or "(ninguno)")
    b.close()
