"""NEMA v1.1 reference parser (SPACE-X / LF-Y; experimental).

Canonical .nema is the stable editing source, never the compressed .nemat wire format.
X0..X5 in 5W1H: What, Why, How, Who, When, Where.
Native headers/mode selectors use Tab; *body column separators use ASCII SPACE*.
This library's human renderer is deliberately semantic, NOT byte-reversible.
"""
from __future__ import annotations
import re
from typing import Any

HEADER = re.compile(r'^\t(>?)([A-Za-z][A-Za-z0-9_.-]*) ([1-9][0-9]*)$')
EDGE = re.compile(r'^([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)([><=])([A-Za-z][A-Za-z0-9_.:-]*)$')
NODE = re.compile(r'^[A-Za-z][A-Za-z0-9_.:-]*$')
CJK = re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]')
PASCAL = re.compile(r'[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|[0-9]+|[^A-Za-z0-9]+')
FIELD_NAMES = ('What','Why','How','Who','When','Where')


def rows_from(source: str) -> list[str]:
    if '\r' in source:raise ValueError('NEMA v1.1 requires LF (no CR)')
    if not source.endswith('\n\n\n') or source.endswith('\n\n\n\n'):
        raise ValueError('document must end with exactly two empty physical lines (three LF)')
    rows=source[:-3].split('\n')
    if not rows or any(r=='' for r in rows):
        raise ValueError('blank interior rows forbidden (no inter-domain empty line)')
    return rows


def cell_escape(s:str)->str:
    return s.replace('\\','\\\\').replace(' ','\\ ').replace('\t','\\t')


def cell_unescape(s:str)->str:
    out=[];i=0
    while i<len(s):
        if s[i]!='\\':out.append(s[i]);i+=1;continue
        if i+1>=len(s):raise ValueError('trailing native backslash')
        next=s[i+1]
        if next in ('\\',' ','t'):
            out.append('\t' if next=='t' else next);i+=2;continue
        if next=='=': # exact-literal hint retained in AST, stripped by semantic view
            out.append('\\=');i+=2;continue
        raise ValueError('unknown native cell escape: '+next)
    return ''.join(out)


def split_x(row:str)->list[str]:
    """Single SPACE separates columns, escaped SPACE stays within a column."""
    fields=[];buf=[];i=0
    while i<len(row):
        if row[i]=='\\' and i+1<len(row) and row[i+1] in ('\\',' ','t','='):
            buf.append(row[i:i+2]);i+=2;continue
        if row[i]==' ':
            fields.append(cell_unescape(''.join(buf)));buf=[];i+=1;continue
        if row[i]=='\t':raise ValueError('raw Tab forbidden in body; escape it as \\t')
        buf.append(row[i]);i+=1
    fields.append(cell_unescape(''.join(buf)))
    return fields


def append_columns(cols:list[list[str]],cells:list[str])->None:
    for i,s in enumerate(cells):
        while len(cols)<=i:cols.append([])
        if s:cols[i].append(s)


def parse(source:str)->list[dict[str,Any]]:
    domains=[];d=None;seen=set()
    for line in rows_from(source):
        m=HEADER.fullmatch(line)
        if m:
            mark,name,rev=m.groups();key=(name,int(rev))
            if key in seen:raise ValueError('duplicate domain ID/revision')
            seen.add(key)
            d={'id':name,'revision':int(rev),'mode':'graph' if mark else None,
               'raw_rows':[],'columns':[],'records':[]}
            domains.append(d);continue
        if d is None:raise ValueError('data before domain header')
        if d['mode'] is None:d['mode']='table' if line.startswith('\t') else '5w1h'
        if d['mode']=='table' and not d['raw_rows']:
            if not line.startswith('\t') or line.startswith('\t\t'):
                raise ValueError('table header must begin with exactly one Tab')
            labels=split_x(line[1:])
            if len(set(labels))!=len(labels) or not labels or any(not x for x in labels):
                raise ValueError('table columns missing or duplicate')
            d['columns']=labels
        elif d['mode']=='5w1h':
            cells=split_x(line)
            if len(cells)>6:raise ValueError('5W1H supports max six columns')
            append_columns(d.setdefault('fields',[[] for _ in range(6)]),cells)
        elif d['mode']=='table':
            cells=split_x(line)
            if len(cells)>len(d['columns']):raise ValueError('too many table columns')
            if cells[0]:d['records'].append({'values':[]})
            elif not d['records']:raise ValueError('table continuation before first data row')
            append_columns(d['records'][-1]['values'],cells)
        else:
            cells=split_x(line)
            if cells[0]:
                code=cells[0];edge=EDGE.fullmatch(code)
                if edge:
                    a,left,e,right,b=edge.groups()
                    if left!=right:raise ValueError('edge must use matching direction markers')
                    frm,to=(b,a) if left=='<' else (a,b)
                    record={'kind':'edge','id':e,'source':frm,'target':to,
                            'direction':left,'raw':code,'values':[]}
                else:
                    if not NODE.fullmatch(code):raise ValueError('invalid node declaration')
                    record={'kind':'node','id':code,'values':[]}
                d['records'].append(record)
            elif not d['records']:raise ValueError('graph continuation before first node/edge')
            append_columns(d['records'][-1]['values'],cells)
        d['raw_rows'].append(line)
    for d in domains:
        if not d['raw_rows']:raise ValueError('empty domain')
        if d['mode']=='table' and not d['records']:raise ValueError('empty table')
        if d['mode']=='graph':
            nodes=set();edges=set()
            for r in d['records']:
                if r['kind']=='node':
                    if r['id'] in nodes:raise ValueError('duplicate node')
                    nodes.add(r['id'])
                else:
                    if r['id'] in edges:raise ValueError('duplicate edge ID')
                    edges.add(r['id'])
            for r in d['records']:
                if r['kind']=='edge' and (r['source'] not in nodes or r['target'] not in nodes):
                    raise ValueError('dangling graph reference')
    return domains


def lexical_words(s:str)->list[str]:
    """HTTPItIs -> HTTP, It, Is. Adjacent uppercase acronym ambiguity is not soluble."""
    return [m.group() for m in PASCAL.finditer(s)]


def join_intents(chunks:list[str],language:str='auto')->str:
    """Human-readable display, not a reversible transform.
    \\=literal is an exact-literal hint for APIs, paths, identifiers and proper nouns.
    """
    parts=[]
    for raw in chunks:
        if not raw:continue
        exact=raw.startswith('\\=')
        body=raw[2:] if exact else raw
        # CJK text glues naturally; exact-marked strings and symbol-heavy strings are opaque.
        if exact or language in ('zh','ja') or (language=='auto' and CJK.search(body)) or bool(re.search(r'[./:#@]',body)):
            atoms=[body]
        elif ' ' in body:
            atoms=[atom for segment in body.split(' ') for atom in lexical_words(segment)]
        else:atoms=lexical_words(body)
        for atom in atoms:
            if not atom:continue
            if not exact and language not in ('zh','ja') and re.fullmatch(r'[A-Za-z]+',atom):
                if not atom.isupper() and parts:
                    atom=atom.lower()
            if not parts:parts.append(atom);continue
            if atom[0] in ',.;:!?、。！？）]}\'’"' or parts[-1].endswith(("'",'’')):
                parts[-1]+=atom
            elif CJK.search(parts[-1][-1]) or CJK.search(atom[0]):
                parts[-1]+=atom
            else:parts.append(atom)
    return ' '.join(parts)


def view(source:str,language:str='auto')->list[dict[str,Any]]:
    result=[]
    for d in parse(source):
        v={'id':d['id'],'revision':d['revision'],'mode':d['mode']}
        if d['mode']=='5w1h':
            v['fields']={name:join_intents(d['fields'][i],language) for i,name in enumerate(FIELD_NAMES)}
        elif d['mode']=='table':
            v['columns']=d['columns']
            v['records']=[{name:join_intents(r['values'][i],language) if i<len(r['values']) else ''
                           for i,name in enumerate(d['columns'])} for r in d['records']]
        else:
            v['nodes']=[{'id':r['id'],'name':join_intents(r['values'][1],language) if len(r['values'])>1 else '',
                         'description':join_intents(r['values'][2],language) if len(r['values'])>2 else ''}
                        for r in d['records'] if r['kind']=='node']
            v['edges']=[{'id':r['id'],'source':r['source'],'target':r['target'],
                         'direction':r['direction'],
                         'name':join_intents(r['values'][1],language) if len(r['values'])>1 else '',
                         'description':join_intents(r['values'][2],language) if len(r['values'])>2 else ''}
                        for r in d['records'] if r['kind']=='edge']
        result.append(v)
    return result
