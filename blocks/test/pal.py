from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":860})
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1400)
    names = pg.eval_on_selector_all(".blocklyToolboxCategoryLabel", "els => els.map(e => e.textContent)")
    print("categorias:", names)
    for i, n in enumerate(names):
        if n in ("Movement", "Operators"):
            pg.locator(".blocklyToolboxCategory").nth(i).click(); pg.wait_for_timeout(900)
            pg.screenshot(path=paths.shot("pal-%s.png") % n.lower())
    b.close()
