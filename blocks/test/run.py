from playwright.sync_api import sync_playwright

import paths
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 820})
    pg.on("console", lambda m: errs.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000)
    pg.wait_for_timeout(1500)
    print("=== NQC generado ===")
    print(pg.evaluate("window.__nqc()"))
    print("=== bloques en el lienzo ===")
    print(pg.text_content("#count"))
    pg.screenshot(path=paths.shot("shot-claro.png"))
    pg.click("#btnTheme"); pg.wait_for_timeout(900)
    pg.screenshot(path=paths.shot("shot-oscuro.png"))
    b.close()
print("=== errores ===")
print("\n".join(errs) if errs else "(ninguno)")
