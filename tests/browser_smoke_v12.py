"""Run from package root: python tests/browser_smoke_v12.py
Chromium E2E checks for actual website, JSON Token Lab, Graph hover, whitespace toggling.
"""
import sys,json,time,subprocess,signal,os,re,base64
from pathlib import Path
from contextlib import contextmanager
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PORT=18888

def load_static_inline(page,filename):
    """Use Chromium's set_content: no server/local-file URL permission required."""
    html=(ROOT/'website'/filename).read_text(encoding='utf-8')
    # Inlined styles in original order (offline media fallback retained).
    def css(match):
        path=(ROOT/'website'/match.group(1))
        txt=path.read_text(encoding='utf-8')
        for img in re.findall(r"url\(['\"]?(assets/[^)'\"]+)",txt):
            f=ROOT/'website'/img
            if f.is_file():
                content=base64.b64encode(f.read_bytes()).decode('ascii')
                mime='image/webp' if f.suffix=='.webp' else 'image/svg+xml'
                txt=txt.replace(img,'data:'+mime+';base64,'+content)
        return '<style>\n'+txt+'\n</style>'
    html=re.sub(r'<link[^>]+href="([a-zA-Z0-9._/-]+\.css)"[^>]*>',css,html)
    scripts=[]
    def js(match):
        path=match.group(1)
        if path=='three-hero.js': return '' # optional WebGL module has network fallback
        src=(ROOT/'website'/path).read_text(encoding='utf-8')
        scripts.append('<script>\n'+src+'\n</script>')
        return ''
    html=re.sub(r'<script\b[^>]*src="([a-zA-Z0-9._/-]+\.js)"[^>]*></script>',js,html)
    for img in re.findall(r'(?:src|href)="(assets/[^"#]+)"',html):
        f=ROOT/'website'/img
        if f.exists():
            content=base64.b64encode(f.read_bytes()).decode('ascii')
            mime='image/webp' if f.suffix=='.webp' else 'image/svg+xml' if f.suffix=='.svg' else 'image/png'
            html=html.replace('"'+img+'"','"data:'+mime+';base64,'+content+'"')
    html=html.replace('</body>',''.join(scripts)+'</body>')
    page.set_content(html,wait_until='domcontentloaded')

def main():
 results=[];errs=[];screens=ROOT/'previews';screens.mkdir(exist_ok=True)
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
  for width,height,name in ((1440,900,'desktop'),(768,1024,'tablet'),(390,844,'mobile')):
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
   page.route('https://cdn.jsdelivr.net/**',lambda route:route.abort()) # offline 3D fallback should not damage the website
   page.on('pageerror',lambda ex:errs.append('JS '+str(ex)))
   load_static_inline(page,'index.html')
   page.wait_for_timeout(300)
   assert '.NEMA' in page.title(),page.title()
   assert page.locator('#sourceCode').count()==1
   before=page.locator('#sourceCode').text_content()
   page.locator('#spacesButton').click()
   after=page.locator('#sourceCode').text_content()
   assert before!=after and '·' in after and '⇥' in after,after[:120]
   page.locator('#spacesButton').click()
   assert before==page.locator('#sourceCode').text_content()
   page.get_by_role('tab',name=re.compile('Node.*Edge',re.I)).click() if False else page.locator('[data-mode="graph"]').click()
   src=page.locator('#sourceCode').text_content()
   assert '\n A LoginAPI Authentication\n' in src,src
   assert '\nA>X>B Reads VerifySession\n' in src
   assert page.locator('[data-graph-kind="node"]').count()>=3
   assert page.locator('[data-graph-kind="edge"]').count()>=4
   page.locator('[data-graph-kind="node"]').first.hover()
   page.wait_for_timeout(100)
   assert 'Authentication' in page.locator('body').inner_text()
   page.locator('[data-lang="en"]').first.click()
   assert page.locator('[data-lang="en"]').first.get_attribute('aria-pressed')=='true'
   x=page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
   assert x <= 2,(name,'horizontal overflow',x)
   page.screenshot(path=str(screens/f'v12-home-{name}.png'),full_page=(name=='desktop'))
   results.append({'view':name,'overflow':x,'graph_nodes':page.locator('[data-graph-kind="node"]').count(),'graph_edges':page.locator('[data-graph-kind="edge"]').count()})
   page.close()
  page=browser.new_page(viewport={'width':1280,'height':900});page.route('https://cdn.jsdelivr.net/**',lambda route:route.abort())
  page.on('pageerror',lambda ex:errs.append('LAB '+str(ex)))
  load_static_inline(page,'token-benchmark.html')
  assert page.locator('#scenario option').count()==8
  assert page.locator('#labRows tr').count()==8
  page.locator('#scenario').select_option('graph_40n_160e')
  assert page.locator('#activeCase').inner_text()=='graph_40n_160e'
  assert page.locator('#caseBars .measure-row').count()==5
  page.locator('[data-source="json"]').click();assert '"nodes"' in page.locator('#labSource').text_content()
  page.locator('#showWhitespace').click();assert '·' in page.locator('#labSource').text_content()
  page.screenshot(path=str(screens/'v12-token-lab.png'),full_page=False)
  load_static_inline(page,'download.html')
  assert page.locator('#dlBtn').get_attribute('href').endswith('NEMA_Interpreter_v1.2.zip')
  load_static_inline(page,'graph-guide.html')
  assert 'Authentication' in page.locator('body').inner_text()
  assert page.locator('[data-graph-item="A"]').count()>=1
  results.append({'view':'secondary pages','token_rows':8,'download':True,'graph':True})
  browser.close()
 assert not errs,errs
 (ROOT/'audit'/'browser_v12.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import re
 main()
