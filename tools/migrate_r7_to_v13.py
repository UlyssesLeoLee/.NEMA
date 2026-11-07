#!/usr/bin/env python3
"""Explicit .NEMA R7 Graph -> v1.3 migration, preserving domain headers byte-for-byte.
Usage: python tools/migrate_r7_to_v13.py old.nema new.nema
Never auto-migrates in place. Needs the preserved original R7 parser.
"""
from pathlib import Path
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,str(path))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
old=load(ROOT/'archive/R7_original/codec__native.py','nema_r7_native')
new=load(ROOT/'tools/native_v13_legacy.py','nema_v13_native')

def migrate(src):
    old.parse(src)  # Fail closed for malformed input, not a heuristic indent fixer.
    result=[];graph=False
    for line in src.split('\n'):
        header=old.HEADER.fullmatch(line)
        if header:
            graph=header.group(1)=='>'
            result.append(line)
        elif graph and line.startswith(' '):
            result.append(line[1:])
        else:result.append(line)
    out='\n'.join(result)
    if old.view(src)!=new.view(out):
        raise ValueError('semantic mismatch; migration aborted')
    # Ensure all domain header lines have unchanged bytes.
    oldheads=[x for x in src.split('\n') if old.HEADER.fullmatch(x)]
    newheads=[x for x in out.split('\n') if new.HEADER.fullmatch(x)]
    if oldheads!=newheads:raise ValueError('domain header changed; migration aborted')
    return out

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: migrate_r7_to_v13.py SOURCE.nema TARGET.nema')
    a,b=map(Path,sys.argv[1:]);
    if a.resolve()==b.resolve():raise SystemExit('refusing in-place migration')
    if b.exists():raise SystemExit('refusing to overwrite output')
    raw=a.read_bytes();decoded=raw.decode('utf-8')
    b.write_bytes(migrate(decoded).encode('utf-8'))
    print(f'migrated {a} -> {b}')
