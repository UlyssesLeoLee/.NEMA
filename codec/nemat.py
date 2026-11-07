"""Experimental NEMA v1.1 transport codec.  Native SPACE geometry is preserved byte for byte.
Stateful control lines use SPACE; escaped caret is \\^ (literal ^).
Requires out-of-band format negotiation: NEVER silently parse .nemat as .nema.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import re
from typing import Callable
from .native import HEADER, rows_from, parse as parse_native

SUFFIX=re.compile(r'^(.*?)(\d+)$')
SELECT=re.compile(r'^\t(\d+)$')
SHORT=re.compile(r'^\t(\d+) ([1-9][0-9]*)$')
DICT=re.compile(r'^\t\$(\d+)$')
ALIAS=re.compile(r'^\^(\d+)$')
MAX_DICT=64
MAX_INPUT=16*1024*1024
SECRET=re.compile(r'(?i)(?:sk-(?:proj-)?[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{20,}|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[^\s]+|Bearer\s+[A-Za-z0-9._-]{12,})')

@dataclass(frozen=True)
class Result:
    mode:str
    text:str
    score:int
    source_bytes:int
    result_bytes:int


def _rows(text:str)->list[str]:
    if len(text.encode())>MAX_INPUT:raise ValueError('input too large')
    return rows_from(text)


def _join(lines:list[str])->str:
    return '\n'.join(lines)+'\n\n\n'


def split_raw(line:str)->list[str]:
    # Don't unescape native cells: guarantees exact source byte roundtrip.
    out=[];buf=[];i=0
    while i<len(line):
        if line[i]=='\\' and i+1<len(line) and line[i+1] in (' ','\\','t'):
            buf.extend((line[i],line[i+1]));i+=2;continue
        if line[i]==' ':
            out.append(''.join(buf));buf=[];i+=1;continue
        buf.append(line[i]);i+=1
    out.append(''.join(buf))
    return out


def esc(s:str)->str:
    return s.replace('^', '\\^')


def unesc(s:str)->str:
    # Only \^ is transport-specific; other backslashes are owned by native syntax.
    out=[];i=0
    while i<len(s):
        if s[i]=='\\' and i+1<len(s) and s[i+1]=='^':
            out.append('^');i+=2;continue
        if s[i]=='^':raise ValueError('literal ^ requires \\^ in transport')
        out.append(s[i]);i+=1
    return ''.join(out)


def _stem(header_match):
    mark,name,_=header_match.groups()
    m=SUFFIX.fullmatch(name)
    return (mark,m.group(1),m.group(2)) if m and m.group(1) else None


def prefix_encode(lines:list[str],use:bool)->list[str]:
    groups={};active=None;out=[]
    for line in lines:
        m=HEADER.fullmatch(line)
        if m:
            base=_stem(m)
            if base is None:out.append(line);active=None;continue
            marker,stem,num=base;key=(marker,stem)
            if key not in groups:
                groups[key]=len(groups);out.append(line);active=groups[key];continue
            g=groups[key]
            candidate=([f'\t{g}'] if g!=active else [])+[f'\t{num} {m.group(3)}']
            if use and sum(len(s.encode())+1 for s in candidate)<len(line.encode())+1:
                out+=candidate
            else:out.append(line)
            active=g
        elif SHORT.fullmatch(line) or SELECT.fullmatch(line):
            # Escaped reserved table header/rare native line. Not interpreted as control.
            out.append('\t\\'+line[1:])
        else:out.append(line)
    return out


def prefix_decode(lines:list[str])->list[str]:
    groups=[];seen={};active=None;out=[]
    for line in lines:
        if line.startswith('\t\\') and (SHORT.fullmatch('\t'+line[2:]) or SELECT.fullmatch('\t'+line[2:])):
            out.append('\t'+line[2:]);continue
        m=HEADER.fullmatch(line)
        if m:
            base=_stem(m)
            if base is None:active=None
            else:
                key=base[:2]
                if key not in seen:seen[key]=len(groups);groups.append(key)
                active=seen[key]
            out.append(line);continue
        m=SELECT.fullmatch(line)
        if m:
            idx=int(m.group(1))
            if idx>=len(groups):raise ValueError('undefined prefix group')
            active=idx;continue
        m=SHORT.fullmatch(line)
        if m:
            if active is None:raise ValueError('missing prefix group')
            mark,stem=groups[active]
            out.append(f'\t{mark}{stem}{m.group(1)} {m.group(2)}');continue
        out.append(line)
    return out


def cell_candidates(source:str)->list[str]:
    out=[];mode=None;first=False
    for line in _rows(source):
        m=HEADER.fullmatch(line)
        if m:mode='graph' if m.group(1) else None;first=True;continue
        if first and mode is None:
            mode='table' if line.startswith('\t') else '5w1h'
        if first and mode=='table':first=False;continue
        first=False
        vals=split_raw(line)
        for i,s in enumerate(vals):
            if not s or len(s)<3 or len(s.encode())>16384 or SECRET.search(s):continue
            if mode=='graph' and i==0:continue
            out.append(s)
    return out


def dict_encode(lines:list[str],dictionary:list[str])->list[str]:
    look={v:'^'+str(i) for i,v in enumerate(dictionary)}
    mode=None;first=False;out=[]
    for line in lines:
        m=HEADER.fullmatch(line)
        if m:mode='graph' if m.group(1) else None;first=True;out.append(line);continue
        if first and mode is None:mode='table' if line.startswith('\t') else '5w1h'
        if first and mode=='table':out.append(esc(line));first=False;continue
        first=False
        vals=split_raw(line)
        out.append(' '.join((esc(v) if mode=='graph' and idx==0 else look.get(v,esc(v))) for idx,v in enumerate(vals)))
    return out


def dict_decode(lines:list[str],dictionary:list[str])->list[str]:
    mode=None;first=False;out=[]
    for line in lines:
        m=HEADER.fullmatch(line)
        if m:mode='graph' if m.group(1) else None;first=True;out.append(line);continue
        if first and mode is None:mode='table' if line.startswith('\t') else '5w1h'
        if first and mode=='table':out.append(unesc(line));first=False;continue
        first=False
        vals=split_raw(line)
        decoded=[]
        for idx,value in enumerate(vals):
            ref=ALIAS.fullmatch(value)
            if ref and not (mode=='graph' and idx==0):
                n=int(ref.group(1))
                if n>=len(dictionary):raise ValueError('invalid alias')
                decoded.append(dictionary[n])
            else:decoded.append(unesc(value))
        out.append(' '.join(decoded))
    return out


def encode(source:str, dictionary:list[str]|None=None, prefixes=True)->str:
    lines=_rows(source);dictionary=list(dictionary or [])
    if len(dictionary)>MAX_DICT or len(set(dictionary))!=len(dictionary):raise ValueError('dictionary invalid')
    if any(not s or '\n' in s or '\t' in s or len(s.encode())>16384 for s in dictionary):
        raise ValueError('invalid dictionary entry')
    body=prefix_encode(dict_encode(lines,dictionary),prefixes)
    manifest=([f'\t${len(dictionary)}']+[esc(s) for s in dictionary]) if dictionary else []
    return _join(manifest+body)


def decode(source:str)->str:
    lines=_rows(source);dic=[]
    if lines and (m:=DICT.fullmatch(lines[0])):
        n=int(m.group(1))
        if n>MAX_DICT or len(lines)<n+2:raise ValueError('invalid dictionary count')
        dic=[unesc(s) for s in lines[1:n+1]]
        if any(not s for s in dic) or len(set(dic))!=n:raise ValueError('invalid dictionary entries')
        lines=lines[n+1:]
    output=_join(dict_decode(prefix_decode(lines),dic))
    if len(output.encode())>MAX_INPUT:raise ValueError('decoded source too large')
    parse_native(output)  # fail closed: corrupted manifests must not reconstruct invalid native streams
    return output


def candidates(source:str,scorer:Callable[[str],int]|None=None,max_dictionary:int=12)->dict[str,Result]:
    _rows(source)
    scorer=scorer or (lambda t:len(t.encode()))
    counts=Counter(cell_candidates(source))
    allowed=sorted((s for s,n in counts.items() if n>1),key=lambda s:(-counts[s]*len(s.encode()),s))[:30]
    opts={'native':source,'prefix':encode(source,[],True)}
    for pref in (False,True):
        chosen=[];current=encode(source,chosen,pref)
        for _ in range(min(max_dictionary,len(allowed))):
            best=None;low=scorer(current)
            for s in allowed:
                if s in chosen:continue
                try:trial=encode(source,chosen+[s],pref)
                except ValueError:continue
                cost=scorer(trial)
                if cost<low:low=cost;best=(s,trial)
            if best is None:break
            chosen.append(best[0]);current=best[1]
        opts['combined' if pref else 'dictionary']=current
    result={}
    for mode,txt in opts.items():
        if mode!='native' and decode(txt)!=source:raise AssertionError('lossless codec validation failed: '+mode)
        result[mode]=Result(mode,txt,scorer(txt),len(source.encode()),len(txt.encode()))
    return result


def optimize(source:str,scorer:Callable[[str],int]|None=None)->Result:
    return min(candidates(source,scorer).values(),key=lambda c:(c.score,c.result_bytes,0 if c.mode=='native' else 1))
