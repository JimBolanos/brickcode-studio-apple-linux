from playwright.sync_api import sync_playwright

import paths
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":820})
    pg.goto(paths.PAGE)
    pg.wait_for_function("window.__ready === true", timeout=20000); pg.wait_for_timeout(1500)
    print(pg.evaluate("""() => {
      const out=[];
      document.querySelectorAll('.blocklyToolboxCategoryIcon').forEach((ic,i)=>{
        const cs=getComputedStyle(ic), r=ic.getBoundingClientRect();
        out.push(i+' x='+Math.round(r.x)+' y='+Math.round(r.y)+' w='+Math.round(r.width)+' h='+Math.round(r.height)
          +' vis='+cs.visibility+' op='+cs.opacity+' pos='+cs.position+' bg='+cs.backgroundColor+' radius='+cs.borderRadius);
      });
      const cont=document.querySelector('.blocklyTreeRowContentContainer');
      const cc=getComputedStyle(cont);
      out.push('contenedor display='+cc.display+' dir='+cc.flexDirection);
      const cat=document.querySelector('.blocklyToolboxCategory');
      out.push('categoria overflow='+getComputedStyle(cat).overflow+' h='+Math.round(cat.getBoundingClientRect().height));
      return out.join('\\n');
    }"""))
    b.close()
