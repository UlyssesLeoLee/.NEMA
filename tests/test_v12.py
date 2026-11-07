import unittest,json,sys,zipfile,subprocess,random,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import native,nemat

LF=lambda *items:'\n'.join(items)+'\n\n\n'
SAMPLE=LF('\t>G1 1',' A LoginAPI Authentication',' B TokenStore SessionStorage','A>X>B Reads VerifySession','  CacheExpiredRetryOnce','B<Y<A Notifies StatusReady','A=U=B Shares SecurityPolicy','A>P>A Retry Maximum3Attempts')

class NemaV12Tests(unittest.TestCase):
 def test_what_first(self):
  d=native.view(LF('\tT1 1','BuildLoginFlow'))[0];self.assertEqual(d['fields']['What'],'Build login flow');self.assertEqual(d['fields']['Who'],'')
 def test_english_http(self):self.assertEqual(native.view(LF('\tT1 1','What','HTTPItIs'),'en')[0]['fields']['What'],'What HTTP it is')
 def test_im_what(self):self.assertEqual(native.view(LF('\tT1 1','I',"'m",'what?'),'en')[0]['fields']['What'],"I'm what?")
 def test_cjk(self):
  for sample in ('审核登录流程','ログイン処理を確認する'):
   self.assertEqual(native.view(LF('\tT1 1',sample))[0]['fields']['What'],sample)
 def test_order(self):self.assertEqual(tuple(native.FIELD_NAMES),('What','Why','How','Who','When','Where'))
 def test_graph_parse(self):
  d=native.view(SAMPLE)[0];self.assertEqual([x['id'] for x in d['nodes']],['A','B']);self.assertEqual(d['nodes'][0]['name'],'LoginAPI');self.assertEqual(d['nodes'][0]['description'],'Authentication');self.assertEqual(d['edges'][0]['description'],'Verify session cache expired retry once')
 def test_edges(self):
  e=native.view(SAMPLE)[0]['edges'];self.assertEqual([(x['id'],x['source'],x['target'],x['direction']) for x in e],[('X','A','B','>'),('Y','A','B','<'),('U','A','B','='),('P','A','A','>')])
 def test_node_one_space_only(self):
  for s in (LF('\t>G1 1','A LoginAPI Authentication'),LF('\t>G1 1','  A LoginAPI Authentication')):
   with self.assertRaises(ValueError):native.parse(s)
 def test_edge_only_zero_space(self):
  with self.assertRaises(ValueError):native.parse(LF('\t>G1 1',' A LoginAPI',' B TokenStore',' A>X>B Reads'))
 def test_multiple_domains_no_blank(self):
  s=LF('\tT1 1','What','\t>G1 1',' A LoginAPI',' B TokenStore','A>X>B Reads','\tT2 1','Another');self.assertEqual(len(native.view(s)),3)
 def test_table_and_continuation(self):
  s=LF('\tT1 1','\tAgent Status Note','Claude Ready AuthPassed','  VerifyAgain','Codex Done Verified');v=native.view(s)[0];self.assertEqual(v['mode'],'table');self.assertEqual(len(v['records']),2);self.assertEqual(v['records'][0]['Note'],'Auth passed verify again')
 def test_table_empty(self):
  with self.assertRaises(ValueError):native.parse(LF('\tT1 1','\tAgent Status Note'))
 def test_dangling(self):
  with self.assertRaises(ValueError):native.parse(LF('\t>G1 1',' A LoginAPI','A>X>B Reads'))
 def test_duplicate_node(self):
  with self.assertRaises(ValueError):native.parse(LF('\t>G1 1',' A LoginAPI',' A TokenStore'))
 def test_duplicate_edge(self):
  with self.assertRaises(ValueError):native.parse(LF('\t>G1 1',' A LoginAPI',' B TokenStore','A>X>B Reads','A>X>B Writes'))
 def test_duplicate_domain_id(self):
  with self.assertRaises(ValueError):native.parse(LF('\tT1 1','What','\tT1 2','Other'))
 def test_no_crlf(self):
  with self.assertRaises(ValueError):native.parse(LF('\tT1 1','What').replace('\n','\r\n'))
 def test_eof(self):
  for src in ('\tT1 1\nWhat\n','\tT1 1\nWhat\n\n','\tT1 1\nWhat\n\n\n\n'):
   with self.assertRaises(ValueError):native.parse(src)
 def test_native_escape(self):
  s=LF('\tT1 1',r'Hello\ World Why');self.assertEqual(native.parse(s)[0]['fields'][0],['Hello World'])
 def test_native_invalid_escape(self):
  with self.assertRaises(ValueError):native.parse(LF('\tT1 1',r'Invalid\z'))
 def test_literal_graph_id(self):self.assertEqual(native.view(LF('\t>G1 1',' A LoginAPI'))[0]['nodes'][0]['name'],'LoginAPI')
 def test_nemat_roundtrip(self):
  for x in (SAMPLE,LF('\tT1 1','What','HTTPItIs'),LF('\tTb1 1','\tAgent Status','Claude Ready','Codex Done')):
   for pre in (True,False):
    cand=nemat.encode(x,[],pre);self.assertEqual(nemat.decode(cand),x)
 def test_dictionary_roundtrip(self):
  s=LF('\tT001 1','BuildLoginFlow PreventLeak','\tT002 1','BuildLoginFlow PreventLeak')
  for k in ([],['BuildLoginFlow'],['PreventLeak','BuildLoginFlow']):
   self.assertEqual(nemat.decode(nemat.encode(s,k)),s)
 def test_graph_dictionary_preserves_structure(self):
  s=LF('\t>G1 1',' A LoginAPI Authentication',' B LoginAPI Authentication','A>X>B Reads Authentication')
  self.assertEqual(nemat.decode(nemat.encode(s,['Authentication','LoginAPI'])),s)
 def test_caret_escaping(self):
  s=LF('\tT1 1',r'Caret^Value Token^2');wire=nemat.encode(s,['Caret^Value']);self.assertEqual(nemat.decode(wire),s);self.assertIn(r'\^',wire)
 def test_preserve_backslash(self):
  s=LF('\tT1 1',r'Path\\ToDir');self.assertEqual(nemat.decode(nemat.encode(s)),s)
 def test_lone_caret_malformed_wire(self):
  with self.assertRaises(ValueError):nemat.decode(LF('\tT1 1','^123'))
 def test_bad_dictionary_count(self):
  with self.assertRaises(ValueError):nemat.decode(LF('\t$99','value'))
 def test_high_entropy_fallback(self):
  raw=(ROOT/'examples/high_entropy_60.nema').read_text();c=nemat.optimize(raw);self.assertTrue(c.text==raw or nemat.decode(c.text)==raw)
 def test_all_current_cases(self):
  for p in sorted((ROOT/'examples').glob('*.nema')):
   with self.subTest(p=p.name):
    s=p.read_text();native.parse(s);res=nemat.optimize(s);self.assertEqual(s,(res.text if res.mode=='native' else nemat.decode(res.text)))
 def test_training_valid(self):
  for f in ['sft_train_v12.jsonl','sft_eval_v12.jsonl']:
   for ln in (ROOT/'training'/f).read_text(encoding='utf-8').splitlines():
    o=json.loads(ln);native.parse(o['messages'][-1]['content'])
 def test_training_negative(self):
  for ln in (ROOT/'training/adversarial_v12.jsonl').read_text(encoding='utf-8').splitlines():
   o=json.loads(ln)
   with self.assertRaises(ValueError):native.parse(o['source'])
 def test_semantic_json_baseline(self):
  from importlib.machinery import SourceFileLoader
  for name in ('english_60','chinese_60','japanese_60','table_200','graph_40n_160e','high_entropy_60','short_what','graph_3n_4e'):
   raw=(ROOT/'examples'/f'{name}.nema').read_text();ref=json.loads((ROOT/'examples'/f'{name}.json').read_text());self.assertEqual(native.view(raw),ref)
 def test_benchmark_source_exists(self):
  data=json.loads((ROOT/'bench/latest_results.json').read_text())
  for s in data['scenarios']:
   self.assertIn('json_positional',s['models']['bpe']);self.assertIn('unigram',s['models'])
 def test_packaged_interpreter(self):
  p=ROOT/'downloads/NEMA_Interpreter_v1.2.zip';self.assertTrue(p.is_file())
  with zipfile.ZipFile(p) as z:
   self.assertIsNone(z.testzip());self.assertIn('NEMA_Interpreter_v1.2/codec/native.py',z.namelist())
 def test_web_literals_current(self):
  s=(ROOT/'website/demo_data.js').read_text();json_body=s.split('=',1)[1].strip().rstrip(';');demo=json.loads(json_body)
  for d in demo:
   view=native.view(d['raw'])[0];self.assertEqual(view['mode'],d['mode']);self.assertEqual(view['id'],d['id'])
 def test_brand_title(self):
  s=(ROOT/'website/index.html').read_text();self.assertIn('<span class="period">.</span>NEMA',s);self.assertIn('下载解释器',s)
 def test_website_json_data(self):
  s=(ROOT/'website/benchmark_v12.js').read_text();obj=json.loads(s.split('=',1)[1].strip().rstrip(';'));report=json.loads((ROOT/'bench/latest_results.json').read_text());self.assertEqual(len(obj['scenarios']),len(report['scenarios']))
 def test_threejs_actual(self):
  s=(ROOT/'website/three-hero.js').read_text();self.assertIn('three@0.187.0/build/three.module.js',s);self.assertIn('new THREE.WebGLRenderer',s)
 def test_downloadable_docs(self):
  for f in ('SPEC_v1.2_zh.md','AI_TRAINING_v1.2.md','IDE1.0_INTEGRATION_v1.2.md','IME1.0_INTEGRATION_v1.2.md','JSON_COMPARISON_METHOD_v1.2.md'):
   self.assertTrue((ROOT/'docs'/f).is_file())

if __name__=='__main__':unittest.main(verbosity=2)
