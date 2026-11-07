"""Release v1.3 Graph: validation and legacy migration invariants."""
import unittest,sys,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import native,nemat
from tools.migrate_r7_to_v13 import migrate,old

class GraphV13(unittest.TestCase):
 def test_domain_header_fixed(self):
  s=(ROOT/'examples/graph_v13_canonical.nema').read_text()
  self.assertTrue(s.startswith('\t>Gauth1 1\nA LoginAPI'))
  self.assertEqual(native.HEADER.pattern,old.HEADER.pattern)
  self.assertEqual(native.view(s)[0]['id'],'Gauth1')
 def test_x0_nodes_and_edges(self):
  v=native.view((ROOT/'examples/graph_v13_canonical.nema').read_text())[0]
  self.assertEqual(len(v['nodes']),2)
  self.assertEqual(len(v['edges']),4)
  self.assertEqual(v['nodes'][0]['name'],'LoginAPI')
  self.assertEqual(v['edges'][0]['description'],'Verify session cache expired retry once')
  self.assertEqual(v['edges'][0]['extensions']['X3'],'HTTP401 RetryOnTimeout')
 def test_empty_invalid_ambiguous_relation(self):
  for line in ('A>X B','A>X<B Reads','A=X>B Read','A> B','A >X>B','X^Q^Y F'):
   with self.subTest(line=line):
    with self.assertRaises(ValueError):native.parse('\t>G 1\nA node\nB node\n'+line+'\n\n\n')
 def test_continuation_boundaries(self):
  for line in (' Task','  APIKey'):
   s='\t>G 1\nA LoginAPI Authentication\n'+line+'\n\n\n'
   self.assertEqual(native.view(s)[0]['nodes'][0]['id'],'A')
  with self.assertRaises(ValueError):native.parse('\t>G 1\n NoRecord\n\n\n')
 def test_three_modes(self):
  s=(ROOT/'examples/complete_v12.nema').read_text()
  self.assertEqual([x['mode'] for x in native.view(s)],['5w1h','table','graph'])
 def test_migration_semantics_and_headers(self):
  inputs=[ROOT/'archive/R7_original/website__demo_data.js']
  import json
  demos=json.loads(inputs[0].read_text().split('=',1)[1].strip().rstrip(';'))
  examples=[x['raw'] for x in demos if x['mode']=='graph']
  examples.append('\t>G 1\n A LoginAPI Authentication APIKey\n B TokenStore\nA>X>B Reads VerifySession HTTP401\n   RetryOnTimeout\n\n\n')
  for src in examples:
   converted=migrate(src)
   self.assertEqual(old.view(src),native.view(converted))
   self.assertEqual(src.split('\n')[0],converted.split('\n')[0])
 def test_codec_lossless(self):
  for name in ['graph_v13_canonical.nema','graph_x3_extensions.nema','graph_3n_4e.nema']:
   s=(ROOT/'examples'/name).read_text()
   self.assertEqual(nemat.decode(nemat.encode(s)),s)
   self.assertEqual(nemat.decode(nemat.encode(s,['LoginAPI','HTTP401'])),s)
 def test_standalone_parity(self):
  for name in ['native.py','nemat.py']:
   self.assertEqual((ROOT/'codec'/name).read_bytes(),(ROOT/'_Interpreter_Standalone/codec'/name).read_bytes())
if __name__=='__main__':unittest.main()
