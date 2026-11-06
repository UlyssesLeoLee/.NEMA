"""Experimental NEMA/2: one zero-indent block = one independent Agent work domain.
Horizontal TAB cells = schema slots; vertical leading-space count = record role.
Canonical UTF-8 / LF, simple deterministic reference codec; no exec semantics.
"""
from __future__ import annotations
import re
from collections import defaultdict
from i_codec import (Document, IFormatError, GROUP_RE, ID_RE, FIELD_RE,
   validate_type, choose_dictionary, choose_prefixes, MAX_BYTES, MAX_DECODED_BYTES,base62)

VERSION='n2'
ROLES={'uses':2, 'touches':3, 'depends':4}
ROLE_NAMES={v:k for k,v in ROLES.items()}
REF_RE=re.compile(r'([A-Za-z][A-Za-z0-9_-]{0,15})/([A-Za-z0-9_.-]{1,96})\Z',re.ASCII)

# Literal string escapes: tabs and physical line breaks must be escaped, ordinary spaces/punctuation unescaped.
def escape(v: str) -> str:
    return v.replace('\\','\\\\').replace('\t','\\t').replace('\n','\\n').replace('\r','\\r')
def unescape(s:str)->str:
    if '\\' not in s:return s
    mapping={'t':'\t','n':'\n','r':'\r','s':' ','\\':'\\'}
    out=[];i=0
    while i<len(s):
        if s[i]!='\\':out.append(s[i]);i+=1;continue
        if i+1>=len(s) or s[i+1] not in mapping:raise IFormatError('bad escape')
        out.append(mapping[s[i+1]]);i+=2
    return ''.join(out)

def slot(v, kind, dic):
    validate_type(v,kind)
    if kind=='b':return '1' if v else '0'
    if kind=='n':return str(v)
    if v in dic:return '^'+dic[v]
    # Raw strings beginning ^ are legal; dictionary aliases are unambiguous via \^ escape.
    text=escape(v)
    if text.startswith(' '): text='\\s'+text[1:]
    return '\\'+text if text.startswith('^') else text

def decode(s,kind,dic):
    if kind=='b':
        if s not in ('0','1'):raise IFormatError('noncanonical bool')
        return s=='1'
    if kind=='n':
        if len(s)>20 or not re.fullmatch(r'-?(0|[1-9][0-9]*)',s,re.ASCII):raise IFormatError('invalid integer')
        v=int(s);validate_type(v,'n');return v
    if s.startswith('^'):
        if s[1:] not in dic:raise IFormatError('unknown dictionary code')
        return dic[s[1:]]
    if s.startswith('\\^'):return '^'+unescape(s[2:])
    return unescape(s)

def encode_ref(ref,prefixes):
    g,local=ref.split('/',1)
    p=prefixes.get(g,'')
    return g+'/'+local[len(p):]

def decode_ref(ref,prefixes):
    m=REF_RE.fullmatch(ref)
    if not m:raise IFormatError('invalid domain reference')
    g,local=m.groups()
    full=prefixes.get(g,'')+local
    if not ID_RE.fullmatch(full): raise IFormatError('decoded domain name invalid')
    return g+'/'+full

def _dictionary(doc):
    # Adapt dictionary to TAB encoding; entries are chosen only if byte savings are positive.
    from collections import Counter
    count=Counter(n.values[k] for n in doc.nodes.values() for k,t in doc.schemas[n.group] if t=='s')
    result={}
    for v,n in sorted(count.items(), key=lambda x:(-x[1]*len(x[0].encode('utf-8')),x[0])):
        code=base62(len(result));ref='^'+code;line='$'+code+'\t'+escape(v)+'\n'
        gain=n*(len(escape(v).encode('utf-8'))-len(ref.encode('utf-8')))-len(line.encode('utf-8'))
        if gain>0:result[v]=code
    return result

def write(doc:Document, *, dictionary=True, prefixes=True, remove_schema=False):
    d=_dictionary(doc) if dictionary else {}
    pre=choose_prefixes(doc) if prefixes else {}
    out=[VERSION]
    if not remove_schema:
        for g,fields in sorted(doc.schemas.items()):
            out.append('%'+g+'\t'+'\t'.join(k+(':'+typ if typ!='s' else '') for k,typ in fields))
    for v,c in sorted(d.items(),key=lambda x:(len(x[1]),x[1])):
        out.append('$'+c+'\t'+escape(v))
    for g,p in sorted(pre.items()):out.append(':'+g+'\t'+p)
    links=defaultdict(list)
    for a,b,rel in doc.edges:links[a].append((b,rel))
    for n in sorted(doc.nodes.values(),key=lambda x:x.ref):
        # 0 spaces = domain, 1 space = positional schema row
        out.append(encode_ref(n.ref,pre)+' '+str(n.rev))
        out.append(' '+'\t'.join(slot(n.values[k],typ,d) for k,typ in doc.schemas[n.group]))
        for b,r in sorted(links[n.ref], key=lambda t:(ROLES.get(t[1],6),t[0],t[1])):
            indent=ROLES.get(r,6)
            out.append((' '*indent)+encode_ref(b,pre)+(('\t'+r) if indent==6 else ''))
        for check in sorted(getattr(doc,'checks',{}).get(n.ref,[])):
            out.append('     '+escape(check))
    return '\n'.join(out)+'\n'

def parse(source:str|bytes, *, external_schema=None):
    if isinstance(source,bytes):
        if len(source)>MAX_BYTES:raise IFormatError('input too large')
        source=source.decode('utf-8','strict')
    if len(source.encode('utf-8'))>MAX_BYTES:raise IFormatError('input too large')
    if '\r' in source or '\x00' in source or not source.endswith('\n'):raise IFormatError('invalid physical encoding')
    lines=source[:-1].split('\n')
    if not lines or lines[0]!=VERSION:raise IFormatError('bad version')
    doc=Document(schemas={g:list(fields) for g,fields in (external_schema or {}).items()})
    dic={};pre={};phase='header';current=None; awaiting=False;pending=[];decoded=0;checks=defaultdict(list)
    for num,line in enumerate(lines[1:],2):
        if not line:raise IFormatError(f'empty line at {num}')
        if line[0]=='%' and phase=='header':
            parts=line[1:].split('\t');g=parts[0]
            if not GROUP_RE.fullmatch(g) or g in doc.schemas or len(parts)<2 or len(parts)>65:
                raise IFormatError('invalid schema declaration')
            fields=[];seen=set()
            for x in parts[1:]:
                name,sep,typ=x.partition(':');typ=typ if sep else 's'
                if not FIELD_RE.fullmatch(name) or name in seen or typ not in ('s','b','n'):
                    raise IFormatError('invalid schema slot')
                fields.append((name,typ));seen.add(name)
            doc.schemas[g]=fields;continue
        if line[0]=='$' and phase=='header':
            parts=line[1:].split('\t')
            if len(parts)!=2 or not re.fullmatch(r'[A-Za-z0-9]+',parts[0],re.ASCII) or parts[0] in dic:
                raise IFormatError('bad dictionary')
            dic[parts[0]]=unescape(parts[1]);continue
        if line[0]==':' and phase=='header':
            parts=line[1:].split('\t')
            if len(parts)!=2 or parts[0] not in doc.schemas or parts[0] in pre or not ID_RE.fullmatch(parts[1]) or parts[1][-1] not in '._-':raise IFormatError('invalid prefix')
            pre[parts[0]]=parts[1];continue
        phase='domains'
        if line[0]!=' ':
            if line.endswith(' ') or line.endswith('\t'):raise IFormatError('trailing whitespace in domain header')
            if awaiting:raise IFormatError('domain missing payload')
            if line.count(' ')!=1 or '\t' in line:raise IFormatError('bad domain header')
            ref,rev=line.split(' ')
            if len(rev)>19 or not re.fullmatch(r'[1-9][0-9]*',rev,re.ASCII):raise IFormatError('bad domain revision')
            current=decode_ref(ref,pre)
            if current.split('/')[0] not in doc.schemas:raise IFormatError('undeclared schema')
            if current in doc.nodes:raise IFormatError('duplicate domain id')
            revision=int(rev);awaiting=True;continue
        if current is None:raise IFormatError('orphan child')
        indent=len(line)-len(line.lstrip(' '))
        data=line[indent:]
        if awaiting:
            if indent!=1:raise IFormatError('first row must be positional payload')
            g,local=current.split('/',1)
            fields=doc.schemas[g];parts=data.split('\t')
            if len(parts)!=len(fields):raise IFormatError('wrong slot count')
            vals={name:decode(s,typ,dic) for (name,typ),s in zip(fields,parts)}
            decoded+=sum(len(v.encode('utf-8')) for v in vals.values() if type(v)==str)
            if decoded>MAX_DECODED_BYTES:raise IFormatError('decoded content too large')
            doc.add(g,local,vals,rev=revision)
            if len(doc.nodes)>200_000:raise IFormatError('too many domains')
            awaiting=False;continue
        if indent==5:
            checks[current].append(unescape(data))
            continue
        if indent not in (2,3,4,6):raise IFormatError('undefined vertical slot')
        parts=data.split('\t')
        if indent==6:
            if len(parts)!=2 or not FIELD_RE.fullmatch(parts[1]):raise IFormatError('bad custom relation')
            target,rel=parts
        else:
            if len(parts)!=1:raise IFormatError('bad relation width')
            target,rel=data,ROLE_NAMES[indent]
        pending.append((current,decode_ref(target,pre),rel))
        if len(pending)>400_000:raise IFormatError('too many edges')
    if awaiting:raise IFormatError('dangling header')
    for a,b,r in pending:doc.link(a,b,r)
    doc.checks=dict(checks)
    return doc

def write_auto(doc:Document,objective='bytes',token_count=None):
    """Choose byte/gzip/token minimum over 4 legitimate encodings, with stable tie break.
    Token mode requires a *real target-model* tokenizer callback; no token estimation.
    """
    import gzip
    if objective not in ('bytes','gzip','tokens'):raise ValueError('unknown compression objective')
    if objective=='tokens' and token_count is None:raise ValueError('token_count callable required')
    candidates=[write(doc,dictionary=di,prefixes=pr) for di,pr in
        ((False,False),(True,False),(False,True),(True,True))]
    if objective=='bytes':scorer=lambda x:len(x.encode('utf-8'))
    elif objective=='gzip':scorer=lambda x:len(gzip.compress(x.encode('utf-8'),9,mtime=0))
    else:scorer=token_count
    return min(candidates,key=lambda x:(scorer(x),len(x.encode('utf-8'))))
