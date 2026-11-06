from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from codec import render
examples={'table_no_header':'00_default_table_no_header.nema','table_with_header':'01_explicit_table_header.nema','what_first':'02_5w1h_what_first.nema','graph':'03_graph_complex.nema','dictionary':'04_inline_shared_dictionary.nema','languages':'05_mixed_languages.nema'}
data={}
for k,f in examples.items():
 src=(root/'examples'/f).read_text(encoding='utf-8')
 data[k]={'name':f,'source':src,'rendered':render(src)}
(root/'website'/'demo_data.js').write_text('window.NEMA_DEMOS='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
results=[]
for f in ['bench_en_60.nema','bench_zh_60.nema','bench_ja_60.nema','bench_table_300.nema','bench_graph_120_600.nema','bench_high_entropy_120.nema']:
 src=(root/'examples'/f).read_text(encoding='utf-8')
 candidates=list((root/'bench/outputs').glob(f.replace('.nema','')+'.*'))
 arr=[p for p in candidates if p.suffix in ('.nemat','.nema')]
 out=arr[0].read_text(encoding='utf-8') if arr else src
 results.append({'name':f,'native':src[:1500],'optimized':out[:1500],'truncated':len(src)>1500 or len(out)>1500})
(root/'website'/'benchmark_samples.js').write_text('window.NEMA_BENCHMARK_SAMPLES='+json.dumps(results,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('wrote website demo and benchmark samples')
