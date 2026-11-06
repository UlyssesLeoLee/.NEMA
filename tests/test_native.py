import unittest,random,string,pathlib,sys,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from codec.core import parse,render,validate_source,render_text,join_cell
ROOT=pathlib.Path(__file__).resolve().parents[1]
def doc(s):return s+'\n\n\n'
class NativeTests(unittest.TestCase):
 def test_all_fixtures(self):
  for f in sorted((ROOT/'examples').glob('*.nema')):
   with self.subTest(fixture=f.name):
    d=parse(f.read_text(encoding='utf-8'));self.assertTrue(d.domains)
 def test_numeric_headers_and_default_revision(self):
  for head,mode,rev in [('\t\\1','table',1),('\t?2','5w1h',1),('\t>3','graph',1),('\t\\4 7','table',7)]:
   with self.subTest(head=head):
    body='A Node' if mode=='graph' else 'Hello'
    d=parse(doc(head+'\n'+body)).domains[0]
    self.assertEqual((d.mode,d.revision),(mode,rev))
 def test_header_vs_continuation(self):
  d=render(doc('\t\\1\nA B\n  Continued\n\t\\2\nC D'))['domains']
  self.assertEqual(len(d),2)
  self.assertEqual(d[0]['rows'][0]['cells'][1],'B Continued')
 def test_reject_missing_graph_node(self):
  with self.assertRaisesRegex(ValueError,'undefined graph node'):
   parse(doc('\t>1\nA Node\nA>X>B Reads'))
 def test_reject_duplicate_graph_edge(self):
  with self.assertRaisesRegex(ValueError,'duplicate edge ID'):
   parse(doc('\t>1\nA Node\nB Node\nA>X>B Reads\nB<X<A Writes'))
 def test_headerless_table(self):
  d=render(doc('\t\\1\nClaude Ready HTTPItIs'))['domains'][0]
  self.assertFalse(d['explicit_header']);self.assertEqual(d['columns'],['column1','column2','column3']);self.assertEqual(len(d['rows']),1)
  self.assertEqual(d['rows'][0]['cells'][2],'HTTP It Is')
 def test_explicit_header(self):
  d=render(doc('\t\\1\n\\ Agent Status Note\nClaude Ready CheckSession'))['domains'][0]
  self.assertTrue(d['explicit_header']);self.assertEqual(d['columns'],['Agent','Status','Note']);self.assertEqual(len(d['rows']),1)
 def test_expand_column(self):
  d=render(doc('\t\\1\nA B\nC D E\n    Fourth'))['domains'][0]
  self.assertEqual(d['columns'],['column1','column2','column3','column4']);self.assertEqual(d['rows'][-1]['cells'][3],'Fourth')
 def test_backslash_caret_first_data_is_not_header(self):
  d=render(doc('\t\\1\n\\^0 A'))['domains'][0]
  self.assertFalse(d['explicit_header']);self.assertEqual(d['rows'][0]['cells'][0],'^0')
 def test_5w1h_order(self):
  d=render(doc('\t?1\nBuildProject MaintainQuality Rust .'))['domains'][0]
  self.assertEqual(d['columns'],['What','Why','How','Who','When','Where']);self.assertTrue(d['rows'][0]['tail_empty'])
  self.assertEqual(d['rows'][0]['cells'][3:6],['','',''])
 def test_only_what(self):
  d=render(doc('\t?1\n修复登录系统'))['domains'][0]
  self.assertEqual(d['rows'][0]['cells'][0],'修复登录系统');self.assertEqual(d['rows'][0]['cells'][1],'')
 def test_en_dictionary_atom(self):
  src=doc('\t$1\nAPIKey\n\t?1\nValidate^0BeforeAccess')
  self.assertEqual(render(src)['domains'][0]['rows'][0]['cells'][0],'Validate APIKey Before Access')
 def test_chinese_dictionary_atom(self):
  src=doc('\t$1\nAPIKey\n\t?1\n请检查^0是否有效')
  self.assertEqual(render(src)['domains'][0]['rows'][0]['cells'][0],'请检查APIKey是否有效')
 def test_japanese_join(self):
  src=doc('\t?1\n私は\n 学生\n です。')
  d=render(src)['domains'][0]
  self.assertEqual(d['rows'][0]['cells'][0],'私は学生です。')
 def test_english_acronym(self):
  self.assertEqual(render_text('HTTPItIs',[]),'HTTP It Is')
 def test_literal_caret(self):
  self.assertEqual(render_text('\\^0',[]),'^0')
 def test_literal_dot(self):
  d=render(doc('\t\\1\nA \\.'))['domains'][0]
  self.assertEqual(d['rows'][0]['cells'][1],'.');self.assertFalse(d['rows'][0]['tail_empty'])
 def test_graph_forward(self):
  d=render(doc('\t>1\nA Node\nB Node\nA>X>B Reads'))['domains'][0]
  self.assertEqual(d['rows'][2]['edge']['from'],'A');self.assertEqual(d['rows'][2]['edge']['to'],'B')
 def test_graph_reverse(self):
  d=render(doc('\t>1\nA Node\nB Node\nA<X<B Reads'))['domains'][0]
  self.assertEqual(d['rows'][2]['edge']['from'],'B');self.assertEqual(d['rows'][2]['edge']['to'],'A')
 def test_graph_undirected(self):
  d=render(doc('\t>1\nA Node\nB Node\nA=X=B Shares'))['domains'][0]
  self.assertEqual(d['rows'][2]['edge']['direction'],'undirected')
 def test_graph_self_loop(self):
  d=render(doc('\t>1\nA Node\nA>Retry>A Retry'))['domains'][0]
  self.assertEqual(d['rows'][1]['edge']['to'],'A')
 def test_graph_vertical_edge(self):
  d=render(doc('\t>1\nA Node\nB Node\nA>X>B Reads CheckSession\n   RetryOnce'))['domains'][0]
  self.assertEqual(d['rows'][-1]['cells'][2],'Check Session Retry Once')
 def test_invalid_graph_edge(self):
  with self.assertRaises(ValueError):parse(doc('\t>1\nA>X<B Reads'))
 def test_bad_header_mode(self):
  with self.assertRaises(ValueError):parse(doc('\t#T1 1\nA B'))
 def test_no_tab_body(self):
  with self.assertRaises(ValueError):parse(doc('\t\\1\nA\tB'))
 def test_no_internal_blanks(self):
  with self.assertRaises(ValueError):parse(doc('\t\\1\nA\n\nB'))
 def test_trailing_newlines(self):
  with self.assertRaises(ValueError):parse('\t\\1\nA\n')
 def test_duplicate_domain_ids(self):
  with self.assertRaises(ValueError):parse(doc('\t\\1\nA\n\t\\1 2\nB'))
 def test_missing_dictionary_reference(self):
  with self.assertRaises(ValueError):render(doc('\t\\1\nA ^9'))
 def test_no_header_after_table_data(self):
  d=render(doc('\t\\1\nA B\n\\ Header Maybe'))['domains'][0]
  self.assertFalse(d['explicit_header']);self.assertEqual(len(d['rows']),2)
 def test_multiple_space_horizontal_rejected(self):
  with self.assertRaises(ValueError):parse(doc('\t\\1\nA  B'))
 def test_continuation_before_row_rejected(self):
  with self.assertRaises(ValueError):parse(doc('\t\\1\n A'))
 def test_many_continuations(self):
  rows=['\t\\1','A B C'] + ['   Word'+str(i) for i in range(20)]
  d=render(doc('\n'.join(rows)))['domains'][0];self.assertEqual(len(d['rows']),1);self.assertEqual(len(d['rows'][0]['groups'][2]),21)
if __name__=='__main__':unittest.main()
