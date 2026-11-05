"""i/1 reference codec: schema-table text, stable domains, optional intern table and ID prefixes.

No executable semantics. This reference implementation is designed for reproducible experiments.
"""
from __future__ import annotations
from collections import Counter, OrderedDict
from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import re
from typing import Any

GROUP_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,15}\Z", re.ASCII)
ID_RE = re.compile(r"[A-Za-z0-9_.-]{1,96}\Z", re.ASCII)
FIELD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,31}\Z", re.ASCII)
BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MAX_BYTES = 32 * 1024 * 1024
MAX_DECODED_BYTES = 64 * 1024 * 1024

class IFormatError(ValueError): pass
class Conflict(IFormatError): pass

@dataclass
class Node:
    group: str
    local_id: str
    rev: int
    values: dict[str, Any]

    @property
    def ref(self): return f"{self.group}/{self.local_id}"

@dataclass
class Document:
    schemas: dict[str, list[tuple[str,str]]] = field(default_factory=dict)
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: set[tuple[str,str,str]] = field(default_factory=set)

    def add(self, group: str, local_id: str, values: dict, rev: int = 1):
        if not GROUP_RE.fullmatch(group) or not ID_RE.fullmatch(local_id):
            raise IFormatError("invalid domain identifier")
        if type(rev) is not int or rev < 1 or rev > 2**63-1:
            raise IFormatError("invalid revision")
        if group not in self.schemas: raise IFormatError("undeclared group")
        keys = {k for k, _ in self.schemas[group]}
        if set(values) != keys: raise IFormatError(f"fields mismatch for {group}: {set(values) ^ keys}")
        for k,t in self.schemas[group]: validate_type(values[k], t)
        node = Node(group, local_id, rev, dict(values))
        if node.ref in self.nodes: raise IFormatError(f"duplicate domain: {node.ref}")
        self.nodes[node.ref] = node

    def link(self, src: str, dst: str, relation: str):
        if not FIELD_RE.fullmatch(relation): raise IFormatError("invalid relation")
        if src not in self.nodes or dst not in self.nodes: raise IFormatError("dangling edge")
        edge = (src, dst, relation)
        if edge in self.edges: raise IFormatError("duplicate edge")
        self.edges.add(edge)

    def canonical_obj(self):
        return {
            'schemas': {g: [{'name':name, 'type':typ} for name, typ in fields] for g,fields in sorted(self.schemas.items())},
            'nodes': [dict(group=n.group, id=n.local_id, rev=n.rev, **n.values) for n in sorted(self.nodes.values(), key=lambda x:x.ref)],
            'edges': [dict(src=a, dst=b, rel=c) for a,b,c in sorted(self.edges)]
        }

def validate_type(v, typ):
    if typ == 's':
        if type(v) is not str: raise IFormatError("expected string")
    elif typ == 'n':
        if type(v) is not int or abs(v) > 2**63 - 1: raise IFormatError("expected 64-bit integer")
    elif typ == 'b':
        if type(v) is not bool: raise IFormatError("expected boolean")
    else: raise IFormatError("unknown field type")

def esc(s: str) -> str:
    # The first '^' is reserved for a dictionary reference in string-value positions.
    z = s.replace('\\','\\\\').replace('|','\\|').replace('\n','\\n').replace('\r','\\r').replace('\t','\\t')
    return ('\\' + z) if z.startswith('^') else z

def unesc(s: str) -> str:
    if '\\' not in s: return s
    out = []
    i = 0
    replacements = {'n':'\n','r':'\r','t':'\t','|':'|','\\':'\\','^':'^'}
    while i < len(s):
        if s[i] == '\\':
            if i+1 >= len(s) or s[i+1] not in replacements: raise IFormatError("invalid escape")
            out.append(replacements[s[i+1]]); i += 2
        else:
            out.append(s[i]); i += 1
    return ''.join(out)

def split_line(s: str) -> list[str]:
    if '\\' not in s: return s.split('|')
    parts = []; buf = []; esc_next = False
    for c in s:
        if esc_next: buf.append(c); esc_next = False
        elif c == '\\': buf.append(c); esc_next = True
        elif c == '|': parts.append(''.join(buf)); buf=[]
        else: buf.append(c)
    if esc_next: raise IFormatError("dangling escape")
    parts.append(''.join(buf))
    return parts

def as_text(v: Any, typ: str) -> str:
    validate_type(v,typ)
    if typ == 's': return esc(v)
    if typ == 'b': return '1' if v else '0'
    return str(v)

def from_text(s: str, typ: str, dictionary: dict[str, str]):
    if typ == 's':
        if s.startswith('^'):
            if s[1:] not in dictionary: raise IFormatError('unknown dictionary key')
            return dictionary[s[1:]]
        return unesc(s)
    if typ == 'b':
        if s not in ('0','1'): raise IFormatError('noncanonical boolean')
        return s == '1'
    if len(s) > 20 or not re.fullmatch(r'-?(0|[1-9][0-9]*)', s, re.ASCII): raise IFormatError('noncanonical integer')
    v = int(s)
    validate_type(v, typ)
    return v

def base62(n: int) -> str:
    out = ''
    while True:
        out = BASE62[n % 62] + out
        n = n // 62 - 1
        if n < 0: return out

def choose_dictionary(doc: Document) -> dict[str,str]:
    # Only string *values*, not schema and identity, can be interned.
    counts = Counter()
    for node in doc.nodes.values():
        for name, typ in doc.schemas[node.group]:
            if typ == 's': counts[node.values[name]] += 1
    candidates = []
    for value, count in counts.items():
        raw = esc(value)
        # rank by the possible one-letter saving; dictionary overhead includes newline.
        possible = count * (len(raw.encode('utf-8')) - 2) - (len(raw.encode('utf-8')) + 4)
        if possible > 0: candidates.append((possible, value))
    candidates.sort(key=lambda x:(-x[0], x[1]))
    result = {}
    for _, value in candidates:
        code = base62(len(result))
        raw = esc(value)
        ref = '^'+code
        definition = '$'+code+'|'+raw+'\n'
        saving = counts[value]*(len(raw.encode('utf-8')) - len(ref.encode('utf-8'))) - len(definition.encode('utf-8'))
        if saving > 0: result[value] = code
    return result

def choose_prefixes(doc: Document) -> dict[str,str]:
    result = {}
    for g in doc.schemas:
        ids = [n.local_id for n in doc.nodes.values() if n.group == g]
        if len(ids)<2: continue
        import os
        prefix = __import__('os').path.commonprefix(ids)
        # Keep only prefix ending at a human-readable ID separator; avoid surprising partial IDs.
        p = max(prefix.rfind('.'),prefix.rfind('-'),prefix.rfind('_'))+1
        prefix = prefix[:p]
        if not prefix or prefix in ids: continue
        refs = sum(1 for a,b,c in doc.edges for ref in (a,b) if ref.startswith(g+'/'))
        saving = (len(ids)+refs)*len(prefix.encode('utf-8')) - len((':'+g+'|'+prefix+'\n').encode('utf-8'))
        if saving > 0: result[g] = prefix
    return result

def write(doc: Document, round_num: int = 3) -> str:
    """Round 0 verbose fields; 1 table schemas; 2+ dictionary; 3 ID-prefix.
    Rounds 0-2 are historical benchmark encodings; only round 3 is normative i/1.
    """
    if round_num not in (0,1,2,3): raise ValueError('round')
    if round_num == 0:
        rows = ['!i0']
        for g,fields in sorted(doc.schemas.items()):
            rows.append('%'+g+'|'+','.join(k+':'+t for k,t in fields))
        for n in sorted(doc.nodes.values(),key=lambda x:x.ref):
            fields = [key+'='+as_text(n.values[key], typ) for key,typ in doc.schemas[n.group]]
            rows.append('@'+n.ref+':'+str(n.rev)+'|'+ '|'.join(fields))
        for a,b,c in sorted(doc.edges): rows.append('>'+a+'|'+b+'|'+c)
        return '\n'.join(rows)+'\n'
    rows = ['!i1']
    for g,fields in sorted(doc.schemas.items()):
        rows.append('%'+g+'|'+','.join(k+':'+t for k,t in fields))
    dictionary = choose_dictionary(doc) if round_num>=2 else {}
    for value,code in sorted(dictionary.items(),key=lambda x:(len(x[1]),x[1])):
        rows.append('$'+code+'|'+esc(value))
    prefixes = choose_prefixes(doc) if round_num==3 else {}
    for g,p in sorted(prefixes.items()): rows.append(':'+g+'|'+p)
    def short_ref(ref):
        g, ident = ref.split('/',1)
        return g+'/'+ident[len(prefixes[g]):] if g in prefixes else ref
    for n in sorted(doc.nodes.values(),key=lambda x:x.ref):
        vals = []
        for key,typ in doc.schemas[n.group]:
            v = n.values[key]
            vals.append('^'+dictionary[v] if typ=='s' and v in dictionary else as_text(v,typ))
        rows.append('@'+short_ref(n.ref)+':'+str(n.rev)+'|'+'|'.join(vals))
    for a,b,c in sorted(doc.edges):
        rows.append('>'+short_ref(a)+'|'+short_ref(b)+'|'+c)
    return '\n'.join(rows)+'\n'

def parse(text: str, *, strict: bool=True) -> Document:
    if len(text.encode('utf-8')) > MAX_BYTES: raise IFormatError('file too large')
    if not text.endswith('\n'): raise IFormatError('missing final newline')
    # splitlines() also breaks on U+2028/U+0085, which are legal field contents.
    lines = text[:-1].split('\n')
    if not lines or lines[0] != '!i1': raise IFormatError('unsupported format header')
    doc = Document(); dictionary = {}; prefixes = {}
    decoded_bytes = 0
    phase = 'meta'
    for linenum, line in enumerate(lines[1:],2):
        if not line: raise IFormatError(f'empty line at {linenum}')
        head = line[0]; parts = split_line(line[1:])
        if head == '%':
            if phase != 'meta' or len(parts)!=2 or not GROUP_RE.fullmatch(parts[0]) or parts[0] in doc.schemas:
                raise IFormatError('invalid schema declaration')
            fields=[]; seen=set()
            for part in parts[1].split(','):
                kv=part.split(':')
                if len(kv)!=2 or not FIELD_RE.fullmatch(kv[0]) or kv[0] in seen or kv[1] not in ('s','n','b'):
                    raise IFormatError('invalid field type/duplicate')
                fields.append((kv[0], kv[1]));seen.add(kv[0])
            if not fields: raise IFormatError('empty schema')
            doc.schemas[parts[0]]=fields
        elif head == '$':
            if phase != 'meta' or len(parts)!=2 or not re.fullmatch('[A-Za-z0-9]+',parts[0]) or parts[0] in dictionary:
                raise IFormatError('bad dictionary declaration')
            dictionary[parts[0]]=unesc(parts[1])
        elif head == ':':
            if phase != 'meta' or len(parts)!=2 or parts[0] not in doc.schemas or parts[0] in prefixes:
                raise IFormatError('bad ID-prefix declaration')
            if not ID_RE.fullmatch(parts[1]) or parts[1][-1] not in '._-':
                raise IFormatError('bad prefix')
            prefixes[parts[0]]=parts[1]
        elif head == '@':
            phase='nodes'
            if len(parts)<2: raise IFormatError('invalid node')
            m=re.fullmatch(r'([A-Za-z][A-Za-z0-9_-]{0,15})/([A-Za-z0-9_.-]{1,96}):([1-9][0-9]*)',parts[0],re.ASCII)
            if not m: raise IFormatError('invalid node identity/revision')
            g,shortid,rev=m.groups()
            if len(rev) > 19: raise IFormatError('revision too large')
            if g not in doc.schemas: raise IFormatError('unknown group')
            if len(parts)-1!=len(doc.schemas[g]): raise IFormatError('wrong number of fields')
            local_id=prefixes.get(g,'')+shortid
            values={name:from_text(val,typ,dictionary) for (name,typ),val in zip(doc.schemas[g],parts[1:])}
            decoded_bytes += sum(len(v.encode('utf-8')) for v in values.values() if type(v) is str)
            if decoded_bytes > MAX_DECODED_BYTES: raise IFormatError('decoded content too large')
            doc.add(g,local_id,values,int(rev))
        elif head == '>':
            if phase not in ('nodes','edges') or len(parts)!=3: raise IFormatError('invalid edge')
            phase='edges'
            def long_ref(s):
                if '/' not in s: raise IFormatError('invalid edge reference')
                g, local_id=s.split('/',1)
                return g+'/'+prefixes.get(g,'')+local_id
            a,b,rel=parts
            doc.link(long_ref(a),long_ref(b),rel)
        else: raise IFormatError('unknown record prefix')
    if strict:
        if write(doc,3)!=text: raise IFormatError('noncanonical encoding')
    return doc

@dataclass
class SetField:
    ref: str
    base_rev: int
    field: str
    value: Any


@dataclass
class EditDomain:
    ref: str
    base_rev: int
    values: dict[str, Any]

@dataclass
class AddNode:
    group: str
    local_id: str
    values: dict[str,Any]

@dataclass
class DelNode:
    ref: str
    base_rev: int

@dataclass
class AddEdge:
    src: str; dst: str; relation: str

@dataclass
class DelEdge:
    src: str; dst: str; relation: str

def apply(doc: Document, changes: list) -> Document:
    """Transactional, optimistic-CAS patch. No silent last-writer-wins."""
    clone = deepcopy(doc)
    touched=set()
    # Forbid two operations on the same domain within one patch. A client can bundle
    # simultaneous field updates in a single ReplaceNode in a future version.
    for op in changes:
        if isinstance(op,EditDomain):
            if op.ref in touched: raise Conflict('duplicate domain touched in patch')
            touched.add(op.ref)
            if op.ref not in clone.nodes: raise Conflict('missing domain')
            node=clone.nodes[op.ref]
            if node.rev!=op.base_rev: raise Conflict('stale revision')
            if not op.values: raise IFormatError('empty edit')
            schema=dict(clone.schemas[node.group])
            for key,value in op.values.items():
                if key not in schema: raise IFormatError('unknown field')
                validate_type(value,schema[key])
            node.values.update(op.values); node.rev+=1
        elif isinstance(op,SetField):
            if op.ref in touched: raise Conflict('duplicate domain touched in patch')
            touched.add(op.ref)
            if op.ref not in clone.nodes: raise Conflict('missing domain')
            node=clone.nodes[op.ref]
            if node.rev!=op.base_rev: raise Conflict('stale revision')
            typ=dict(clone.schemas[node.group]).get(op.field)
            if typ is None: raise IFormatError('unknown field')
            validate_type(op.value,typ)
            node.values[op.field]=op.value;node.rev+=1
        elif isinstance(op,AddNode):
            ref=op.group+'/'+op.local_id
            if ref in touched: raise Conflict('duplicate domain touched in patch')
            touched.add(ref)
            clone.add(op.group,op.local_id,op.values)
        elif isinstance(op,DelNode):
            if op.ref in touched: raise Conflict('duplicate domain touched in patch')
            touched.add(op.ref)
            if op.ref not in clone.nodes or clone.nodes[op.ref].rev!=op.base_rev: raise Conflict('missing/stale revision')
            if any(op.ref in (a,b) for a,b,_ in clone.edges): raise Conflict('cannot delete referenced domain')
            del clone.nodes[op.ref]
        elif isinstance(op,AddEdge):
            clone.link(op.src,op.dst,op.relation)
        elif isinstance(op,DelEdge):
            edge=(op.src,op.dst,op.relation)
            if edge not in clone.edges: raise Conflict('missing edge')
            clone.edges.remove(edge)
        else: raise IFormatError('unknown operation')
    return clone

def digest(doc: Document) -> str:
    return sha256(write(doc,3).encode('utf-8')).hexdigest()
