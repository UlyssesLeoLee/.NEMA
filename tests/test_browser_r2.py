"""Website R2 Playwright smoke tests; requires Chromium + playwright."""
from pathlib import Path
import re
import mimetypes
import base64
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]/'website'

def load_offline(page,name):
    html=(BASE/name).read_text()
    html=re.sub(r'<link(?=[^>]*https://)[^>]*>', '', html)
    html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>'+((BASE/m.group(1)).read_text())+'</style>',html)
    scripts=[]
    def inline_script(m):
        scripts.append((BASE/m.group(1)).read_text())
        return ''
    html=re.sub(r'<script src="([^"]+)" defer></script>',inline_script,html)
    html=re.sub(r'src="assets/([^"]+)"',lambda m:'src="data:'+ (mimetypes.guess_type(m.group(1))[0] or 'application/octet-stream')+';base64,'+base64.b64encode((BASE/'assets'/m.group(1)).read_bytes()).decode('ascii')+'"',html)
    html=html.replace('</body>', ''.join('<script>'+script+'</script>' for script in scripts)+'</body>')
    page.set_content(html,wait_until='domcontentloaded')
    return page

OUT=Path(__file__).resolve().parents[1]/'website'/'previews'
OUT.mkdir(parents=True,exist_ok=True)

def run():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  errors=[]
  for width,height in [(1440,960),(390,844),(768,1024)]:
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
   page.on('pageerror',lambda e: errors.append(str(e)));page.set_default_timeout(5000)
   load_offline(page,'index.html')
   page.locator('[data-mode="graph"]').click()
   assert 'Authentication' in page.locator('#sourceCode').inner_text()
   assert page.locator('.graph-node').count()==3
   assert page.locator('.graph-edge').count()==4
   assert page.locator('.graph-inspector').is_visible()
   assert 'Authentication' in page.locator('.graph-inspector').inner_text()
   # Edge Y is B<Y<C, directed C -> B.
   page.locator('.graph-choice').filter(has_text='Y ·').click()
   assert 'C → B' in page.locator('.graph-inspector').inner_text()
   page.locator('.graph-choice').filter(has_text='X ·').click()
   assert 'A → B' in page.locator('.graph-inspector').inner_text()
   page.locator('.graph-choice').filter(has_text='U ·').click()
   assert 'A — C' in page.locator('.graph-inspector').inner_text()
   page.locator('.graph-choice').filter(has_text='A ·').click()
   assert 'Authentication' in page.locator('.graph-inspector').inner_text()
   # Locale and mode switches work and preserve structural meaning.
   for lang,needle in [('ja','任意'),('en','optional'),('zh','可选')]:
    page.locator(f'.lang[data-lang="{lang}"]').click()
    assert needle in page.locator('#graph-guide').inner_text()
   page.locator('[data-mode="table"]').click()
   assert page.locator('.data-table tr').count()==3
   page.locator('[data-mode="task"]').click()
   assert page.locator('.field-card').count()==6
   page.locator('.lang[data-lang="zh"]').click()
   assert page.locator('#graph-guide').is_visible()
   overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
   assert not overflow,f'Horizontal overflow at {width}px'
   if width in (1440,390):
    page.locator('[data-mode="graph"]').click()
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.wait_for_timeout(250)
    page.screenshot(path=str(OUT/('homepage-desktop.png' if width==1440 else 'homepage-mobile.png')),full_page=True)
   page.close()
  for target in ('graph-guide.html','token-benchmark.html','codec.html'):
   p=browser.new_page(viewport={'width':390,'height':844})
   p.on('pageerror',lambda e: errors.append(str(e)));p.set_default_timeout(5000)
   load_offline(p,target)
   assert not p.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1'),f'Overflow: {target}'
   if target=='graph-guide.html':
    assert 'Authentication' in p.locator('body').inner_text()
    p.locator('[data-lang="en"]').click();assert 'What exactly does Authentication' in p.locator('body').inner_text()
    p.locator('[data-lang="ja"]').click();assert 'Authentication は何' in p.locator('body').inner_text()
    p.locator('[data-lang="zh"]').click();assert '身份认证' in p.locator('body').inner_text()
    p.screenshot(path=str(OUT/'graph-guide-mobile.png'),full_page=True)
   if target=='token-benchmark.html':
    assert 'Token' in p.title()
   p.close()
  assert not errors,errors
  browser.close()
 print('BROWSER R2 OK: 3 viewport sizes, 3 modes, 3 locales, 4 edges, Graph guide + Token + Codec, no JS errors or horizontal overflow.')
if __name__=='__main__':run()
