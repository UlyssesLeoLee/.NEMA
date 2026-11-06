import unittest,random,string,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from codec import encode,decode,parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def doc(s):return s+'\n\n\n'
class TransportTests(unittest.TestCase):
 def test_all_fixtures_roundtrip(self):
  for f in sorted((ROOT/'examples').glob('*.nema')):
   with self.subTest(fixture=f.name):
    s=f.read_text(encoding='utf-8'); ch=encode(s);self.assertEqual(decode(ch.text) if ch.format=='nemat' else ch.text,s)
 def test_lossless_dict_preserved(self):
  s=doc('\t$1\nAPIKey\n\t?Task001 1\nValidate^0BeforeAccess\n\t?Task002 1\nValidate^0BeforeAccess')
  x=encode(s);self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
 def test_prefix_applies(self):
  s=doc('\n'.join(f'\tLongRepeatedDomain{i:03d} 1\nSameValue RepeatedValue' for i in range(30)))
  x=encode(s);self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
 def test_rle_cjk(self):
  s=doc('\tT1 1\n'+'哈'*200+' AAAAAAAA')
  x=encode(s);self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
 def test_literal_caret_and_slash(self):
  # Intrinsic native ^7 without a dictionary is not renderable; use escaped only.
  s=doc('\tT1 1\n\\^ \\^7 \\8A \\\\ \\.')
  x=encode(s);self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
 def test_sensitive_high_entropy_fallback(self):
  s=(ROOT/'examples/bench_high_entropy_120.nema').read_text(encoding='utf-8')
  x=encode(s);self.assertEqual(x.format,'nema')
 def test_bad_transport_header(self):
  with self.assertRaises(ValueError):decode(doc('\tT1 1\nA B'))
 def test_bad_reference(self):
  with self.assertRaises(ValueError):decode(doc('\t$1\nValue\n\tT1 1\n^9'))
 def test_bad_rle(self):
  with self.assertRaises(ValueError):decode(doc('\t$0\n\tT1 1\n\\9999999A'))
 def test_bad_prefix_selector(self):
  with self.assertRaises(ValueError):decode(doc('\t$0\n\t0\n\tT1 1\nA'))
 def test_byte_exact_whitespace(self):
  s=doc('\tT1 1\n\\ Agent State Note\nA Ready Hello\n   ManyFragments\nB Blocked InvalidToken')
  x=encode(s);self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
 def test_randomized_roundtrips(self):
  r=random.Random(123)
  for n in range(50):
   lines=['\tT1 1']
   for _ in range(r.randint(1,12)):
    v=''.join(r.choice(string.ascii_letters+string.digits+'^\\.') for _ in range(r.randint(4,30)))
    v=v.replace('\\','\\\\').replace('^','\\^')
    lines.append(v+' Foo')
   s=doc('\n'.join(lines));x=encode(s)
   with self.subTest(n=n):self.assertEqual(decode(x.text) if x.format=='nemat' else x.text,s)
if __name__=='__main__':unittest.main()
