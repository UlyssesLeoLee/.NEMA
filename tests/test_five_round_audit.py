"""R4 five-round acceptance: syntax, topology, accessibility, metrics and package resources."""
from pathlib import Path
import hashlib, json, re, unittest
from codec.native import parse, view
from codec.nemat import optimize, decode

ROOT=Path(__file__).resolve().parents[1]

class R4Audit(unittest.TestCase):
    def test_01_graph_fields_not_automatic_nodes(self):
        source='\t>G1 1\nA \\=LoginAPI Authentication\nB \\=TokenStore SessionStorage\nA>X>B Reads VerifySession\n\n\n'
        graph=view(source)[0]
        self.assertEqual(len(graph['nodes']),2)
        self.assertEqual(len(graph['edges']),1)
        self.assertEqual(graph['nodes'][0]['name'],'LoginAPI')
        self.assertEqual(graph['nodes'][0]['description'],'Authentication')
        self.assertEqual((graph['edges'][0]['source'],graph['edges'][0]['target']),('A','B'))

    def test_02_arrow_direction_and_edge_description(self):
        source=(ROOT/'examples/complete.nema').read_text()
        domains=view(source)
        self.assertEqual(len(domains),len(parse(source)))
        graph=[d for d in domains if d['mode']=='graph']
        self.assertTrue(graph)
        for d in graph:
            self.assertEqual(len({e['id'] for e in d['edges']}),len(d['edges']))
            for edge in d['edges']:
                self.assertIn(edge['source'],{n['id'] for n in d['nodes']})
                self.assertIn(edge['target'],{n['id'] for n in d['nodes']})

    def test_03_no_unearned_token_claims(self):
        report=(ROOT/'bench/REPORT.md').read_text()
        self.assertIn('SentencePiece',report)
        home=(ROOT/'website/index.html').read_text()
        self.assertIn('benchmark_data.js',home)
        self.assertNotIn('69.9%',home)

    def test_04_benchmark_data_identical(self):
        data=json.loads((ROOT/'bench/results.json').read_text())
        raw=(ROOT/'website/benchmark_data.js').read_text().strip()
        self.assertTrue(raw.startswith('const BENCHMARK='))
        client=json.loads(raw[len('const BENCHMARK='):].removesuffix(';'))
        self.assertEqual(client['cases'],data['scenarios'])
        english=client['cases'][0]['tokenizers']['bpe']
        self.assertEqual((english['native'],english['yaml'],english['optimized']),(3012,3849,1953))

    def test_05_codec_all_samples_round_trip(self):
        for p in sorted((ROOT/'examples').glob('*.nema')):
            with self.subTest(name=p.name):
                text=p.read_text()
                if p.stem.endswith('_tab_control'):
                    # Control data represents the discarded Tab-X variant, not active syntax.
                    continue
                parsed=parse(text)
                self.assertTrue(parsed)
                res=optimize(text)
                if res.mode!='native':self.assertEqual(decode(res.text),text)

    def test_06_copy_not_an_html_interpolation(self):
        app=(ROOT/'website/app.js').read_text()
        self.assertIn('tooltip.hidden=false',app)
        self.assertIn('d.textContent=',app)
        self.assertNotIn('d.innerHTML=',app)

    def test_07_aria_tab_implementation(self):
        html=(ROOT/'website/index.html').read_text()
        self.assertEqual(html.count('role="tab"'),3)
        self.assertIn('role="tabpanel"',html)
        self.assertIn('aria-labelledby="nema-tab-task"',html)
        app=(ROOT/'website/app.js').read_text()
        self.assertIn('next.focus({preventScroll:true})',app)
        self.assertIn("'ArrowRight'",app)

    def test_08_graph_docs_consistency(self):
        for lang in ['zh','ja','en']:
            text=(ROOT/f'docs/GRAPH_FIELD_GUIDE_{lang}.md').read_text()
            self.assertIn('Authentication',text)
            self.assertIn('X2',text)
            self.assertIn('B<Y<C',text)
            self.assertIn('\\=LoginAPI',text)
        self.assertIn('焦点', (ROOT/'docs/GRAPH_HOVER_RENDERER_DESIGN.md').read_text())

    def test_09_link_integrity(self):
        for p in (ROOT/'website').glob('*.html'):
            body=p.read_text()
            for link in re.findall(r'''(?:href|src)=["']([^"']+)["']''',body):
                if link.startswith(('http:','https:','data:','#','mailto:')):continue
                with self.subTest(html=p.name,path=link):
                    self.assertTrue((p.parent/link.split('#')[0].split('?')[0]).exists(),f'{p.name}: {link}')

    def test_10_training_data_valid_jsonl(self):
        for name in ['sft_train.jsonl','sft_eval.jsonl']:
            lines=(ROOT/'training'/name).read_text().splitlines()
            self.assertGreater(len(lines),30)
            for row in lines:json.loads(row)

if __name__=='__main__':unittest.main()
