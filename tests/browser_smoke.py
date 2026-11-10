from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1] /'website'
res=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
 for vw,vh in [(1440,900),(390,844)]:
  page=b.new_page(viewport={'width':vw,'height':vh},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto("http://127.0.0.1:8767/index.html",wait_until='domcontentloaded',timeout=20000)
  page.wait_for_timeout(900)
  page.screenshot(path=str(root.parent/f'preview-{vw}.png'),full_page=True,timeout=15000)
  metrics=page.locator('#metrics .meter')
  assert metrics.count()==3,metrics.count()
  page.locator('[data-bench="node_edge"]').click()
  assert '91 Token' in page.locator('#metrics').inner_text()
  h=page.evaluate('({sw:document.documentElement.scrollWidth,w:innerWidth,stage:document.querySelector(".statue-stage").getBoundingClientRect().toJSON()})')
  res.append({'page':'home','viewport':vw,'metrics':metrics.count(),'layout':h,'errors':errors})
  if vw==390:
   page.locator('#menuBtn').click();assert page.locator('#navLinks').evaluate('(n)=>n.classList.contains("open")')
  page.close()
 for file in ['grammar.html','playground.html','downloads.html']:
  page=b.new_page(viewport={'width':1280,'height':900})
  errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  page.goto("http://127.0.0.1:8767/"+file,wait_until='domcontentloaded',timeout=20000)
  page.wait_for_timeout(350)
  item={'page':file,'errors':errs}
  if file=='grammar.html':
   assert page.locator('#matrixRows tr').count()>10
   page.locator('#matrixRows tr').first.click();assert page.locator('#ruleDialog').evaluate('(d)=>d.open')
   page.keyboard.press('Escape');assert not page.locator('#ruleDialog').evaluate('(d)=>d.open')
   item['visible_rules']=page.locator('#matrixRows tr').count()
  if file=='playground.html':
   assert 'domains' not in page.locator('#ast').inner_text().lower() or page.locator('#ast').inner_text().startswith('[')
   item['ast_length']=len(page.locator('#ast').inner_text())
  if file=='downloads.html':assert page.locator('a[download]').count()>=4
  res.append(item);page.close()
 b.close()
print(json.dumps(res,ensure_ascii=False,indent=2))
