"""Optional offline Playwright Chromium smoke. Loads shipped HTML, CSS and JS without network access."""
import pathlib,re,base64
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
WEB=ROOT/'website'

def load(page,filename,scripts):
    html=(WEB/filename).read_text(encoding='utf-8')
    html=re.sub(r'<script[^>]*src="[^"]*"[^>]*></script>','',html)
    html=re.sub(r'<link[^>]*rel="stylesheet"[^>]*>','',html)
    logo=base64.b64encode((WEB/'assets/nema-logo.svg').read_bytes()).decode('ascii')
    html=html.replace('src="assets/nema-logo.svg"', f'src="data:image/svg+xml;base64,{logo}"')
    page.set_content(html,wait_until='load')
    css=(WEB/'styles.css').read_text(encoding='utf-8')
    art=base64.b64encode((WEB/'assets/ariadne-maze.webp').read_bytes()).decode('ascii')
    css=css.replace("url('assets/ariadne-maze.webp')", "url('data:image/webp;base64,"+art+"')")
    page.add_style_tag(content=css)
    for script in scripts:
        page.add_script_tag(content=(WEB/script).read_text(encoding='utf-8'))

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':850})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        load(page,'index.html',['demo_data.js','graph.js','app.js'])
        page.screenshot(path=str(WEB/'preview-desktop.png'))
        page.locator('[data-demo="graph"]').click()
        page.locator('.graph-edge').first.wait_for()
        edges=page.locator('.graph-edge'); assert edges.count()==8,edges.count()
        assert page.locator('.graph-edge[marker-end]').count()==7
        for eid,expected in [('Z','C → B'),('R','A → B'),('U','A — C'),('P','A → A')]:
            # svg path may be behind label; dispatch click as a direct interaction.
            page.locator(f'.graph-edge[data-edge-id="{eid}"]').dispatch_event('click')
            assert expected in page.locator('.edge-detail').inner_text(),(eid,page.locator('.edge-detail').inner_text())
        assert not page.locator('.graph-edge[data-edge-id="U"]').get_attribute('marker-end')
        page.locator('.graph-edge[data-edge-id="Z"]').dispatch_event('click')
        page.locator('#demo').scroll_into_view_if_needed()
        page.screenshot(path=str(WEB/'preview-graph-v1.5.png'))
        page.locator('[data-lang="ja"]').click();assert page.locator('html').get_attribute('lang')=='ja-JP'
        page.locator('[data-lang="en"]').click();assert page.locator('html').get_attribute('lang')=='en'
        page.locator('[data-demo="table_no_header"]').click()
        assert 'column1' in page.locator('#renderPanel').inner_text()
        page.locator('[data-demo="table_with_header"]').click()
        assert 'Agent' in page.locator('#renderPanel').inner_text()
        load(page,'token-bench.html',['benchmark_data.js','benchmark_samples.js','bench.js'])
        assert page.locator('#nativeTokens').inner_text().strip() not in ('','—')
        assert not errors, errors
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'desktop x overflow'
        mobile=browser.new_page(viewport={'width':390,'height':844})
        load(mobile,'index.html',['demo_data.js','graph.js','app.js'])
        mobile.screenshot(path=str(WEB/'preview-mobile.png'))
        mobile.locator('[data-demo="graph"]').click()
        assert mobile.locator('.graph-edge').count()==8
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),'mobile x overflow'
        browser.close()
        print('BROWSER PASS: 8 edges, 7 arrows, reverse/loop/undirected, locale, table, token page, desktop/mobile')
if __name__=='__main__':main()
