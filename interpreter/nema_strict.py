"""NEMA strict candidate parser for the reviewed 7-column grammar matrix.
Only SPACE U+0020 is syntax whitespace; no native raw Tab or fullwidth whitespace.
Data AST distinguishes missing/null/empty string. The original v1.5 parser remains
in _Interpreter_Standalone as a historical implementation, not an alias for this.
"""
import re, json, sys, argparse
from pathlib import Path

HEADER=re.compile(r'^ \\([?>]?)([1-9][0-9]*) ([1-9][0-9]*)$')
NODE=re.compile(r'^[A-Za-z][A-Za-z0-9_.:-]*$')
EDGE=re.compile(r'^([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)$')
ESC={' ':' ', '\\':'\\', '?':'?', '>':'>','<':'<','=':'=', '~':'~','^':'^', '#':'#', '_':'_','%':'%', 'n':'\n','r':'\r','t':'\t'}
MISSING={'type':'missing'}
class NemaError(ValueError):
 def __init__(self,line,message):super().__init__(f'line {line}: {message}');self.line=line;self.detail=message

def fields(text,line):
 if not text:raise NemaError(line,'empty field expression')
 out=[];cur=[];i=0
 while i<len(text):
  c=text[i]
  if c=='\\':
   if i+1>=len(text):raise NemaError(line,'trailing escape')
   n=text[i+1]
   if n not in ESC:raise NemaError(line,f'unknown escape \\{n}')
   cur.append(('literal',ESC[n]));i+=2;continue
  if c==' ':
   if not cur:raise NemaError(line,'consecutive spaces or empty field')
   out.append(_value(cur));cur=[];i+=1;continue
  cur.append(('raw',c));i+=1
 if not cur:raise NemaError(line,'trailing separator space')
 out.append(_value(cur));return out

def _value(parts):
 if len(parts)==1 and parts[0]==('raw','~'):return None
 if len(parts)==1 and parts[0]==('raw','\\_'):return MISSING # unreachable; handled below
 s=''.join(v for _,v in parts)
 if len(parts)==1 and parts[0]==('literal','_'):return MISSING
 if len(parts)==1 and parts[0]==('literal','e'):return ''
 return s
# \\e requires a special escaped token distinct from raw e
ESC['e']='\u0000EMPTY\u0000'
_old_value=_value
def _value(parts):
 if len(parts)==1:
  t,v=parts[0]
  if t=='raw' and v=='~':return None
  if t=='literal' and v=='_':return dict(MISSING)
  if t=='literal' and v=='\u0000EMPTY\u0000':return ''
 return ''.join(v for _,v in parts)

def field_display(v):
 if isinstance(v,dict):return '<Missing>'
 if v is None:return '<Null>'
 return v

def parse(source):
 if '\t' in source:raise NemaError(0,'raw Tab U+0009 prohibited')
 if '\u3000' in source:raise NemaError(0,'fullwidth space U+3000 prohibited')
 if '\r' in source:raise NemaError(0,'CR prohibited in native source; use LF')
 items=[];active=None;ids=set()
 lines=source.split('\n')
 if lines and lines[-1]=='':lines.pop()
 for li,raw in enumerate(lines,1):
  if raw=='':continue
  header=HEADER.fullmatch(raw)
  if header:
   tag,ident,rev=header.groups()
   if ident in ids:raise NemaError(li,'duplicate domain ID')
   ids.add(ident);mode={'':'table','?':'5w1h','>':'graph'}[tag]
   active={'mode':mode,'id':int(ident),'revision':int(rev),'rows':[]}
   if mode=='table':active.update(columns=None,records=[],explicit=False,declared_width=None)
   if mode=='5w1h':active['records']=[]
   if mode=='graph':active['records']=[]
   items.append(active);continue
  if re.match(r'^ +\\(?:[?>]?[0-9]|[?>]?\s)',raw):raise NemaError(li,'malformed domain header')
  if active is None:raise NemaError(li,'body before domain header')
  mode=active['mode']
  # Graph uses leading spaces as X2+, non-graph as X1+
  if mode=='table' and raw.startswith('\\#'):
   if active['records'] or active['explicit']:raise NemaError(li,'header only allowed before records')
   if raw=='\\#':raise NemaError(li,'header requires names')
   if not raw.startswith('\\# '):raise NemaError(li,'invalid table header')
   names=fields(raw[3:],li)
   if any(not isinstance(n,str) or n=='' for n in names):raise NemaError(li,'column name must be nonempty text')
   if len(set(names))!=len(names):raise NemaError(li,'duplicate column name')
   if active['declared_width'] is not None and len(names)!=active['declared_width']:raise NemaError(li,'column width mismatch')
   active['columns']=names;active['explicit']=True;active['rows'].append(raw);continue
  if mode=='table' and raw.startswith('\\%'):
   if active['records'] or active['declared_width'] is not None:raise NemaError(li,'width declaration must be unique and before records')
   if not re.fullmatch(r'\\%[1-9][0-9]*',raw):raise NemaError(li,'invalid width declaration')
   n=int(raw[2:]);active['declared_width']=n;active['columns']=['column'+str(i+1) for i in range(n)]
   active['rows'].append(raw);continue
  leading=len(raw)-len(raw.lstrip(' '))
  if leading:
   if not active['records']:raise NemaError(li,'continuation without record')
   column=leading+(1 if mode=='graph' else 0)
   if mode=='5w1h' and column>=6:raise NemaError(li,'5w1h continuation outside six fields')
   if mode=='table' and column>=len(active['columns']):raise NemaError(li,'continuation exceeds table width')
   values=fields(raw[leading:],li)
   if len(values)!=1:raise NemaError(li,'continuation must contain one field; escape inner spaces')
   val=values[0]
   if not isinstance(val,str):raise NemaError(li,'continuation value must be text')
   rec=active['records'][-1];cols=rec['values']
   was_new=column>=len(cols)
   while len(cols)<=column:cols.append(dict(MISSING))
   previous=cols[column]
   if previous is None:raise NemaError(li,'cannot append to null value')
   if isinstance(previous,dict):
    if mode=='graph' and was_new:cols[column]=val
    else:raise NemaError(li,'cannot append to missing value')
   else:cols[column]=previous+val
   active['rows'].append(raw);continue
  vals=fields(raw,li)
  if mode=='table':
   if active['columns'] is None:active['columns']=['column'+str(i+1) for i in range(len(vals))]
   if len(vals)>len(active['columns']):raise NemaError(li,'record exceeds table width')
   vals+= [dict(MISSING) for _ in range(len(active['columns'])-len(vals))]
   active['records'].append({'values':vals})
  elif mode=='5w1h':
   if len(vals)>6:raise NemaError(li,'5w1h exceeds six fields')
   vals += [dict(MISSING) for _ in range(6-len(vals))]
   active['records'].append({'values':vals})
  else:
   token=vals[0]
   if not isinstance(token,str):raise NemaError(li,'graph identifier must be text')
   if any(sym in token for sym in ('>','<','=')):
    e=EDGE.fullmatch(token)
    if not e or e.group(2)!=e.group(4):raise NemaError(li,'invalid edge expression')
    a,op,edge_id,_,b=e.groups()
    if len(vals)<2:raise NemaError(li,'edge name missing')
    rec={'kind':'edge','id':edge_id,'from':b if op=='<' else a,'to':a if op=='<' else b,'operator':op,'values':vals}
   else:
    if not NODE.fullmatch(token):raise NemaError(li,'invalid node identifier')
    if len(vals)<2:raise NemaError(li,'node name missing')
    rec={'kind':'node','id':token,'values':vals}
   active['records'].append(rec)
  active['rows'].append(raw)
 for domain in items:
  if domain['mode']=='graph':
   nodes=set();edges=set()
   for rec in domain['records']:
    if rec['kind']=='node':
     if rec['id'] in nodes:raise NemaError(0,'duplicate node ID: '+rec['id'])
     nodes.add(rec['id'])
    else:
     if rec['id'] in edges:raise NemaError(0,'duplicate edge ID: '+rec['id'])
     edges.add(rec['id'])
   if nodes&edges:raise NemaError(0,'node and edge IDs overlap')
   for rec in domain['records']:
    if rec['kind']=='edge' and (rec['from'] not in nodes or rec['to'] not in nodes):raise NemaError(0,'dangling edge endpoint '+rec['id'])
 return items

def cli():
 p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('--json',action='store_true');ns=p.parse_args()
 try:
  result=parse(Path(ns.path).read_text(encoding='utf-8'));print(json.dumps(result,indent=2,ensure_ascii=False))
 except (NemaError,UnicodeError) as e:print(str(e),file=sys.stderr);sys.exit(2)
if __name__=='__main__':cli()
