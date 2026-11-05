import gzip, json, time, statistics, platform
from pathlib import Path
import yaml
from bench import make_doc,as_md
from i_codec import write as write_i,parse as parse_i
from nema_codec import write as write_n1,parse as parse_n1
from nema2_codec import write as write_n2,parse as parse_n2

def bench(n, variant):
    d=make_doc(n,variant);obj=d.canonical_obj()
    content={
        'JSON-min':json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',
        'YAML':yaml.safe_dump(obj,allow_unicode=True,sort_keys=False),
        'Markdown':as_md(d),
        'i-r3':write_i(d,3),
        'NEMA1':write_n1(d),
        'NEMA2-r0':write_n2(d,dictionary=False,prefixes=False),
        'NEMA2-r1':write_n2(d,dictionary=True,prefixes=False),
        'NEMA2-r2':write_n2(d,dictionary=False,prefixes=True),
        'NEMA2-r3':write_n2(d,dictionary=True,prefixes=True),
    }
    assert parse_n2(content['NEMA2-r3']).canonical_obj()==obj
    assert parse_n1(content['NEMA1']).canonical_obj()==obj
    timings={
        'JSON-min':lambda:json.loads(content['JSON-min']),
        'YAML':lambda:yaml.safe_load(content['YAML']),
        'i-r3':lambda:parse_i(content['i-r3'],strict=False),
        'NEMA1':lambda:parse_n1(content['NEMA1']),
        'NEMA2-r3':lambda:parse_n2(content['NEMA2-r3']),
    }
    rows=[]
    for name,s in content.items():
        raw=s.encode('utf-8')
        fn=timings.get(name);times=[]
        if fn:
            for i in range(9):
                t=time.perf_counter_ns();fn();times.append((time.perf_counter_ns()-t)/1e6)
        rows.append({'format':name,'bytes':len(raw),'gzip_bytes':len(gzip.compress(raw,compresslevel=9,mtime=0)),
            'parse_ms_median':round(statistics.median(times),3) if times else None})
    return {'n':n,'variant':variant,'metrics':rows}
if __name__=='__main__':
    output={'python':platform.python_version(),'method':'median 9 warm runs, CPython; same canonical doc; UTF-8 bytes and gzip9; no tokenizer',
            'cases':[bench(3,'agent'),bench(300,'mixed'),bench(300,'random'),bench(1000,'agent')]}
    Path('benchmark_v2.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for case in output['cases']:
        print('\n',case['n'],case['variant'])
        for r in case['metrics']:
            print(f"{r['format']:12s} {r['bytes']:8}B gzip:{r['gzip_bytes']:7} parse:{r['parse_ms_median']}")
