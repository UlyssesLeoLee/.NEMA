"""Reproducible semantics-matched comparison of review candidate .NEMA / JSON / YAML.
Neutral local SentencePiece BPE; NOT GPT/Claude/Gemini billable tokens.
"""
import sys,json,csv
from pathlib import Path
import yaml
import sentencepiece as spm
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'interpreter'))
from nema_strict import parse
sp=spm.SentencePieceProcessor(model_file=str(R/'bench/neutral_bpe.model'))
S={
 'table_with_null':' \\1 1\n\\# Name Status Detail\nClaude Ready Verified\n~ Running Build\nCodex \\e \\_',
 'five_w_one_h':' \\?2 1\nBuildLogin PreventLeak VerifyToken AuthAgent OnRequest API\n  RetryOnTimeout\nFixLogout \\_ RunTests Reviewer AfterApproval Service',
 'node_edge':' \\>3 1\nA LoginAPI Authentication\nB TokenStore SessionStorage\nC AuditLog Security\nA>X>B Reads VerifySession\n CacheExpiredRetryOnce\nA>Y>C Writes Audit\nB<Z<C Returns Result'
}
def semantic(s):
 out=[]
 for x in parse(s):
  d={'mode':x['mode'],'id':x['id'],'revision':x['revision']}
  if x['mode']=='table':d['columns']=x['columns']
  if x['mode']=='5w1h':d['columns']=['What','Why','How','Who','When','Where']
  d['records']=x['records']
  out.append(d)
 return {'domains':out}
records=[]
for name,source in S.items():
 payload=semantic(source)
 enc={'nema':source,'json':json.dumps(payload,ensure_ascii=False,separators=(',',':')),'yaml':yaml.safe_dump(payload,allow_unicode=True,sort_keys=False,width=100000,default_flow_style=True).strip()}
 for fmt,text in enc.items():
  records.append({'scenario':name,'format':fmt,'bytes_utf8':len(text.encode()),'neutral_bpe_tokens':len(sp.encode(text)),'source':text})
report={'tokenizer':'local SentencePiece neutral_bpe.model (vocab 1800), not provider API','semantics':'JSON/YAML encode full explicit mode/ID/revision/records/columns; NEMA uses implicit 5W1H semantic columns','records':records}
(R/'bench/REVIEW_TOKEN_COMPARE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (R/'bench/REVIEW_TOKEN_COMPARE.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=['scenario','format','bytes_utf8','neutral_bpe_tokens']);wr.writeheader();wr.writerows({k:r[k] for k in wr.fieldnames} for r in records)
print('Comparable local measurements:')
for r in records:print(r['scenario'],r['format'],r['bytes_utf8'],r['neutral_bpe_tokens'])
