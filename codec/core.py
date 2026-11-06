"""NEMA v1.4 table-first native parser; horizontal ASCII space, vertical LF.

Invariants:
  - Leading TAB marks a domain header or initial dictionary manifest, never a field.
  - The unmarked domain is a Table. Its optional column header starts with '\\ '.
  - Every non-indented data line starts a record; N leading spaces continuates X(N-1).
  - Source coordinates are retained as ordered semantic fragments; rendered strings are views.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re

HEADER = re.compile(r'^\t([?>]?)([A-Za-z][A-Za-z0-9_.-]*) ([1-9][0-9]*)$')
DICT = re.compile(r'^\t\$([0-9]+)$')
EDGE = re.compile(r'^([A-Za-z][A-Za-z0-9_.-]*)([><=])([A-Za-z][A-Za-z0-9_.-]*)([><=])([A-Za-z][A-Za-z0-9_.-]*)$')
REF = re.compile(r'\^([0-9]+)')
ENGLISH = re.compile(r'[A-Z]+(?=[A-Z][a-z]|$)|[A-Z][a-z]+|[A-Z]+|[a-z]+|[0-9]+|[^A-Za-z0-9]+')
MODES = {'':'table', '?':'5w1h', '>':'graph'}
AXES = ['What','Why','How','Who','When','Where']
MAX_BYTES = 16 * 1024 * 1024

@dataclass
class Record:
    cells: list[list[str]] = field(default_factory=list)
    explicit_tail_empty: bool = False
    def add(self, col: int, part: str):
        while len(self.cells) <= col: self.cells.append([])
        self.cells[col].append(part)

@dataclass
class Domain:
    id: str
    revision: int
    mode: str
    columns: list[str] = field(default_factory=list)
    records: list[Record] = field(default_factory=list)
    explicit_header: bool = False

@dataclass
class Document:
    domains: list[Domain] = field(default_factory=list)
    dictionary: list[str] = field(default_factory=list)


def validate_source(source: str):
    if len(source.encode('utf-8')) > MAX_BYTES: raise ValueError('source too large')
    if '\r' in source: raise ValueError('LF only')
    if not source.endswith('\n\n\n') or source.endswith('\n\n\n\n'):
        raise ValueError('must terminate with exactly two empty physical lines (three LF)')
    if not source[:-3]: raise ValueError('no content')
    if '\n\n' in source[:-3]: raise ValueError('internal empty line prohibited')
    return source[:-3].split('\n')


def unescape_opaque(v: str) -> str:
    # Only backslash and caret are escapes in the native format. \\. is a literal dot.
    out = []
    i = 0
    while i < len(v):
        if v[i] == '\\' and i + 1 < len(v) and v[i+1] in ('^','\\','.'):
            out.append(v[i+1]); i += 2
        else:
            out.append(v[i]); i += 1
    return ''.join(out)


def mixed_atoms(raw: str, dictionary: list[str]) -> list[tuple[str,bool]]:
    """Return opaque dictionary values separately; PascalCase cannot split them."""
    result: list[tuple[str,bool]] = []
    buf = []
    i = 0
    def flush():
        if buf:
            result.append((unescape_opaque(''.join(buf)),False)); buf.clear()
    while i < len(raw):
        if raw[i] == '\\' and i + 1 < len(raw):
            buf.append(raw[i:i+2]); i += 2; continue
        m = REF.match(raw,i)
        if m:
            ix = int(m.group(1))
            if ix >= len(dictionary): raise ValueError(f'undefined dictionary reference ^{ix}')
            flush(); result.append((dictionary[ix],True)); i = m.end(); continue
        buf.append(raw[i]); i += 1
    flush()
    return result


def render_text(raw: str, dictionary: list[str]) -> str:
    items = mixed_atoms(raw, dictionary)
    out = []
    for text, opaque in items:
        if opaque:
            out.append(text)
        else:
            # Chinese/Japanese remain contiguous; English Camel/Pascal segments get spaces.
            if re.search(r'[\u3040-\u30ff\u3400-\u9fff]', text):
                out.append(text)
            else:
                pieces = ENGLISH.findall(text)
                # Avoid adding spaces around ASCII punctuation or numeric suffixes.
                v = ''
                for part in pieces:
                    if not v: v=part
                    elif part.isalpha() and v[-1:].isalpha(): v+=' '+part
                    else: v+=part
                out.append(v)
    # Dictionary atoms are indivisible; insert spaces only for English surroundings.
    joined = ''
    for i, chunk in enumerate(out):
        if i and chunk:
            prev = joined[-1:]
            if (prev.isascii() and prev.isalnum() and chunk[0].isascii() and chunk[0].isalnum()): joined += ' '
        joined += chunk
    return joined


def join_cell(parts: list[str], dictionary: list[str]) -> str:
    # Vertical groups concatenate without invented syntax for CJK; words in English get spaces.
    acc = ''
    for p in parts:
        r = render_text(p,dictionary)
        if not acc: acc = r; continue
        if r and r[0] in ',.;:!?)]}、。，！？；：': acc += r
        elif r and (r[0] in "'’" or acc[-1] in "'’"): acc += r
        elif any('\u3040' <= x <= '\u9fff' for x in acc[-1:] + r[:1]): acc += r
        else: acc += ' ' + r
    return acc


def parse(source: str) -> Document:
    lines = validate_source(source)
    doc = Document()
    i = 0
    if DICT.fullmatch(lines[0]):
        n = int(DICT.fullmatch(lines[0]).group(1)); i = 1
        if n > 2048 or i + n > len(lines): raise ValueError('bad dictionary manifest size')
        doc.dictionary = [unescape_opaque(s) for s in lines[i:i+n]]
        if any((not s or '\t' in s) for s in doc.dictionary): raise ValueError('dictionary entries must be nonempty TAB-free')
        i += n
    current: Domain | None = None
    for line in lines[i:]:
        h = HEADER.fullmatch(line)
        if h:
            current = Domain(h.group(2),int(h.group(3)),MODES[h.group(1)])
            if current.mode == '5w1h': current.columns = AXES.copy()
            if current.mode == 'graph': current.columns = ['Element','Relation','Description']
            if any(d.id==current.id for d in doc.domains): raise ValueError('duplicate domain ID')
            doc.domains.append(current)
            continue
        if '\t' in line: raise ValueError('TAB is reserved for domain/dictionary control; body uses ASCII spaces')
        if current is None: raise ValueError('body before domain')
        # The first line of default Table may declare the header with the exact prefix '\\ '.
        if current.mode == 'table' and not current.records and not current.explicit_header and line.startswith('\\ '):
            names = line[2:].split(' ')
            if not names or any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*',x) for x in names):
                raise ValueError('table headers require nonempty single-token names')
            if len(set(names)) != len(names): raise ValueError('duplicate column header')
            current.columns = names
            current.explicit_header = True
            continue
        if line.startswith(' '):
            if not current.records: raise ValueError('continuation before first record')
            n = len(line) - len(line.lstrip(' '))
            part = line[n:]
            if not part: raise ValueError('blank continuation')
            current.records[-1].add(n-1,part)
        else:
            # End-of-row sentinel: final ' .' is explicit missing remaining fields.
            empty = line.endswith(' .') and not line.endswith(' \\.')
            if empty: line = line[:-2]
            cells = line.split(' ')
            if not cells or any(not x for x in cells):
                raise ValueError('horizontal coordinates require exactly one ASCII space')
            rec=Record(explicit_tail_empty=empty)
            for j,c in enumerate(cells): rec.add(j,c)
            current.records.append(rec)
        if current.mode == 'table':
            while len(current.columns) < len(current.records[-1].cells):
                current.columns.append(f'column{len(current.columns)+1}')
        elif current.mode == 'graph' and not line.startswith(' '):
            e=current.records[-1].cells[0][0]
            if '>' in e or '<' in e or '=' in e:
                m=EDGE.fullmatch(e)
                if not m or m.group(2)!=m.group(4): raise ValueError(f'invalid edge expression: {e}')
            elif not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*',e):
                raise ValueError(f'invalid node ID {e}')
        if current.mode=='5w1h' and len(current.records[-1].cells)>6:
            raise ValueError('5w1h maximum six fields')
    if not doc.domains: raise ValueError('no domains')
    # Native correctness also requires every inline dictionary reference to resolve.
    for domain in doc.domains:
        for record in domain.records:
            for cell in record.cells:
                for group in cell:
                    mixed_atoms(group, doc.dictionary)
    return doc


def render(source: str) -> dict:
    doc = parse(source)
    out=[]
    for d in doc.domains:
        rows=[]
        for rec in d.records:
            vals=[join_cell(parts,doc.dictionary) for parts in rec.cells]
            if d.mode=='5w1h': vals += ['']*(6-len(vals))
            row={'cells':vals,'groups':rec.cells,'tail_empty':rec.explicit_tail_empty}
            if d.mode=='graph':
                m=EDGE.fullmatch(rec.cells[0][0]);
                if m:
                    a,operator,eid,_,b=m.groups();
                    if operator=='>': start,end=a,b
                    elif operator=='<': start,end=b,a
                    else: start,end=a,b
                    row['edge']={'id':eid,'from':start,'to':end,'direction':'undirected' if operator=='=' else 'directed'}
                else: row['node']={'id':rec.cells[0][0]}
            rows.append(row)
        out.append({'id':d.id,'revision':d.revision,'mode':d.mode,'columns':d.columns,'explicit_header':d.explicit_header,'rows':rows})
    return {'dictionary':doc.dictionary,'domains':out}
