"""Executable Chromium acceptance tests for NEMA R3 Node/Edge hover UX."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_browser_r2 import load_offline

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'website'/'previews'
OUT.mkdir(exist_ok=True,parents=True)

def run():
    tests=0
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        errors=[]
        for width,height in ((1440,960),(390,844),(768,1024)):
            p=browser.new_page(viewport={'width':width,'height':height})
            p.on('pageerror',lambda error: errors.append(str(error)))
            load_offline(p,'index.html')
            p.locator('[data-mode="graph"]').click()
            a=p.locator('[data-graph-kind="node"][data-graph-id="A"]')
            x=p.locator('[data-graph-kind="edge"][data-graph-id="X"]')
            y=p.locator('[data-graph-kind="edge"][data-graph-id="Y"]')
            u=p.locator('[data-graph-kind="edge"][data-graph-id="U"]')
            tt=p.locator('.graph-hover-tooltip')
            assert tt.is_hidden()
            a.hover(force=True)
            assert tt.is_visible() and 'Authentication' in tt.inner_text()
            assert 'A · LoginAPI' in tt.inner_text()
            assert 'X2' in tt.inner_text()
            tests+=1
            if width==1440:
                p.screenshot(path=str(OUT/'graph-node-hover-desktop.png'),full_page=False)
            x.hover(force=True)
            assert tt.is_visible() and 'Verify session' in tt.inner_text()
            assert 'A → B' in tt.inner_text()
            tests+=1
            if width==1440:
                p.screenshot(path=str(OUT/'graph-edge-hover-desktop.png'),full_page=False)
            y.hover(force=True)
            assert 'C → B' in tt.inner_text() and 'Audit event' in tt.inner_text()
            tests+=1
            u.hover(force=True)
            assert 'A — C' in tt.inner_text() and 'Security policy' in tt.inner_text()
            tests+=1
            a.focus()
            assert 'Authentication' in tt.inner_text()
            a.press('Escape')
            assert tt.is_hidden()
            tests+=1
            x.focus();assert tt.is_visible()
            x.press('Enter')
            assert 'Verify session' in p.locator('.graph-inspector').inner_text()
            tests+=1
            p.locator('.lang[data-lang="ja"]').click()
            p.locator('[data-graph-kind="node"][data-graph-id="A"]').focus()
            assert 'NODE の説明' in p.locator('.graph-hover-tooltip').inner_text()
            p.locator('.lang[data-lang="en"]').click()
            p.locator('[data-graph-kind="node"][data-graph-id="A"]').focus()
            assert 'NODE DESCRIPTION' in p.locator('.graph-hover-tooltip').inner_text()
            tests+=1
            assert not p.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            p.close()
        for lang,needle in (('zh','Authentication'),('ja','Authentication'),('en','Authentication')):
            p=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
            p.on('pageerror',lambda error:errors.append(str(error)))
            load_offline(p,'graph-guide.html')
            p.locator('[data-lang="'+lang+'"]').click()
            node=p.locator('[data-graph-item="A"]')
            node.tap()
            tt=p.locator('#guideGraphTooltip')
            assert tt.is_visible() and needle in tt.inner_text()
            tests+=1
            p.locator('[data-graph-item="X"]').tap()
            assert 'Verify session' in tt.inner_text() and 'A → B' in tt.inner_text()
            tests+=1
            p.locator('[data-graph-item="B"]').tap()
            assert 'Session storage' in tt.inner_text()
            tests+=1
            p.locator('[data-graph-item="B"]').tap()
            assert tt.is_hidden()
            tests+=1
            assert not p.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            if lang=='zh':
                p.locator('[data-graph-item="X"]').tap()
                p.screenshot(path=str(OUT/'graph-guide-edge-tap-mobile.png'),full_page=True)
            p.close()
        assert not errors,errors
        browser.close()
    print(f'BROWSER R3 HOVER PASS: {tests} checks + no JS errors across three viewports and locales')

if __name__=='__main__':run()
