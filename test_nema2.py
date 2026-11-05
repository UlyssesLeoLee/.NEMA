from __future__ import annotations
import sys,unittest,tempfile,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from i_codec import Document,IFormatError,Conflict
from i_store import DomainStore
from bench import make_doc
from nema2_codec import parse,write
from nema2_patch import schema_hash,parse_patch,apply_patch

class Nema2Tests(unittest.TestCase):
    def sample(self):return parse(Path(__file__).with_name('sample.nema').read_text(encoding='utf-8'))
    def test_one_block_one_domain(self):
        d=self.sample();self.assertEqual(len(d.nodes),4)
        self.assertEqual(d.nodes['T/a7'].values['how'],'60/min/ip')
        self.assertIn(('T/a7','F/auth','touches'),d.edges)
        self.assertEqual(d.checks['T/a7'],['cargo test'])
    def test_roundtrip_canonical(self):
        d=self.sample();self.assertEqual(parse(write(d)).canonical_obj(),d.canonical_obj())
        self.assertEqual(parse(write(d)).checks,d.checks)
    def test_3_rounds_lossless(self):
        for variant in ('agent','mixed','random'):
            d=make_doc(100,variant)
            for kw in ({'dictionary':False,'prefixes':False},{'dictionary':True,'prefixes':False},{'dictionary':True,'prefixes':True}):
                self.assertEqual(parse(write(d,**kw)).canonical_obj(),d.canonical_obj())
    def test_leading_space_and_trailing_space(self):
        d=make_doc(3);n=next(iter(d.nodes.values()));k=next(k for k,v in n.values.items() if isinstance(v,str))
        n.values[k]=' start with space ';self.assertEqual(parse(write(d)).nodes[n.ref].values[k], ' start with space ')
    def test_empty_terminal_field(self):
        d=Document();d.schemas={'T':[('a','s'),('b','s')]};d.add('T','a',{'a':'x','b':''})
        self.assertEqual(parse(write(d)).nodes['T/a'].values['b'],'')
    def test_all_escapes(self):
        d=Document();d.schemas={'T':[('a','s')]};d.add('T','a',{'a':'^a\tword\n\\xx\r\u2028'})
        self.assertEqual(parse(write(d)).nodes['T/a'].values['a'],'^a\tword\n\\xx\r\u2028')
    def test_unicode_separator_not_newline(self):
        d=Document();d.schemas={'T':[('a','s')]};d.add('T','a',{'a':'a\u0085\u2028z'})
        self.assertEqual(parse(write(d)).nodes['T/a'].values['a'],'a\u0085\u2028z')
    def test_unknown_indent_rejected(self):
        s=Path(__file__).with_name('sample.nema').read_text().replace('     cargo test','       cargo test')
        with self.assertRaises(IFormatError):parse(s)
    def test_tab_to_spaces_breaks_schema(self):
        s=Path(__file__).with_name('sample.nema').read_text().replace('\t','  ')
        with self.assertRaises(IFormatError):parse(s)
    def test_bad_ref_rejected(self):
        s=Path(__file__).with_name('sample.nema').read_text().replace('F/auth\n','F/unknown\n',1)
        with self.assertRaises(IFormatError):parse(s)
    def test_dup_domain_rejected(self):
        s=Path(__file__).with_name('sample.nema').read_text()+ 'T/a7 1\n x\ty\tz\ti\ta\tb\n'
        with self.assertRaises(IFormatError):parse(s)
    def test_patch_update_by_column(self):
        d=self.sample();s='p2 '+schema_hash(d.schemas)+'\nT/a7 1\n 5\t120/min/ip\n'
        patched=apply_patch(d,s)
        self.assertEqual(patched.nodes['T/a7'].values['how'],'120/min/ip')
        self.assertEqual(d.nodes['T/a7'].values['how'],'60/min/ip')
        with self.assertRaises(Conflict):apply_patch(patched,s)
    def test_schema_reorder_attack_rejected(self):
        d=self.sample();s='p2 '+schema_hash(d.schemas)+'\nT/a7 1\n 5\t120/min/ip\n'
        d.schemas['T'][0],d.schemas['T'][5]=d.schemas['T'][5],d.schemas['T'][0]
        with self.assertRaises(IFormatError):parse_patch(d,s)
    def test_patch_atomicity_invalid_ref(self):
        d=self.sample();s='p2 '+schema_hash(d.schemas)+'\nT/a7 1\n 5\t120/min/ip\nT/unknown 1\n 5\tevil\n'
        with self.assertRaises(IFormatError):apply_patch(d,s)
        self.assertEqual(d.nodes['T/a7'].rev,1)
    def test_duplicate_patch_slot_rejected(self):
        d=self.sample();s='p2 '+schema_hash(d.schemas)+'\nT/a7 1\n 5\ta\n 5\tb\n'
        with self.assertRaises(IFormatError):parse_patch(d,s)
    def test_parallel_domains_and_conflict(self):
        d=make_doc(60)
        with tempfile.TemporaryDirectory() as tmp:
            store=DomainStore(Path(tmp)/'db.sqlite');store.load_initial(d)
            refs=list(d.nodes)[:30]
            def update(ref):
                n=store.read(ref);k=next(k for k,v in n.values.items() if type(v)==str)
                store.edit_many([(ref,n.rev,{k:'updated'})],'agent')
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:list(pool.map(update,refs))
            self.assertEqual(sum(store.read(r).rev==d.nodes[r].rev+1 for r in refs),30)
            r=refs[0];version=store.read(r).rev;k=next(k for k,v in store.read(r).values.items() if type(v)==str)
            def collide(i):
                try:store.edit_many([(r,version,{k:str(i)})],f'agent{i}');return 1
                except Conflict:return 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:results=list(pool.map(collide,range(10)))
            self.assertEqual(sum(results),1)
    def test_invalid_alias_rejected(self):
        d=Document();d.schemas={'T':[('x','s')]};d.add('T','a',{'x':'^q'})
        s=write(d,dictionary=False,prefixes=False).replace('\\^q','^q')
        with self.assertRaises(IFormatError):parse(s)

if __name__=='__main__':unittest.main(verbosity=2)

class SchedulerTests(unittest.TestCase):
    def test_parallel_non_overlapping_domains(self):
        from nema2_scheduler import ready_batch
        doc=Document();doc.schemas={'T':[('who','s')]}
        for x in ('a','b','resource1','resource2'):doc.add('T',x,{'who':'agent'})
        doc.link('T/a','T/resource1','touches')
        doc.link('T/b','T/resource2','touches')
        self.assertEqual(ready_batch(doc,['T/a','T/b']),['T/a','T/b'])
    def test_write_write_collision_with_read_write(self):
        from nema2_scheduler import ready_batch
        doc=Document();doc.schemas={'T':[('who','s')]}
        for x in ('a','b','resource'):doc.add('T',x,{'who':'agent'})
        doc.link('T/a','T/resource','touches')
        doc.link('T/b','T/resource','touches')
        self.assertEqual(ready_batch(doc,['T/a','T/b']),['T/a'])
        doc.edges.remove(('T/b','T/resource','touches'))
        doc.link('T/b','T/resource','uses')
        self.assertEqual(ready_batch(doc,['T/a','T/b']),['T/a'])
    def test_dependencies_block_until_completed(self):
        from nema2_scheduler import ready_batch
        doc=Document();doc.schemas={'T':[('who','s')]}
        for x in ('a','b'):doc.add('T',x,{'who':'agent'})
        doc.link('T/b','T/a','depends')
        self.assertEqual(ready_batch(doc,['T/a','T/b']),['T/a'])
        self.assertEqual(ready_batch(doc,['T/b'],completed={'T/a'}),['T/b'])

class AutoEncodingTests(unittest.TestCase):
    def test_byte_optimal(self):
        from nema2_codec import write_auto
        d=make_doc(100,'mixed')
        out=write_auto(d,objective='bytes')
        self.assertEqual(len(out.encode()),min(len(write(d,dictionary=di,prefixes=pr).encode()) for di in (False,True) for pr in (False,True)))
        self.assertEqual(parse(out).canonical_obj(),d.canonical_obj())
    def test_gzip_optimal(self):
        from nema2_codec import write_auto
        import gzip
        d=make_doc(100,'agent')
        out=write_auto(d,objective='gzip')
        size=lambda s:len(gzip.compress(s.encode(),9,mtime=0))
        self.assertEqual(size(out),min(size(write(d,dictionary=di,prefixes=pr)) for di in (False,True) for pr in (False,True)))
    def test_token_mode_explicitly_requires_tokenizer(self):
        from nema2_codec import write_auto
        with self.assertRaises(ValueError):write_auto(make_doc(3),objective='tokens')
