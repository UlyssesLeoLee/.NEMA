""".NEMA v1.2 R7 hardening tests. No live model/API claims."""
import unittest,sys,json,random,zipfile,hashlib
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import native,nemat
SRC='\t>Gext1 1\n A LoginAPI Authentication APIKey\n B TokenStore SessionStorage\nA>X>B Reads VerifySession HTTP401\n   RetryOnTimeout\n\n\n'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ('href','src'):
   if tag in ('a','img','link','script') and a.get(k):self.urls.append(a[k])
class R7Tests(unittest.TestCase):
 def test_graph_extensions_not_lost(self):
  r=native.view(SRC)[0];n=r['nodes'][0];e=r['edges'][0]
  self.assertEqual(n['extensions'],{'X3':'APIKey'})
  self.assertEqual(e['extensions'],{'X3':'HTTP401 RetryOnTimeout'})
  self.assertEqual(e['description'],'Verify session')
  self.assertEqual((e['source'],e['target']),('A','B'))
  self.assertNotIn('extensions',r['nodes'][1])
 def test_graph_extension_exact_literals(self):
  s='\t>G1 1\n A LoginAPI Auth SHA256\n B Store\nA>X>B Reads Check APIKey\n\n\n'
  d=native.view(s)[0];self.assertEqual(d['nodes'][0]['extensions']['X3'],'SHA256');self.assertEqual(d['edges'][0]['extensions']['X3'],'APIKey')
 def test_graph_extension_codec_lossless(self):
  for vals in ([],['APIKey','HTTP401'],['LoginAPI','TokenStore']):
   for pref in (False,True):self.assertEqual(nemat.decode(nemat.encode(SRC,vals,pref)),SRC)
 def test_tagged_json_kind(self):
  for path in sorted((ROOT/'examples').glob('*.positional-tagged.json')):
   data=json.loads(path.read_text('utf8'))
   for row in data:
    self.assertIn(row[0],('w','t','g'))
    self.assertIsInstance(row[1],str)
    self.assertIsInstance(row[2],int)
    self.assertEqual(len(row),4 if row[0]=='w' else 5)
 def test_benchmark_local_actual(self):
  import sentencepiece as spm
  results=json.loads((ROOT/'bench/latest_results.json').read_text('utf8'))
  for modeltype in ('bpe','unigram'):
   m=spm.SentencePieceProcessor(model_file=str(ROOT/'bench'/f'neutral_{modeltype}.model'))
   for s in results['scenarios']:
    name=s['scenario'];d=s['models'][modeltype]
    for f,k in (('.nema','nema'),('.json','json'),('.positional.json','json_positional'),('.positional.yaml','yaml_positional')):
     self.assertEqual(len(m.encode((ROOT/'examples'/(name+f)).read_text('utf8'))),d[k],(name,modeltype,k))
   tagged=json.loads((ROOT/'bench/tagged_json_audit_r7.json').read_text('utf8'))
   for row in tagged['scenarios']:
    self.assertEqual(len(m.encode((ROOT/'examples'/(row['scenario']+'.positional-tagged.json')).read_text('utf8'))),row[modeltype])
 def test_site_benchmark_replica_exact(self):
  raw=(ROOT/'website/benchmark_v12.js').read_text('utf8')
  data=json.loads(raw.split('=',1)[1].strip().rstrip(';'))
  source=json.loads((ROOT/'bench/latest_results.json').read_text('utf8'))
  self.assertEqual(len(data['scenarios']),len(source['scenarios']))
  for displayed,measured in zip(data['scenarios'],source['scenarios']):
   self.assertEqual(displayed['scenario'],measured['scenario'])
   self.assertEqual(displayed['models'],measured['models'])
 def test_site_current_demo_extended(self):
  raw=(ROOT/'website/demo_data.js').read_text('utf8');items=json.loads(raw.split('=',1)[1].strip().rstrip(';'))
  g=next(x for x in items if x['mode']=='graph');v=native.view(g['raw'])[0]
  self.assertEqual(v['nodes'][0]['extensions']['X3'],'APIKey')
  self.assertEqual(v['edges'][0]['extensions']['X3'],'HTTP401')
  self.assertEqual(g['data']['items'][0]['columns'][2],'APIKey')
  self.assertEqual(g['data']['items'][3]['columns'][2],'HTTP401')
 def test_repaired_label(self):
  s=(ROOT/'website/app.js').read_text('utf8')
  self.assertIn('JSON オブジェクト形式に対する BPE',s)
  self.assertNotIn("metricLabel:'英語 60 ドメイン：位置式 YAML",s)
  self.assertIn('slice(2).forEach',s)
 def test_current_site_links(self):
  for html in (ROOT/'website').glob('*.html'):
   h=Links();h.feed(html.read_text('utf8'))
   for url in h.urls:
    if url.startswith(('http:','https:','//','#','data:','mailto:','tel:')):continue
    path=unquote(urlsplit(url).path)
    if path:self.assertTrue((html.parent/path).exists(),f'Broken: {html} {url}')
 def test_interpreter_has_fix(self):
  p=ROOT/'downloads/NEMA_Interpreter_v1.2.zip'
  with zipfile.ZipFile(p) as z:
   self.assertIsNone(z.testzip())
   self.assertEqual(z.read('NEMA_Interpreter_v1.2/codec/native.py'),(ROOT/'codec/native.py').read_bytes())
 def test_generator_property_codec(self):
  rand=random.Random(20261107)
  values=['BuildLoginFlow','APIKey','HTTP401','汉字','^caret','\\\\','\\ ','\\t','\\=literal','42','']
  for i in range(90):
   fields=[rand.choice(values) for _ in range(6)]
   source='\tT'+str(i)+' 1\n'+' '.join(fields)+'\n\n\n'
   try:native.parse(source)
   except ValueError:continue
   for d in ([],['BuildLoginFlow'],['APIKey','HTTP401']):
    encoded=nemat.encode(source,d,True)
    self.assertEqual(nemat.decode(encoded),source)
 def test_golden_training(self):
  p=ROOT/'training/R7_GRAPH_EXTENSION_GOLDEN.jsonl'
  self.assertTrue(p.exists())
  for ln in p.read_text('utf8').splitlines():
   obj=json.loads(ln)
   self.assertEqual(native.view(obj['nema']),obj['expected_view'])
if __name__=='__main__':unittest.main()
