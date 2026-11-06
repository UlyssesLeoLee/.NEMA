from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from codec import parse,decode

def main():
    items=[]
    for file in sorted((ROOT/'training').glob('*.jsonl')):
        n=0
        for line in file.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);m=r['messages']
            assert len(m)==3 and [x['role'] for x in m]==['system','user','assistant'],(file,n)
            content=m[-1]['content'];mode=r.get('format','nema')
            if mode=='nemat': content=decode(content)
            parse(content)
            n+=1
        items.append((file.name,n));print(file.name,n,'validated')
    assert sum(n for _,n in items)>300
    train=(ROOT/'training/nema_v1.4_train.jsonl').read_text(encoding='utf-8')
    hold=(ROOT/'training/nema_v1.4_holdout.jsonl').read_text(encoding='utf-8')
    t={json.loads(s)['messages'][2]['content'] for s in train.splitlines()}
    h={json.loads(s)['messages'][2]['content'] for s in hold.splitlines()}
    assert t.isdisjoint(h),'training/evaluation corpus overlap'
    print('disjoint holdout: yes; all corpus parseable')
if __name__=='__main__':main()
