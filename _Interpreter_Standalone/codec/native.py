""".NEMA v1.5 reference interpreter. Space-X and LF-Y; Graph Node/Edge both start at X0.
Editing syntax is not a byte-reversible natural language segmentation algorithm.
"""
from __future__ import annotations
import re
from typing import Any

HEADER=re.compile(r'^ ([?>]?)([A-Za-z0-9][A-Za-z0-9_.-]*) ([1-9][0-9]*)$')
EDGE=re.compile(r'^([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)$')
NODE=re.compile(r'^[A-Za-z][A-Za-z0-9_.:-]*$')
CJK=re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]')
PASCAL=re.compile(r'[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|[0-9]+|[^A-Za-z0-9]+')
FIELD_NAMES=('What','Why','How','Who','When','Where')

def rows_from(source:str)->list[str]:
    if '\r' in source:raise ValueError('UTF-8 LF only: CR is forbidden')
    if not source.endswith('\n\n\n') or source.endswith('\n\n\n\n'):
        raise ValueError('document ends with exactly two blank physical lines (3 LF)')
    rows=source[:-3].split('\n')
    if not rows or any(x=='' for x in rows):raise ValueError('blank interior rows forbidden')
    return rows

def unescape(s:str)->str:
    result=[];i=0
    while i<len(s):
        if s[i]!='\\':result.append(s[i]);i+=1;continue
        if i+1>=len(s):raise ValueError('trailing escape')
        char=s[i+1]
        if char in (' ','\\','t','='):
            result.append('\t' if char=='t' else ('\\=' if char=='=' else char));i+=2
        else:raise ValueError('invalid native escape '+repr(char))
    return ''.join(result)

def split_x(s:str)->list[str]:
    out=[];buf=[];i=0
    while i<len(s):
        if s[i]=='\\' and i+1<len(s) and s[i+1] in (' ','\\','t','='):
            buf.extend((s[i],s[i+1]));i+=2;continue
        if s[i]=='\t':raise ValueError('body raw Tab is reserved')
        if s[i]==' ':
            out.append(unescape(''.join(buf)));buf=[];i+=1;continue
        buf.append(s[i]);i+=1
    out.append(unescape(''.join(buf)));return out

def append_cols(cols:list[list[str]],cells:list[str])->None:
    for i,item in enumerate(cells):
        while len(cols)<=i:cols.append([])
        if item:cols[i].append(item)

def parse(source:str)->list[dict[str,Any]]:
    ds=[];d=None;seen=set()
    for lineno,line in enumerate(rows_from(source),1):
        if '\u3000' in line:raise ValueError(f'line {lineno}: fullwidth U+3000 whitespace forbidden; use ASCII space U+0020')
        head=HEADER.fullmatch(line)
        if head:
            graph,name,version=head.groups()
            if name in seen:raise ValueError('duplicate domain ID')
            seen.add(name)
            d={'id':name,'revision':int(version),'mode':'graph' if graph=='>' else ('5w1h' if graph=='?' else None),'raw_rows':[], 'records':[]}
            ds.append(d);continue
        if d is None:raise ValueError('body before header')
        if d['mode'] is None:d['mode']='table' if line.startswith(' ') else 'table_implicit'
        mode=d['mode']
        if mode=='table' and not d['raw_rows']:
            if not line.startswith(' ') or line.startswith('  '):raise ValueError('table header requires exactly one ASCII space')
            labels=split_x(line[1:])
            if not labels or any(not v for v in labels) or len(labels)!=len(set(labels)):
                raise ValueError('table header invalid')
            d['columns']=labels
        elif mode=='5w1h':
            cells=split_x(line)
            if len(cells)>6:raise ValueError('5w1h max six fields')
            append_cols(d.setdefault('fields',[[] for _ in range(6)]),cells)
        elif mode in ('table','table_implicit'):
            cells=split_x(line)
            if mode=='table_implicit' and not d['raw_rows']:
                if not cells[0]:raise ValueError('implicit table first row requires nonempty X0')
                d['columns']=['column'+str(i+1) for i in range(len(cells))]
            if mode=='table_implicit' and len(cells)>len(d['columns']):
                d['columns'].extend('column'+str(i+1) for i in range(len(d['columns']),len(cells)))
            elif mode=='table' and len(cells)>len(d['columns']):raise ValueError('table data too wide')
            if cells[0]:d['records'].append({'values':[]})
            elif not d['records']:raise ValueError('table continuation without record')
            append_cols(d['records'][-1]['values'],cells)
        else:
            # v1.3: X0 Node ID or relation, selected by the relation operators.
            # One leading ASCII space continues X2; two continue X3, etc.
            # Domain header is ASCII space + mode marker + ID + revision.
            if line.startswith(' '):
                if not d['records']:raise ValueError('graph continuation without element')
                cells=split_x(line)
                if not any(cells[1:]):raise ValueError('empty graph continuation')
                append_cols(d['records'][-1]['values'],['']+cells)
            else:
                cells=split_x(line)
                token=cells[0]
                if any(op in token for op in ('>','<','=')):
                    m=EDGE.fullmatch(token)
                    if not m:raise ValueError('invalid graph edge expression (cannot downgrade to node)')
                    a,op,e,op2,b=m.groups()
                    if op!=op2:raise ValueError('incompatible arrows')
                    source,target=((b,a) if op=='<' else (a,b))
                    r={'kind':'edge','id':e,'source':source,'target':target,'direction':op,'raw':token,'values':[]}
                else:
                    if not NODE.fullmatch(token):raise ValueError('invalid node declaration')
                    r={'kind':'node','id':token,'values':[]}
                d['records'].append(r)
                append_cols(r['values'],cells)
        d['raw_rows'].append(line)
    for d in ds:
        if not d['raw_rows']:raise ValueError('empty domain')
        if d['mode'] in ('table','table_implicit') and not d['records']:raise ValueError('empty table')
        if d['mode']=='graph':
            node_ids=set();edge_ids=set()
            for r in d['records']:
                if r['kind']=='node':
                    if r['id'] in node_ids:raise ValueError('duplicate node')
                    node_ids.add(r['id'])
                else:
                    if r['id'] in edge_ids:raise ValueError('duplicate edge')
                    edge_ids.add(r['id'])
            if node_ids & edge_ids:raise ValueError('node/edge ID collision')
            for r in d['records']:
                if r['kind']=='edge' and (r['source'] not in node_ids or r['target'] not in node_ids):
                    raise ValueError('dangling edge endpoint')
    return ds

def lexical_words(s:str)->list[str]:return [m.group() for m in PASCAL.finditer(s)]

def join_intents(chunks:list[str],language:str='auto',exact_name:bool=False)->str:
    parts=[]
    for chunk in chunks:
        if not chunk:continue
        exact=exact_name or chunk.startswith('\\=')
        body=chunk[2:] if chunk.startswith('\\=') else chunk
        if exact or language in ('zh','ja') or (language=='auto' and CJK.search(body)) or bool(re.search(r'[./:#@]',body)):
            atoms=[body]
        else:atoms=[x for x in lexical_words(body) if x]
        for atom in atoms:
            if not atom:continue
            if not exact and language not in ('zh','ja') and re.fullmatch(r'[A-Za-z]+',atom):
                if not atom.isupper() and parts:atom=atom.lower()
            if not parts:parts.append(atom);continue
            if atom[0] in ',.;:!?、。！？）]}\'’"' or parts[-1].endswith(("'",'’')):
                parts[-1]+=atom
            elif CJK.search(parts[-1][-1]) or CJK.search(atom[0]):parts[-1]+=atom
            else:parts.append(atom)
    return ' '.join(parts)

def view(source:str,language:str='auto')->list[dict[str,Any]]:
    output=[]
    for d in parse(source):
        record={'id':d['id'],'revision':d['revision'],'mode':d['mode']}
        if d['mode']=='5w1h':
            record['fields']={name:join_intents(d['fields'][i],language) for i,name in enumerate(FIELD_NAMES)}
        elif d['mode'] in ('table','table_implicit'):
            record['columns']=d['columns']
            record['records']=[{name:join_intents(r['values'][i],language) if i<len(r['values']) else ''
                for i,name in enumerate(d['columns'])} for r in d['records']]
        else:
            # Preserve Graph X3+ on the semantic output.  X2 is a free-form
            # description; X3+ may contain machine identifiers and MUST NOT be
            # PascalCase-normalized (e.g. SHA256, APIKey, HTTP401).
            def graph_extensions(r):
                return {'X'+str(i):join_intents(r['values'][i],language,exact_name=True)
                        for i in range(3,len(r['values'])) if r['values'][i]}
            def graph_node(r):
                item={'id':r['id'],
                    'name':join_intents(r['values'][1],language,exact_name=True) if len(r['values'])>1 else '',
                    'description':join_intents(r['values'][2],language) if len(r['values'])>2 else ''}
                ext=graph_extensions(r)
                if ext:item['extensions']=ext
                return item
            def graph_edge(r):
                item={'id':r['id'],'source':r['source'],'target':r['target'],'direction':r['direction'],
                    'name':join_intents(r['values'][1],language,exact_name=True) if len(r['values'])>1 else '',
                    'description':join_intents(r['values'][2],language) if len(r['values'])>2 else ''}
                ext=graph_extensions(r)
                if ext:item['extensions']=ext
                return item
            record['nodes']=[graph_node(r) for r in d['records'] if r['kind']=='node']
            record['edges']=[graph_edge(r) for r in d['records'] if r['kind']=='edge']
        output.append(record)
    return output
