from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    print(pg.evaluate("""() => {
      const ic = document.querySelector('.blocklyToolboxCategoryIcon');
      if (!ic) return 'sin icono';
      const cs = getComputedStyle(ic);
      const r = ic.getBoundingClientRect();
      return JSON.stringify({
        clases: ic.className, inline: ic.getAttribute('style'),
        w: cs.width, h: cs.height, bg: cs.backgroundColor,
        display: cs.display, rect: [Math.round(r.width), Math.round(r.height)],
        nCats: document.querySelectorAll('.blocklyToolboxCategory').length
      }, null, 1);
    }"""))
    b.close()
