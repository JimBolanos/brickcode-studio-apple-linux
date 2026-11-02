from playwright.sync_api import sync_playwright

import paths
reqs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("requestfailed", lambda r: reqs.append(r.url))
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000)
    pg.wait_for_timeout(1500)
    b.close()
print("=== peticiones fallidas ===")
for u in dict.fromkeys(reqs):
    print(" ", u[:160])
