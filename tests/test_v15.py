"""Current .NEMA v1.5 regression suite; old tests archived, not incorrectly run as current."""
import unittest,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from codec import native,nemat
from tools.migrate_v13_to_v15 import migrate
from tools import native_v13_legacy as v13
class GrammarV15(unittest.TestCase):
 def test_three_header_prefixes_and_modes(self):
  s=' ?T1 1\nDo Why\n T2 1\nA Ready\n >G1 1\nA App\nB Store\nA>X>B Reads\n\n\n'
  self.assertEqual([d['mode'] for d in native.view(s)],['5w1h','table_implicit','graph'])
  self.assertEqual([d['id'] for d in native.view(s)],['T1','T2','G1'])
 def test_header_exact_ascii_space_only(self):
  for h in ['\t?T1 1','\u3000?T1 1','  ?T1 1','?T1 1','\t>T1 1','\u3000>T1 1','\tT1 1']:
   with self.subTest(h=h),self.assertRaises(ValueError):native.parse(h+'\nBuild\n\n\n')
 def test_explicit_table_header_body_tab_retained(self):
  doc=' T1 1\n Agent Status Note\nA Ready First\nB Blocked Second\n\n\n'
  o=native.view(doc)[0];self.assertEqual(o['mode'],'table');self.assertEqual(o['columns'],['Agent','Status','Note']);self.assertEqual(len(o['records']),2)
 def test_implicit_column_expansion_and_continuation(self):
  doc=' T1 1\nA Ready\nB Blocked Detail\n  More\n\n\n'
  o=native.view(doc)[0];self.assertEqual(o['columns'],['column1','column2','column3']);self.assertEqual(o['records'][0]['column3'],'');self.assertEqual(len(o['records']),2)
  self.assertIn('more',o['records'][1]['column3'])
 def test_graph_x0_x2_x3(self):
  s=' >G1 1\nA LoginAPI Authentication\n MoreDetail\n  APIKey\nB TokenStore\nA>X>B Reads VerifySession\n\n\n'
  o=native.view(s)[0];self.assertEqual(o['nodes'][0]['name'],'LoginAPI');self.assertIn('more',o['nodes'][0]['description']);self.assertEqual(o['nodes'][0]['extensions']['X3'],'APIKey');self.assertEqual(o['edges'][0]['source'],'A')
 def test_graph_bad_edge_refusal(self):
  for bad in ['A>X B','A>X<B Reads','A=X>B Read','A> B','A >X>B']:
   with self.subTest(bad=bad),self.assertRaises(ValueError):native.parse(' >G1 1\nA Node\nB Node\n'+bad+'\n\n\n')
 def test_graph_duplicate_or_dangling(self):
  for txt in [' >G1 1\nA One\nA Two\n\n\n',' >G1 1\nA One\nA>X>B Reads\n\n\n']:
   with self.assertRaises(ValueError):native.parse(txt)
 def test_exact_lf_and_u3000(self):
  for s in [' T1 1\n\tA B\nC D\n\n\n',' ?T1 1\nA\n\n',' ?T1 1\r\nA\r\n\r\n\r\n',' ?T1 1\nA\u3000B\n\n\n']:
   with self.assertRaises(ValueError):native.parse(s)
 def test_active_examples_all_valid(self):
  for f in (ROOT/'examples').glob('*.nema'):
   with self.subTest(file=f.name):self.assertTrue(native.view(f.read_text(encoding='utf-8')))
 def test_transport_dictionary_roundtrip(self):
  for file in ['implicit_table_v15.nema','explicit_5w1h_v15.nema','explicit_table_v15.nema','graph_v15.nema','complete_v12.nema']:
   s=(ROOT/'examples'/file).read_text()
   with self.subTest(file=file):
    self.assertEqual(nemat.decode(nemat.encode(s)),s)
    self.assertEqual(nemat.decode(nemat.encode(s,['LoginAPI','HTTP401'])),s)
 def test_migrate_semantics(self):
  for src in ['\tT1 1\nOne Two\n\n\n','\tT2 1\n\tAgent Status\nA Ready\n\n\n','\t>G1 1\nA App\nB Store\nA>X>B Reads\n\n\n']:
   out=migrate(src);self.assertEqual(v13.view(src),native.view(out))
   self.assertTrue(out.startswith(' '))
 def test_migrate_rejects_v15_double_migration(self):
  with self.assertRaises(ValueError):migrate(' ?T1 1\nHello\n\n\n')
 def test_standalone_codec_parity(self):
  for name in ('native.py','nemat.py'):
   self.assertEqual((ROOT/'codec'/name).read_bytes(),(ROOT/'_Interpreter_Standalone/codec'/name).read_bytes())
if __name__=='__main__':unittest.main()
