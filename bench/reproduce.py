"""Reproducible synthetic NEMA v1.4 benchmark using included local SentencePiece models.
The synthetic scenarios intentionally include repeat-heavy and high-entropy data.
Not a commercial-model tokenizer or a real LLM generation reliability experiment.
"""
from __future__ import annotations
import csv,json,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import sentencepiece as spm
from codec import render
from codec.transport import encode,decode
EX=ROOT/'examples'
FIXTURES=['bench_en_60.nema','bench_zh_60.nema','bench_ja_60.nema', 'bench_table_300.nema','bench_graph_120_600.nema','bench_high_entropy_120.nema','01_explicit_table_header.nema','00_default_table_no_header.nema']
MODELS={'BPE':ROOT/'bench/models/neutral_bpe.model','Unigram':ROOT/'bench/models/neutral_unigram.model'}

def yaml_string(s): return json.dumps(s,ensure_ascii=False,separators=(',',':'))

def position_yaml(source):
    v=render(source)
    rows=['domains:']
    if v['dictionary']:
        rows.append('dictionary: '+json.dumps(v['dictionary'],ensure_ascii=False,separators=(',',':')))
    for d in v['domains']:
        rows.append(f'  - id: {d["id"]}')
        rows.append('    revision: '+str(d['revision']))
        rows.append('    mode: '+d['mode'])
        if d['explicit_header'] or d['mode']!='table':
            rows.append('    columns: '+json.dumps(d['columns'],ensure_ascii=False,separators=(',',':')))
        rows.append('    rows:')
        for record in d['rows']:
            # Preserve semantic vertical groups; raw source code not transformed.
            groups=record['groups']
            cols=[a[0] if len(a)==1 else a for a in groups]
            rows.append('      - '+json.dumps(cols,ensure_ascii=False,separators=(',',':')))
    return '\n'.join(rows)+'\n'

def main():
    sp={k:spm.SentencePieceProcessor(model_file=str(path)) for k,path in MODELS.items()}
    results=[]
    for fixture in FIXTURES:
        src=(EX/fixture).read_text(encoding='utf-8')
        yml=position_yaml(src)
        for model,tokenizer in sp.items():
            score=lambda x:len(tokenizer.encode(x))
            result=encode(src,score)
            if result.format=='nemat':assert decode(result.text)==src
            e={'fixture':fixture,'model':model,'native_tokens':score(src),'optimized_tokens':score(result.text),
               'yaml_tokens':score(yml),'native_bytes':len(src.encode()),'optimized_bytes':len(result.text.encode()),
               'method':result.method,'saving_pct':result.saving_percent,
               'versus_yaml_pct':round(100*(1-score(result.text)/score(yml)),2) if score(yml) else 0,
               'transport_format':result.format}
            results.append(e)
            # One canonical encoded sample per BPE scenario for website side-by-side exact source.
            if model=='BPE':
                dest=ROOT/'bench'/'outputs';dest.mkdir(exist_ok=True)
                (dest/(fixture.replace('.nema','')+'.'+result.format)).write_text(result.text,encoding='utf-8')
                (dest/(fixture.replace('.nema','')+'.yaml')).write_text(yml,encoding='utf-8')
            print(f'{fixture:<30} {model:<8} {e["native_tokens"]:>7} -> {e["optimized_tokens"]:>7} ({e["saving_pct"]:+.2f}%), YAML={e["yaml_tokens"]}, {result.method}',flush=True)
    (ROOT/'bench'/'results.json').write_text(json.dumps({'source':'local SentencePiece','reproducible':True,'fixtures':FIXTURES,'results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'bench'/'results.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=results[0].keys());w.writeheader();w.writerows(results)
    (ROOT/'website'/'benchmark_data.js').write_text('window.NEMA_BENCHMARK='+json.dumps(results,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('Wrote results.json, results.csv, website benchmark_data.js')
if __name__=='__main__':main()
