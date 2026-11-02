from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1200)
    print(pg.evaluate("""() => {
      const t = document.querySelector('.blocklyToolboxDiv') || document.querySelector('[class*=oolbox]');
      if (!t) return 'no encontrado';
      const first = t.querySelector('div');
      return t.className + '\\n---\\n' + t.innerHTML.slice(0, 700);
    }"""))
    b.close()
