"""NEMA v1.4 .nemat lossless text transport codec.

Transport is opt-in by MIME/extension; never attempt autodetection on native .nema.
Dictionary manifest: first line TAB+$N, followed by N literal dictionary entries;
inline reference ^N, native literal caret \\^, slash \\\\; RLE \\8A or \\8\\7.
Numeric native IDs supersede alphabetic-prefix encoding; selector codes remain reserved
for future version negotiation, but are not emitted by the v1.5 reference encoder.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import re
from .core import parse, HEADER, MAX_BYTES

DICT_START = re.compile(r'^\t\$([0-9]+)$')
# Numeric domain headers have no reusable alphabetic prefix.
# TAB+digits remains reserved for negotiated future compressed selector groups.
ATOM = re.compile(r'[A-Za-z][A-Za-z0-9_]{3,}|[\u3400-\u9fff\u3040-\u30ff]{4,}')

@dataclass
class Choice:
    method: str
    text: str
    score: int
    baseline_score: int
    format: str
    @property
    def saving_percent(self):
        return round(100*(1-self.score/self.baseline_score),2) if self.baseline_score else 0


def _units(s, token_cost):
    if token_cost is None: return len(s.encode('utf-8'))
    return token_cost(s)


def _candidate_dict(body: list[str], max_entries=48) -> list[str]:
    c = Counter()
    for row in body:
        if row.startswith('\t'): continue
        c.update(ATOM.findall(row))
    choices=[]
    for word,num in c.items():
        if num < 3: continue
        if word.lower() in ('password','secret','credential'): continue
        if len(word)>48: continue  # conservative: avoid potential credential-like high-entropy strings
        gain=(num-1)*len(word) - num*3 - 5
        if gain>3: choices.append((gain,word))
    return [s for _,s in sorted(choices, key=lambda it:(-it[0],it[1]))[:max_entries]]


def _esc(s):
    return s.replace('\\','\\\\').replace('^','\\^')


def _encode_row(row, words: list[str], *, rle=True) -> str:
    # Keep all ASCII spaces exactly as source. No invented spacing or newline joins.
    order=sorted(enumerate(words),key=lambda x:(-len(x[1]),x[0]))
    out=[]; i=0
    while i < len(row):
        chosen=None
        for idx,w in order:
            if row.startswith(w,i): chosen=(idx,w); break
        if chosen is not None:
            out.append('^'+str(chosen[0])); i+=len(chosen[1]); continue
        ch=row[i];j=i+1
        if rle and ch!=' ':
            while j<len(row) and row[j]==ch: j+=1
            rep=j-i
            if rep>=4:
                enc='\\'+str(rep)+('\\'+ch if ch.isdigit() or ch=='\\' else ch)
                if len(enc)<len(_esc(ch))*rep:
                    out.append(enc);i=j;continue
        out.append(_esc(ch));i+=1
    return ''.join(out)


def _decode_row(row,words):
    out=[]; i=0; bytes_so_far=0
    while i<len(row):
        ch=row[i]
        if ch=='^':
            m=re.match(r'\^([0-9]+)',row[i:])
            if not m: raise ValueError('invalid dictionary reference')
            ix=int(m.group(1))
            if ix>=len(words): raise ValueError('dictionary index out of range')
            out.append(words[ix]);i+=len(m.group());continue
        if ch=='\\':
            if i+1>=len(row): raise ValueError('trailing transport escape')
            v=row[i+1]
            if v in ('^','\\'):
                out.append(v);i+=2;continue
            if v.isascii() and v.isdigit():
                m=re.match(r'\\([0-9]+)',row[i:])
                n=int(m.group(1))
                if not 4<=n<=100000: raise ValueError('RLE count exceeds bounds')
                start=i+len(m.group())
                if start>=len(row): raise ValueError('RLE missing character')
                c=row[start]
                if c=='\\':
                    if start+1>=len(row): raise ValueError('missing escaped RLE character')
                    c=row[start+1];start+=1
                if c==' ' or c=='\t': raise ValueError('RLE may not encode coordinate separators')
                out.append(c*n);i=start+1;continue
            raise ValueError('unknown transport escape')
        out.append(ch);i+=1
        bytes_so_far+=len(ch.encode('utf-8'))
        if bytes_so_far>MAX_BYTES: raise ValueError('row too large')
    return ''.join(out)


def _build(source, words, *, use_rle=True):
    rows=source[:-3].split('\n')
    encoded=[]
    for row in rows:
        if row.startswith('\t') and HEADER.fullmatch(row):encoded.append(row)
        else:
            # In native .nema the original dictionary manifest is a control line too;
            # it must survive byte-for-byte after transport decode.
            encoded.append(_encode_row(row,words,rle=use_rle))
    manifest=['\t$'+str(len(words)), *[_esc(w) for w in words]]
    return '\n'.join(manifest+encoded)+'\n\n\n'


def encode(source, token_cost=None, *, max_entries=48) -> Choice:
    parse(source)
    baseline=_units(source,token_cost)
    rows=source[:-3].split('\n')
    words=_candidate_dict(rows,max_entries)
    candidates=[('dictionary+rle',_build(source,words)),
                ('dictionary',_build(source,words,use_rle=False)),
                ('rle',_build(source,[],use_rle=True))]
    best=Choice('native',source,baseline,baseline,'nema')
    for method,text in candidates:
        try: decoded=decode(text)
        except Exception: continue
        if decoded!=source: continue
        score=_units(text,token_cost)
        if score<best.score:
            best=Choice(method,text,score,baseline,'nemat')
    return best


def decode(text: str) -> str:
    if len(text.encode('utf-8')) > MAX_BYTES: raise ValueError('transport too large')
    if '\r' in text or not text.endswith('\n\n\n') or text.endswith('\n\n\n\n'):
        raise ValueError('invalid transport newline termination')
    rows=text[:-3].split('\n')
    head=DICT_START.fullmatch(rows[0]) if rows else None
    if not head: raise ValueError('expected transport dictionary manifest; pass native .nema separately')
    n=int(head.group(1))
    if n>2048 or len(rows)<n+2: raise ValueError('bad dictionary size')
    values=[_decode_row(v,[]) for v in rows[1:n+1]]
    if any(not v or '\n' in v or '\t' in v for v in values): raise ValueError('invalid dictionary value')
    out=[]
    for row in rows[n+1:]:
        if HEADER.fullmatch(row):
            out.append(row)
            continue
        if re.fullmatch(r'\t[0-9]+(?: [0-9]+)?',row):
            raise ValueError('unsupported legacy prefix selector; v1.5 uses numeric domain headers')
        v=_decode_row(row,values)
        if v.startswith('\t') and HEADER.fullmatch(v):
            raise ValueError('encoded domain header not permitted')
        out.append(v)
    expanded='\n'.join(out)+'\n\n\n'
    parse(expanded)
    if len(expanded.encode('utf-8'))>MAX_BYTES: raise ValueError('decoded source exceeds limit')
    return expanded
