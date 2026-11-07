"""NEMA website R2 static and parser consistency checks."""
from pathlib import Path
import json,re,unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codec.native import parse,view
BASE=Path(__file__).resolve().parents[1]
W=BASE/'website'
class TestWebsiteR2(unittest.TestCase):
 def test_graph_source_matches_actual_native_view(self):
  items=json.loads((BASE/'examples/website_samples.json').read_text())
  graph=next(x for x in items if x['mode']=='graph')
  parsed=parse(graph['raw'])
  rendered=view(graph['raw'])[0]
  self.assertEqual(len(parsed),1)
  self.assertEqual(rendered['mode'],'graph')
  nodes=[x for x in graph['data']['items'] if x['kind']=='node']
  edges=[x for x in graph['data']['items'] if x['kind']=='edge']
  self.assertEqual([(n['id'],n['columns'][0],n['columns'][1]) for n in nodes],[(n['id'],n['name'],n['description']) for n in rendered['nodes']])
  self.assertEqual([(e['id'],e['columns'][0],e['columns'][1]) for e in edges],[(e['id'],e['name'],e['description']) for e in rendered['edges']])
  self.assertEqual(next(n for n in nodes if n['id']=='A')['columns'][1],'Authentication')
  self.assertEqual(next(e for e in rendered['edges'] if e['id']=='Y')['source'],'C')
  self.assertEqual(next(e for e in rendered['edges'] if e['id']=='Y')['target'],'B')
 def test_demo_js_json_match(self):
  expected=json.loads((BASE/'examples/website_samples.json').read_text())
  js=(W/'demo_data.js').read_text().strip()
  self.assertEqual(json.loads(js.removeprefix('const NEMA_DEMO = ').removesuffix(';')),expected)
 def test_internal_links_resolve(self):
  for file in W.glob('*.html'):
   html=file.read_text()
   for uri in re.findall(r'\b(?:href|src)="([^"]+)"',html):
    if not uri or uri.startswith(('http://','https://','#','data:','mailto:')):continue
    if '#' in uri:uri=uri.split('#',1)[0]
    self.assertTrue((file.parent/uri).exists(),f'{file.name} missing {uri}')
 def test_graph_guides_three_languages(self):
  for lang in ('zh','ja','en'):
   spec=(BASE/'docs'/f'GRAPH_FIELD_GUIDE_{lang}.md').read_text()
   for needle in ('Authentication','\\=LoginAPI','A>X>B','A<Y<B','X0','X1','X2'):
    self.assertIn(needle,spec)
 def test_writing_and_protocol_scope(self):
  spec=(BASE/'docs/NEMA_SPEC_v1.1_zh.md').read_text()
  self.assertIn('X0 What、X1 Why、X2 How、X3 Who、X4 When、X5 Where',spec)
  self.assertIn('X2 的说明只用于 AI 理解',spec)
  self.assertIn('`\\=LoginAPI`',spec)
  html=(W/'graph-guide.html').read_text()
  self.assertIn('⇥>G1 1',html)
  self.assertIn('⇥>1',html) # explicitly marked invalid shorthand
 def test_benchmark_metrics_not_changed(self):
  cases=json.loads((BASE/'bench/results.json').read_text())
  # Compare the published core numbers with the actual source dataset rather than editing them.
  entries=cases['scenarios']
  ref=next(x for x in entries if x['scenario']=='en_60_compact')['tokenizers']['bpe']
  self.assertEqual(ref['native'],3012)
  self.assertEqual(ref['yaml'],3849)
  self.assertEqual(ref['optimized'],1953)
  self.assertAlmostEqual(100*(ref['yaml']-ref['native'])/ref['yaml'],21.75,places=2)
 def test_no_wrong_english_example_in_current_site(self):
  for file in [*W.glob('*.html'),*W.glob('*.js')]:
   self.assertNotIn("Who I'm I",file.read_text())
 def test_website_has_accessible_navigation(self):
  html=(W/'index.html').read_text()
  self.assertIn('id="mainNav"',html)
  self.assertIn('id="graph-guide"',html)
  self.assertIn('class="mode-tabs"',html)
  self.assertIn('href="graph-guide.html"',html)
if __name__=='__main__':unittest.main()
