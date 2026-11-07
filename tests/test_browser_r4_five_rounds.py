"""Run via python tests/test_browser_r4_five_rounds.py (requires Chromium / Playwright)."""
from playwright.sync_api import sync_playwright
from test_browser_r2 import load_offline


def run():
    checks=0;errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width,height in [(1440,960),(768,1024),(390,844)]:
            p=browser.new_page(viewport={'width':width,'height':height})
            p.on('pageerror',lambda error: errors.append(str(error)))
            load_offline(p,'index.html')
            # Round 1: single-source benchmark (numbers come from benchmark_data.js).
            expected=p.evaluate("BENCHMARK.cases.find(x=>x.scenario==='en_60_compact').tokenizers.bpe")
            assert p.locator('#metricValue').inner_text()==f"{expected['vs_yaml_pct']:.2f}%"
            assert str(expected['optimized']) in p.locator('#benchmarkBars').inner_text().replace(',','')
            checks+=2
            # Round 2: 5W1H/Table/Graph tablist navigable without pointer.
            tab=p.locator('[data-mode="task"]');tab.focus();tab.press('ArrowRight')
            assert p.locator('[data-mode="table"]').get_attribute('aria-selected')=='true'
            assert p.evaluate('document.activeElement.dataset.mode')=='table'
            assert p.locator('#rendered').get_attribute('aria-labelledby')=='nema-tab-table'
            p.locator('[data-mode="table"]').press('End')
            assert p.evaluate('document.activeElement.dataset.mode')=='graph'
            checks+=4
            # Round 3: preserve keyboard focus after SVG and picker rebuild.
            x=p.locator('svg [data-graph-kind="edge"][data-graph-id="X"]');x.focus();x.press('Enter')
            assert p.evaluate('document.activeElement?.dataset.graphId')=='X'
            assert 'A → B' in p.locator('.graph-inspector').inner_text()
            picker=p.locator('.graph-choice[data-picker-id="Y"]');picker.focus();picker.press('Enter')
            assert p.evaluate('document.activeElement?.dataset.pickerId')=='Y'
            assert 'C → B' in p.locator('.graph-inspector').inner_text()
            checks+=4
            # Round 4: hover is read-only and descriptions come from X2.
            before=p.locator('#sourceCode').text_content()
            inspected=p.locator('.graph-inspector').inner_text()
            a=p.locator('svg [data-graph-kind="node"][data-graph-id="A"]');a.hover(force=True)
            tooltip=p.locator('.graph-hover-tooltip')
            assert 'Authentication' in tooltip.inner_text()
            assert p.locator('#sourceCode').text_content()==before
            assert p.locator('.graph-inspector').inner_text()==inspected
            checks+=3
            # Round 5: opposite-direction multiple edges and multiple self loops receive separate lanes.
            p.evaluate("""() => {
              const graph=NEMA_DEMO.find(x=>x.id==='Gauth1');
              graph.data.items.push({kind:'edge',id:'R',left:'B',right:'A',direction:'>',columns:['Responds','Acknowledged']});
              graph.data.items.push({kind:'edge',id:'S',left:'A',right:'A',direction:'>',columns:['RetryAgain','Limited']});
            }""")
            p.locator('[data-mode="task"]').click();p.locator('[data-mode="graph"]').click()
            paths={i:p.locator(f'svg [data-graph-id="{i}"] .edge-visible').get_attribute('d') for i in ['X','R','P','S']}
            assert paths['X']!=paths['R']
            assert paths['P']!=paths['S']
            p.locator('svg [data-graph-id="R"]').hover(force=True)
            assert 'B → A' in p.locator('.graph-hover-tooltip').inner_text()
            checks+=3
            assert not p.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            checks+=1
            p.close()
        # Round 3: Guide aria labels localize as site language changes.
        p=browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        p.on('pageerror',lambda error: errors.append(str(error)))
        load_offline(p,'graph-guide.html')
        for lang,expected in [('zh','关系说明'),('ja','Edge 説明'),('en','Edge note')]:
            p.locator(f'[data-lang="{lang}"]').click()
            label=p.locator('[data-graph-item="X"]').get_attribute('aria-label')
            assert expected in label,(lang,label)
            p.locator('[data-graph-item="X"]').tap()
            assert 'Verify session' in p.locator('#guideGraphTooltip').inner_text()
            p.locator('[data-graph-item="X"]').tap()
            checks+=3
        assert not errors,errors
        browser.close()
    print(f'BROWSER R4 FIVE-ROUND REVIEW PASS: {checks} assertions across three widths + 3 localized touch/ARIA checks')

if __name__=='__main__':run()
