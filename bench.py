"""Reproducible same-data serializer benchmark. Python 3.11+, PyYAML optional."""
from __future__ import annotations
import argparse, gzip, json, random, statistics, time
from pathlib import Path
import yaml
from i_codec import Document, write, parse

SEED=20261106

def make_doc(size=1000, variant='agent'):
    rng=random.Random(SEED)
    d=Document()
    d.schemas={
      'T':[('owner','s'),('state','s'),('priority','n'),('target','s'),('summary','s')],
      'I':[('method','s'),('path','s'),('request','s'),('response','s'),('auth','b')],
      'F':[('path','s'),('language','s'),('owner','s'),('hash','s')],
      'M':[('source','s'),('confidence','n'),('fact','s'),('verified','b')],
    }
    counts={'T':max(1,size*5//10),'I':max(1,size*2//10),'F':max(1,size*2//10),'M':max(1,size-size*9//10)}
    ids={g:[] for g in d.schemas}
    options=['argo','codex','claude','hermes','gemini','orchestrator']
    statuses=['ready','open','done','blocked']
    verbs=['validate','create','update','publish','lock','review','rebase']
    def unique_value(j):
        return ''.join(rng.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(40)) + f'{j}'
    for g,count in counts.items():
        for j in range(count):
            local={'T':'task.','I':'api.','F':'file.','M':'note.'}[g]+f'{j:05d}'
            ids[g].append(g+'/'+local)
            if variant=='random':
                v=unique_value(j + (ord(g)*1000))
                if g=='T': values=dict(owner=v,state=unique_value(j+99),priority=j,target=unique_value(j+199),summary=unique_value(j+299))
                if g=='I': values=dict(method=v,path=unique_value(j+400),request=unique_value(j+500),response=unique_value(j+600),auth=j%2==0)
                if g=='F': values=dict(path=v,language=unique_value(j+700),owner=unique_value(j+800),hash=unique_value(j+900))
                if g=='M': values=dict(source=v,confidence=j,fact=unique_value(j+1000),verified=j%2==0)
            elif variant=='mixed':
                v=f'Shared context for group {g} step {j}: '+unique_value(j)
                if g=='T': values=dict(owner=options[j%6],state=statuses[j%4],priority=j%4,target='I/api.%05d'%(j%counts['I']),summary=v+'\nrequires rollback | audit \\ escape')
                if g=='I': values=dict(method='POST' if j%2 else 'GET',path=f'/v1/complex/path/{j}/',request=v,response='JSON response with '+unique_value(j+100),auth=j%2==0)
                if g=='F': values=dict(path=f'src/services/{j}/impl.rs',language='rust',owner=options[j%6],hash=unique_value(j))
                if g=='M': values=dict(source=f'repo://doc/{j}',confidence=j%101,fact=v,verified=j%2==0)
            else:
                if g=='T': values=dict(owner=options[j%6],state=statuses[j%4],priority=j%4,target='I/api.%05d'%(j%counts['I']),summary=verbs[j%7]+' authorization interface')
                if g=='I': values=dict(method='POST' if j%2 else 'GET',path=f'/v1/resource/{j%32}',request='application/json',response='application/json',auth=j%2==0)
                if g=='F': values=dict(path=f'src/components/module_{j:04d}.rs',language='rust',owner=options[j%6],hash='sha256:'+ ('aabbccdd' if j%2 else '11223344'))
                if g=='M': values=dict(source=f'repo://docs/module_{j%20}',confidence=90+(j%10),fact=verbs[j%7]+' must pass tests',verified=j%2==0)
            d.add(g,local,values,rev=1+j%5)
    for j in range(counts['T']):
        t=ids['T'][j]; i=ids['I'][j%counts['I']]; f=ids['F'][j%counts['F']]
        d.link(t,i,'uses');d.link(t,f,'touches')
    return d

def md_escape(value):
    if isinstance(value,bool): return 'true' if value else 'false'
    return str(value).replace('\\','\\\\').replace('|','\\|').replace('\n','\\n').replace('\r','\\r')

def as_md(doc):
    rows=['# Structured agent data']
    for group,schema in sorted(doc.schemas.items()):
        rows += ['',f'## Group {group}']
        head=['id','rev']+[f'{key}:{kind}' for key,kind in schema]
        rows+=['|'+'|'.join(head)+'|','|'+'|'.join('---' for _ in head)+'|']
        for n in sorted(doc.nodes.values(), key=lambda n:n.ref):
            if n.group==group:
                rows+=['|'+'|'.join(map(md_escape,[n.local_id,n.rev]+[n.values[k] for k,_ in schema]))+'|']
    rows+=['','## Edges','|source|target|relation|','|---|---|---|']
    for edge in sorted(doc.edges):rows+=['|'+'|'.join(edge)+'|']
    return '\n'.join(rows)+'\n'

def timed(fn, reps=20):
    vals=[]
    for _ in range(reps):
        st=time.perf_counter_ns();fn(); vals.append((time.perf_counter_ns()-st)/1e6)
    return round(statistics.median(vals),3)

def compare(n, variant):
    d=make_doc(n,variant)
    obj=d.canonical_obj()
    encoded={
        'JSON-min':json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',
        'JSON-pretty':json.dumps(obj,ensure_ascii=False,indent=2)+'\n',
        'YAML':yaml.safe_dump(obj,allow_unicode=True,sort_keys=False),
        'Markdown':as_md(d),
    }
    for r in range(4):encoded[f'i-r{r}']=write(d,r)
    assert parse(encoded['i-r3']).canonical_obj()==obj
    assert json.loads(encoded['JSON-min'])==obj
    assert yaml.safe_load(encoded['YAML'])==obj
    result=[]
    for name,s in encoded.items():
        data=s.encode('utf-8'); gz=gzip.compress(data,compresslevel=9,mtime=0)
        parser={'JSON-min':lambda:json.loads(s),'JSON-pretty':lambda:json.loads(s),
                'YAML':lambda:yaml.safe_load(s),'i-r3':lambda:parse(s,strict=False)}.get(name)
        ms=timed(parser,reps=9) if parser is not None else None
        result.append(dict(format=name,raw_bytes=len(data),gzip_bytes=len(gz),parse_ms_median=ms))
    return result,encoded

def run(output):
    cases=[('tiny',3,'agent'),('agent_1000',1000,'agent'),('mixed_300',300,'mixed'),('random_300',300,'random')]
    results={}
    for name,n,v in cases:
        rows,enc=compare(n,v)
        results[name]=rows
        print('\n',name,'nodes=',len(make_doc(n,v).nodes))
        for row in rows: print(f"{row['format']:12} raw={row['raw_bytes']:>8} gzip={row['gzip_bytes']:>7} parse_ms={row['parse_ms_median']}")
    Path(output).write_text(json.dumps(dict(seed=SEED,environment='CPython, median 9 parses, single process; warm cache',cases=results),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='benchmark.json')
    args=parser.parse_args();run(args.output)
