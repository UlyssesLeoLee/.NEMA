from pathlib import Path
import subprocess,json,sys,zipfile,hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from codec import parse,render,encode,decode
files=list((root/'examples').glob('*.nema'))
for f in files:
 s=f.read_text(encoding='utf-8');r=render(s);assert r['domains']
 ch=encode(s);assert ch.text==s if ch.format=='nema' else decode(ch.text)==s
# Explicitly audit new table first-line behavior.
a=render((root/'examples/00_default_table_no_header.nema').read_text())['domains'][0]
b=render((root/'examples/01_explicit_table_header.nema').read_text())['domains'][0]
assert a['columns']==['column1','column2','column3'] and not a['explicit_header']
assert b['columns']==['Agent','Status','Note'] and b['explicit_header']
# Graph: B<Z<C -> C→B and explanatory continuation must be X2.
g=render((root/'examples/03_graph_complex.nema').read_text())['domains'][0]
z=[r for r in g['rows'] if r.get('edge',{}).get('id')=='Z'][0]
x=[r for r in g['rows'] if r.get('edge',{}).get('id')=='X'][0]
assert z['edge']['from']=='C' and z['edge']['to']=='B'
assert x['cells'][1]=='Reads' and 'When Token Is Valid' in x['cells'][2]
# Inline refs preserve atom.
ident=render((root/'examples/04_inline_shared_dictionary.nema').read_text())
assert ident['dictionary'][0]=='APIKey' and 'APIKey' in json.dumps(ident)
results=json.loads((root/'bench/results.json').read_text())['results']
assert len(results)==16
assert any(r['fixture']=='bench_high_entropy_120.nema' and r['method']=='native' for r in results)
for expected in ['website/index.html','website/token-bench.html','website/bench.js','website/app.js',
                 'website/benchmark_data.js','website/graph.js','tests/graph_renderer.test.js','docs/NEMA_SPEC_v1.5_zh.md',
                 'docs/IDE1.0/02_BASIC_AND_DETAILED_DESIGN.md',
                 'docs/IME1.0/02_BASIC_AND_DETAILED_DESIGN.md',
                 'training/nema_v1.5_train.jsonl','training/nema_v1.5_holdout.jsonl']:
 assert (root/expected).is_file(),expected
assert (root/'website/benchmark_data.js').read_text().count('bench_high_entropy_120.nema')>=2
assert [d['id'] for d in render('\t\\1\nA B\n\t?2\nHello\n\t>3\nA Node\n\n\n')['domains']]==['1','2','3']
assert any(r['edge']['from']=='C' and r['edge']['to']=='B' for r in g['rows'] if r.get('edge'))
print('PROJECT RELEASE CHECK: PASS; 15 fixtures; 16 tokenizer scenarios; numeric domain heads; graph direction; dictionary; all required files')
