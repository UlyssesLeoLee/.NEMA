import unittest,sys,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec import native,nemat

def doc(*lines):return '\n'.join(lines)+'\n\n\n'

class NativeSpec(unittest.TestCase):
    def test_fields_order_and_simple_text(self):
        x=native.view(doc('\tT1 1','处理登录流程'))[0]
        self.assertEqual(x['fields']['What'],'处理登录流程')
        self.assertEqual(tuple(x['fields']),('What','Why','How','Who','When','Where'))
        self.assertFalse(any(x['fields'][k] for k in ('Why','How','Who','When','Where')))
    def test_english_http(self):
        x=native.view(doc('\tT1 1','What','HTTPItIs'))[0]
        self.assertEqual(x['fields']['What'],'What HTTP it is')
        self.assertEqual(native.lexical_words('HTTPItIs'),['HTTP','It','Is'])
    def test_apostrophe(self):
        self.assertEqual(native.join_intents(['I',"'m",'What?']),"I'm what?")
    def test_pascal(self):
        self.assertEqual(native.join_intents(['BuildLoginFlow']),'Build login flow')
    def test_zh(self):
        x=native.view(doc('\tT1 1','处理登录流程','并验证授权'))[0]
        self.assertEqual(x['fields']['What'],'处理登录流程并验证授权')
    def test_ja(self):
        x=native.view(doc('\tT1 1','私は','学生です。'))[0]
        self.assertEqual(x['fields']['What'],'私は学生です。')
    def test_space_col(self):
        x=native.view(doc('\tT1 1','BuildLoginFlow PreventDataLeak ValidateAPI Codex Today AuthService'))[0]
        self.assertEqual(x['fields']['Why'],'Prevent data leak')
        self.assertEqual(x['fields']['Who'],'Codex')
    def test_table_mode(self):
        x=native.view(doc('\tTb1 1','\tAgent Status Note','Claude Ready HTTPResponse','  VerifySession','Codex Done AllPassed'))[0]
        self.assertEqual(x['mode'],'table')
        self.assertEqual(x['records'][0]['Note'],'HTTP response verify session')
        self.assertEqual(len(x['records']),2)
    def test_graph_direction_and_description(self):
        x=native.view(doc('\t>G1 1','A LoginAPI 接收请求','B Store 存储令牌','A>X>B Reads 验证会话','  缓存失效时重试','A<Y<B Notifies 异常反馈','A=Z=B Related 互有关联','A>P>A Retry 最多三次'))[0]
        e={i['id']:i for i in x['edges']}
        self.assertEqual((e['X']['source'],e['X']['target']),('A','B'))
        self.assertEqual((e['Y']['source'],e['Y']['target']),('B','A'))
        self.assertEqual(e['Z']['direction'],'=')
        self.assertEqual(e['P']['source'],e['P']['target'])
        self.assertEqual(e['X']['description'],'验证会话缓存失效时重试')
    def test_adjacent_acronyms_not_guessed(self):
        self.assertEqual(native.lexical_words('APIHTTP'),['APIHTTP'])
    def test_why_fourth_and_where_fifth_continuation(self):
        x=native.view(doc('\tT1 1','Build Why How Who When Where','    Tomorrow','     Tokyo'))[0]
        self.assertEqual(x['fields']['When'],'When tomorrow')
        self.assertEqual(x['fields']['Where'],'Where tokyo')
    def test_graph_duplicate_node(self):
        with self.assertRaises(ValueError):native.parse(doc('\t>G1 1','A','A'))
    def test_mixed_direction_rejected(self):
        with self.assertRaises(ValueError):native.parse(doc('\t>G1 1','A','B','A>X<B Reads'))
    def test_dangling_edge_rejected(self):
        with self.assertRaises(ValueError):native.parse(doc('\t>G1 1','A','A>X>B Reads'))
    def test_duplicate_edge(self):
        with self.assertRaises(ValueError):native.parse(doc('\t>G1 1','A','B','A>X>B Reads','A>X>B Write'))
    def test_escaped_literal_space(self):
        x=native.view(doc('\tT1 1','Build\\ LoginFlow'))[0]
        self.assertEqual(x['fields']['What'],'Build login flow')
    def test_exact_literal(self):
        x=native.view(doc('\tT1 1','\\=APIKey'))[0]
        self.assertEqual(x['fields']['What'],'APIKey')
    def test_body_raw_tab_rejected(self):
        with self.assertRaises(ValueError):native.parse(doc('\tT1 1','One\tTwo'))
    def test_domain_lexer(self):
        x=native.parse(doc('\tT1 1','你好','\tT2 1','こんにちは'))
        self.assertEqual(len(x),2)
    def test_termination(self):
        with self.assertRaises(ValueError):native.parse('\tT1 1\nHello\n')
    def test_plain_body_leading_space_valid(self):
        x=native.view(doc('\tT1 1','What Why','','')) if False else native.view(doc('\tT1 1','BuildLoginFlow PreventDataLeak',' ReviewLogs'))
        self.assertEqual(x[0]['fields']['Why'],'Prevent data leak review logs')
    def test_case_nonreversibility_explained(self):
        raw=doc('\tT1 1','BuildLoginFlow')
        self.assertNotIn('BuildLoginFlow',native.view(raw)[0]['fields']['What'])
        self.assertIn('BuildLoginFlow',native.parse(raw)[0]['fields'][0])

class Transport(unittest.TestCase):
    def sample(self):
        return doc('\tTaskLogin001 1','CheckAPIKey PreventLeak ReviewHTTP Claude Now Auth',
                   '\tTaskLogin002 1','CheckAPIKey PreventLeak ReviewHTTP Codex Now Auth',
                   '\tTaskLogin003 1','CheckAPIKey PreventLeak ReviewHTTP Argo Now Auth')
    def test_secret_not_auto_dictionary(self):
        src=doc('\tT1 1','secret=superVerySensitiveSecret123','\tT2 1','secret=superVerySensitiveSecret123')
        self.assertNotIn('secret=superVerySensitiveSecret123',nemat.cell_candidates(src))
        self.assertEqual(nemat.decode(nemat.encode(src,[],True)),src)
    def test_uncompressed_roundtrip(self):
        src=self.sample();self.assertEqual(nemat.decode(nemat.encode(src,[],False)),src)
    def test_dict_roundtrip(self):
        src=self.sample();out=nemat.encode(src,['PreventLeak','ReviewHTTP'],False)
        self.assertTrue(out.startswith('\t$2\n'))
        self.assertIn('^0',out)
        self.assertEqual(nemat.decode(out),src)
    def test_prefix_roundtrip(self):
        src=self.sample();out=nemat.encode(src,[],True)
        self.assertEqual(nemat.decode(out),src)
    def test_caret_literal(self):
        src=doc('\tT1 1','Price^2 Other','\tT2 1','Price^2 Other')
        out=nemat.encode(src,[],False)
        self.assertIn('\\^',out)
        self.assertEqual(nemat.decode(out),src)
    def test_native_literal_caret_alias_collision(self):
        src=doc('\tT1 1','^0 ^9')
        out=nemat.encode(src,['^0'],True)
        self.assertEqual(nemat.decode(out),src)
    def test_table_roundtrip(self):
        src=doc('\tTb1 1','\tAgent Status Note','Claude Ready Excellent','  Amazing','Codex Done Excellent')
        self.assertEqual(nemat.decode(nemat.encode(src,['Excellent'],True)),src)
    def test_graph_roundtrip(self):
        src=doc('\t>G1 1','A API 処理する','B Store 保存する','A>X>B Reads 検証した','  続ける')
        self.assertEqual(nemat.decode(nemat.encode(src,['検証した'],True)),src)
    def test_mode_prefix_field_collision(self):
        src=doc('\tTb1 1','\tAgent Status','1 Okay','2 Okay')
        self.assertEqual(nemat.decode(nemat.encode(src,[],True)),src)
    def test_deterministic(self):
        src=self.sample();self.assertEqual(nemat.optimize(src).text,nemat.optimize(src).text)
    def test_optimizer_safe(self):
        src=self.sample();r=nemat.optimize(src)
        if r.mode!='native':self.assertEqual(nemat.decode(r.text),src)
        self.assertLessEqual(r.score,len(src.encode()))
    def test_fuzz_random(self):
        r=random.Random(42)
        for _ in range(100):
            cells=[''.join(r.choice('ABCabc0123^\\') for _ in range(8)) for _ in range(5)]
            src=doc('\tT1 1',' '.join(native.cell_escape(x) for x in cells))
            self.assertEqual(nemat.decode(nemat.encode(src,[],True)),src)
    def test_reject_missing_terminator(self):
        with self.assertRaises(ValueError):nemat.decode('\t$0\n\tT1 1\nA')
    def test_dict_manifest_tamper(self):
        with self.assertRaises(ValueError):nemat.decode(doc('\t$2','OnlyOne','\tT1 1','Hi'))
    def test_dict_bad_index(self):
        with self.assertRaises(ValueError):nemat.decode(doc('\t$1','Foo','\tT1 1','^9'))
    def test_header_no_whitespace_ambiguity(self):
        with self.assertRaises(ValueError):native.parse(doc(' T1 1','Hi'))
    def test_manual_string_same_literal(self):
        s=doc('\tT1 1',native.cell_escape('hello world'))
        self.assertEqual(native.parse(s)[0]['fields'][0][0],'hello world')
    def test_prefix_is_tab_digit(self):
        out=nemat.encode(self.sample(),[],True)
        self.assertTrue(any(x.startswith('\t') and x[1:].split()[0].isdigit() for x in out.splitlines()))

if __name__=='__main__':unittest.main()
