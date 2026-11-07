"""Website R3 graph-hover documentation, content source and interface integrity."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'website'

class GraphHoverR3(unittest.TestCase):
    def test_v11_syntax_unchanged(self):
        raw=(ROOT/'examples/website_samples.json').read_text()
        graph=next(x for x in json.loads(raw) if x['mode']=='graph')
        n=next(x for x in graph['data']['items'] if x['kind']=='node' and x['id']=='A')
        e=next(x for x in graph['data']['items'] if x['kind']=='edge' and x['id']=='Y')
        self.assertEqual(n['columns'][1],'Authentication')
        self.assertEqual(e['direction'],'<')
        self.assertEqual((e['left'],e['right']),('B','C'))
        self.assertIn('A>X>B Reads VerifySession',graph['raw'])
        self.assertIn('  CacheExpiredRetryOnce',graph['raw'])
    def test_data_bound_hover_card(self):
        app=(WEB/'app.js').read_text()
        for token in ['function graphic(data)', 'item.columns[1]||t.hoverOptional', 'item.direction===\'<\'?', 'pointerenter', 'pointerleave', "group.addEventListener('focus'", "ev.key==='Escape'", "ev.key==='Enter'", "setAttribute('role','tooltip')", 'tooltip.hidden=false', 'tooltip.hidden=true', 'pointermove', 'pointer-events:none']:
            if token=='pointer-events:none':
                self.assertIn(token,(WEB/'styles.css').read_text())
            else:
                self.assertIn(token,app)
        self.assertIn('group.setAttribute(\'aria-label\'',app)
    def test_all_locales_mention_hover(self):
        app=(WEB/'app.js').read_text()
        guide=(WEB/'graph-guide.js').read_text()
        for hint in ['hoverNodeKind','hoverEdgeKind','hoverHelp','hoverOptional']:
            self.assertGreaterEqual(app.count('"'+hint+'"'),3)
        for hint in ['hoverGuide','interTitle','intTouch','intKeyboard']:
            self.assertGreaterEqual(guide.count('"'+hint+'"'),3)
        self.assertIn('data-t="interTitle"',(WEB/'graph-guide.html').read_text())
    def test_notes_from_existing_schema(self):
        for lang in ('zh','ja','en'):
            text=(ROOT/'docs'/f'GRAPH_FIELD_GUIDE_{lang}.md').read_text()
            self.assertIn('Authentication',text)
            self.assertIn('VerifySession',text)
            self.assertIn('X2',text)
            self.assertTrue('hover' in text.lower() or '悬停' in text or 'ホバー' in text)
        self.assertTrue((ROOT/'docs/GRAPH_HOVER_RENDERER_DESIGN.md').exists())
        self.assertTrue((ROOT/'tests/test_browser_r3_hover.py').exists())
    def test_rendering_does_not_add_new_wire_grammar(self):
        hover=(ROOT/'docs/GRAPH_HOVER_RENDERER_DESIGN.md').read_text()
        self.assertIn('非 NEMA 协议升级',hover)
        self.assertIn('pointer-events:none',hover)
        self.assertIn('C → B',hover)
        self.assertIn('GRAPH_HOVER_RENDERER_DESIGN.md',(ROOT/'integrations/IDE1.0_INTEGRATION.md').read_text())
        self.assertIn('GRAPH_HOVER_RENDERER_DESIGN.md',(ROOT/'integrations/IME1.0_INTEGRATION.md').read_text())
    def test_token_benchmark_is_unmodified(self):
        bench=json.loads((ROOT/'bench/results.json').read_text())
        en=next(x for x in bench['scenarios'] if x['scenario']=='en_60_compact')
        self.assertEqual((en['tokenizers']['bpe']['native'],en['tokenizers']['bpe']['yaml'],en['tokenizers']['bpe']['optimized']),(3012,3849,1953))

if __name__=='__main__':unittest.main()
