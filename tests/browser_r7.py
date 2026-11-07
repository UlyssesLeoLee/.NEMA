from playwright.sync_api import sync_playwright
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
W=ROOT/'website'
errors=[];out={}
with sync_playwright() as p:
 import shutil,os
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN') or shutil.which('chromium') or p.chromium.executable_path,headless=True,args=['--no-sandbox','--disable-gpu'])
 for width,height in [(1440,900),(800,900),(390,844)]:
  page=browser.new_page(viewport={'width':width,'height':height}, device_scale_factor=1)
  page.route('**/*',lambda r:r.abort())
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((W/'index.html').read_text('utf8'),wait_until='domcontentloaded')
  for file in ('styles.css','comic.css','art-direction-v12.css'):
   page.add_style_tag(content=(W/file).read_text('utf8'))
  for file in ('demo_data.js','benchmark_v12.js','app.js'):
   page.add_script_tag(content=(W/file).read_text('utf8'))
  assert page.locator('#metricValue').inner_text()!='0.00%'
  page.locator('[data-mode="graph"]').click()
  code=page.locator('#sourceCode').inner_text()
  assert '\n A LoginAPI Authentication APIKey\n' in code
  assert 'A>X>B Reads VerifySession HTTP401' in code
  assert page.locator('.graph-node').count()>=3
  # Verify interactive extension inspector and hover notes
  page.locator('.graph-node').first.hover(force=True)
  # click UI object => inspector includes X3 exact
  page.locator('.graph-node').first.click(force=True)
  assert 'APIKey' in page.locator('#nema-graph-inspector').inner_text(),page.locator('#nema-graph-inspector').inner_text()
  page.locator('.graph-edge').first.click(force=True)
  assert 'HTTP401' in page.locator('#nema-graph-inspector').inner_text(),page.locator('#nema-graph-inspector').inner_text()
  c=page.locator('#sourceCode').evaluate('(e)=>({letterSpacing:getComputedStyle(e).letterSpacing,whiteSpace:getComputedStyle(e).whiteSpace,font:getComputedStyle(e).fontFamily})')
  assert c['letterSpacing'] in ('0px','normal'),c
  assert c['whiteSpace']=='pre',c
  page.locator('[data-lang="ja"]').first.click()
  assert 'JSON オブジェクト形式' in page.locator('[data-i="metricLabel"]').inner_text()
  page.locator('[data-lang="zh"]').first.click()
  page.locator('#spacesButton').click()
  assert '·A·LoginAPI' in page.locator('#sourceCode').inner_text()
  page.locator('#spacesButton').click()
  assert '\n A LoginAPI' in page.locator('#sourceCode').inner_text()
  h=page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
  assert h,(width,page.evaluate('document.documentElement.scrollWidth'))
  out[str(width)]={'metric':page.locator('#metricValue').inner_text(),'graphNodes':page.locator('.graph-node').count(),'graphEdges':page.locator('.graph-edge').count(),'noOverflow':h,'codeCss':c}
  if width==1440:
   (ROOT/'previews').mkdir(exist_ok=True)
   page.screenshot(path=str(ROOT/'previews/graph-r7-desktop.png'),full_page=False)
  page.close()
 audit=browser.new_page(viewport={'width':1240,'height':900})
 audit.route('**/*',lambda r:r.abort())
 audit.on('pageerror',lambda e:errors.append(str(e)))
 audit.set_content((W/'audit-r7.html').read_text('utf8'),wait_until='domcontentloaded')
 for file in ('styles.css','comic.css','art-direction-v12.css','audit-r7.css'):
  audit.add_style_tag(content=(W/file).read_text('utf8'))
 for file in ('audit-r7-data.js','audit-r7.js'):
  audit.add_script_tag(content=(W/file).read_text('utf8'))
 assert audit.locator('#r7-body tr').count()==8
 assert audit.locator('#r7-body tr').first.inner_text().endswith('24.15%')
 audit.locator('[data-model="unigram"]').click()
 assert audit.locator('#r7-body tr').count()==8
 audit.locator('[data-lang="ja"]').first.click()
 assert '圧縮率' in audit.locator('#r7-title').inner_text()
 audit.locator('[data-lang="en"]').first.click()
 assert 'Protocol accuracy' in audit.locator('#r7-title').inner_text()
 audit.screenshot(path=str(ROOT/'previews/audit-r7-desktop.png'),full_page=True)
 out['auditPage']={'rows':8,'langs':['zh','ja','en'],'models':['bpe','unigram']}
 audit.close()
 browser.close()
assert not errors, errors
(ROOT/'audit/browser_r7.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
