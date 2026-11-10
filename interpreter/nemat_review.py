"""Explicit, nonrecursive and UTF-8 byte reversible NEMAT1 reference codec.
Dictionary controls use ASCII spaces exclusively; source literal ^ escapes as \^.
Compression is optional; it may be worse than native NEMA in tokens/bytes.
"""
from __future__ import annotations
import re,json,collections,argparse,hashlib
from pathlib import Path

MAGIC=' \\!NEMAT1\n'
DATA=' \\!DATA\n'
DICT=re.compile(r'^ @([0-9]+) (".*")$')
REF=re.compile(r'\^([0-9]+)')
WORD=re.compile(r'[A-Za-z_][A-Za-z_0-9]{6,}')
MAX_OUTPUT=32*1024*1024

def choose_candidates(source):
 counts=collections.Counter(WORD.findall(source))
 return [word for word,n in counts.most_common() if n>=3 and len(word)>=8][:64]

def _make(source,words):
 safe=source.replace('^','\\^')
 dictionary=list(words)
 # replace matches longest first so they cannot overlap
 if dictionary:
  pattern=re.compile('|'.join(re.escape(w) for w in sorted(dictionary,key=len,reverse=True)))
  idx={word:i for i,word in enumerate(dictionary)}
  safe=pattern.sub(lambda m:'^'+str(idx[m.group()]),safe)
 control=MAGIC+' $'+str(len(dictionary))+'\n'+''.join(' @'+str(i)+' '+json.dumps(v,ensure_ascii=False)+'\n' for i,v in enumerate(dictionary))+DATA
 return control+safe

def encode(source, maximize_savings=True):
 if isinstance(source,bytes):source=source.decode('utf-8','strict')
 # evaluate byte savings, default no dict if dictionary cost outweighs use
 items=[];best=_make(source,items);bestsize=len(best.encode('utf-8'))
 for word in choose_candidates(source):
  candidate=_make(source,items+[word]);sz=len(candidate.encode('utf-8'))
  if not maximize_savings or sz<bestsize:
   items.append(word);best=candidate;bestsize=sz
 return best

def decode(text,max_output=MAX_OUTPUT):
 if isinstance(text,bytes):text=text.decode('utf-8','strict')
 if not text.startswith(MAGIC):raise ValueError('invalid NEMAT1 magic')
 rest=text[len(MAGIC):]
 countline,sep,rest=rest.partition('\n')
 if not sep or not re.fullmatch(r' \$[0-9]+',countline):raise ValueError('invalid dict count')
 count=int(countline[2:])
 if count>100000:raise ValueError('dictionary too large')
 dictionary=[]
 for i in range(count):
  line,sep,rest=rest.partition('\n')
  if not sep:raise ValueError('truncated dictionary')
  m=DICT.fullmatch(line)
  if not m or int(m.group(1))!=i:raise ValueError('duplicate/invalid dictionary ID')
  try:val=json.loads(m.group(2))
  except json.JSONDecodeError as e:raise ValueError('invalid dictionary string') from e
  if not isinstance(val,str) or not val:raise ValueError('dictionary value must be non-empty string')
  dictionary.append(val)
 if not rest.startswith(DATA):raise ValueError('missing DATA marker')
 payload=rest[len(DATA):]
 output=[];size=0;i=0
 while i<len(payload):
  ch=payload[i]
  if ch=='\\' and payload[i:i+2]=='\\^':piece='^';i+=2
  elif ch=='^':
   m=REF.match(payload,i)
   if not m:raise ValueError('invalid dictionary reference')
   idx=int(m.group(1))
   if idx>=count:raise ValueError('undefined dictionary ref '+str(idx))
   piece=dictionary[idx];i=m.end()
  else:piece=ch;i+=1
  size+=len(piece.encode('utf-8'))
  if size>max_output:raise ValueError('decompressed output limit exceeded')
  output.append(piece)
 return ''.join(output)

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
 for action in ('encode','decode'):
  p=sub.add_parser(action);p.add_argument('source');p.add_argument('target')
 args=ap.parse_args()
 inp=Path(args.source).read_bytes()
 if args.action=='encode':out=encode(inp).encode('utf-8')
 else:out=decode(inp).encode('utf-8')
 Path(args.target).write_bytes(out)
 print('source sha256',hashlib.sha256(inp).hexdigest(),'output sha256',hashlib.sha256(out).hexdigest())
if __name__=='__main__':main()
