"""One-file conservative native header migration. Do NOT use as a blind repository refactor.
Usage: python scripts/migrate_v14_to_v15.py legacy.nema new.nema
Produces new.nema and new.nema.id-map.json. Never overwrites input.
"""
import argparse,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from codec.core import parse
OLD=re.compile(r'^\t([?>]?)([A-Za-z][A-Za-z0-9_.-]*) ([1-9][0-9]*)$',re.M)
def migrate(source):
    seen={}
    def change(m):
        key=m.group(2)
        if key not in seen: seen[key]=str(len(seen)+1)
        prefix={'':'\\','?':'?','>':'>'}[m.group(1)]
        rev=m.group(3)
        return '\t'+prefix+seen[key]+(' '+rev if rev!='1' else '')
    new=OLD.sub(change,source)
    parse(new)
    if not seen:raise ValueError('no legacy headers found; refusing to write')
    return new,seen
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('old');a.add_argument('new');v=a.parse_args()
    old=pathlib.Path(v.old);dest=pathlib.Path(v.new)
    if old.resolve()==dest.resolve() or dest.exists():raise SystemExit('output must be a new path; no overwrite')
    data,mapping=migrate(old.read_text(encoding='utf-8'))
    dest.write_text(data,encoding='utf-8')
    dest.with_name(dest.name+'.id-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Migrated {len(mapping)} domains to {dest}; verify external references using id-map.json')
