from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":820})
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1800)
    pg.screenshot(path=paths.shot("full.png"))
    pg.locator(".blocklyToolbox").screenshot(path=paths.shot("toolbox.png"))
    b.close()
