"""Explicit .NEMA v1.3 -> v1.5 migration; v1.3 headers start with TAB."""
from __future__ import annotations
from pathlib import Path
import argparse
from tools import native_v13_legacy as legacy
from codec import native as current

def migrate(source:str)->str:
    legacy.parse(source)
    out=[];mode=None;first=False
    for line in legacy.rows_from(source):
        m=legacy.HEADER.fullmatch(line)
        if m:
            mark,name,revision=m.groups();mode='graph' if mark=='>' else None;first=True
            if mode=='graph':out.append(' >'+name+' '+revision)
            else:out.append(' '+name+' '+revision)
            continue
        if first and mode is None:
            mode='table' if line.startswith('\t') else '5w1h'
            if mode=='5w1h':
                header=out.pop();out.append(' ?'+header[1:])
            else:
                line=' '+line[1:]
        first=False
        out.append(line)
    result='\n'.join(out)+'\n\n\n'
    original=legacy.view(source)
    updated=current.view(result)
    for a,b in zip(original,updated):
        if a['mode']!=b['mode'] or {k:v for k,v in a.items() if k not in ('mode',)}!={k:v for k,v in b.items() if k not in ('mode',)}:
            raise ValueError('migration semantic mismatch')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');a=ap.parse_args()
    Path(a.output).write_text(migrate(Path(a.input).read_text(encoding='utf-8')),encoding='utf-8',newline='\n')
if __name__=='__main__':main()
