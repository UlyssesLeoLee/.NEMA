"""NEMA/1 reference codec; stable IDs, schema-position records, scoped YAML-inspired indentation.
A deliberately narrow subset for AI-native, multi-agent interchange.
"""
from __future__ import annotations
from collections import Counter
from i_codec import (Document, IFormatError, GROUP_RE, ID_RE, FIELD_RE,
    as_text, from_text, split_line, esc, unesc, choose_dictionary, choose_prefixes,
    base62, MAX_BYTES, MAX_DECODED_BYTES)

MAGIC = '!n1'


def _ref_encode(ref: str, prefixes: dict[str,str]) -> str:
    g, local = ref.split('/', 1)
    return g + '/' + local.removeprefix(prefixes.get(g, ''))


def _ref_decode(ref: str, prefixes: dict[str,str]) -> str:
    if ref.count('/') != 1: raise IFormatError('bad reference')
    g, local = ref.split('/')
    if not GROUP_RE.fullmatch(g) or not ID_RE.fullmatch(local):
        raise IFormatError('bad reference')
    return g + '/' + prefixes.get(g, '') + local


def choose_defaults(doc: Document, dictionary: dict[str,str]):
    """Only remove a column when ALL nodes in that group share exactly the same typed value."""
    defaults = {}
    for g, schema in sorted(doc.schemas.items()):
        nodes = [n for n in doc.nodes.values() if n.group == g]
        if not nodes: continue
        for idx, (name, typ) in enumerate(schema):
            v = nodes[0].values[name]
            if not all(type(n.values[name]) is type(v) and n.values[name] == v for n in nodes):
                continue
            val = '^' + dictionary[v] if typ == 's' and v in dictionary else as_text(v, typ)
            # n rows avoid the field text AND its delimiter, including a single-field row.
            overhead = len(f' = {idx}|{val}\n'.encode('utf-8')) - 1  # adjusted to actual ' =idx|...'
            overhead = len(f' ={idx}|{val}\n'.encode('utf-8'))
            saved = len(nodes) * (len(val.encode('utf-8')) + 1)
            if saved > overhead:
                defaults.setdefault(g, {})[idx] = v
    return defaults


def write(doc: Document, enable_defaults=True, enable_dict=True, enable_prefixes=True) -> str:
    dictionary = choose_dictionary(doc) if enable_dict else {}
    prefixes = choose_prefixes(doc) if enable_prefixes else {}
    defaults = choose_defaults(doc, dictionary) if enable_defaults else {}
    out = [MAGIC]
    for g, fields in sorted(doc.schemas.items()):
        out.append('%'+g+'|'+','.join(f'{name}:{typ}' for name,typ in fields))
    for raw, code in sorted(dictionary.items(), key=lambda x: (len(x[1]), x[1])):
        out.append('$'+code+'|'+esc(raw))
    for g, prefix in sorted(prefixes.items()):
        out.append(':'+g+'|'+prefix)
    edgebysrc={}
    for src,dst,rel in sorted(doc.edges):
        edgebysrc.setdefault(src, []).append((dst,rel))
    for g, schema in sorted(doc.schemas.items()):
        nodes = sorted((n for n in doc.nodes.values() if n.group == g),key=lambda n:n.local_id)
        if not nodes: continue
        out.append(g+':')
        for idx, val in sorted(defaults.get(g,{}).items()):
            name, typ = schema[idx]
            enc = '^'+dictionary[val] if typ == 's' and val in dictionary else as_text(val, typ)
            out.append(f' ={idx}|{enc}')
        for n in nodes:
            lid = n.local_id.removeprefix(prefixes.get(g, ''))
            vals=[]
            for idx,(name,typ) in enumerate(schema):
                if idx in defaults.get(g,{}): continue
                val = n.values[name]
                vals.append('^'+dictionary[val] if typ == 's' and val in dictionary else as_text(val, typ))
            out.append(' @'+lid+':'+str(n.rev)+ ('|'+'|'.join(vals) if vals else ''))
            for dst, rel in edgebysrc.get(n.ref,[]):
                out.append('  >'+_ref_encode(dst,prefixes)+'|'+rel)
    return '\n'.join(out)+'\n'


def parse(source: str | bytes, max_bytes=MAX_BYTES) -> Document:
    if isinstance(source, bytes):
        if len(source)>max_bytes: raise IFormatError('document too large')
        source = source.decode('utf-8',errors='strict')
    elif len(source.encode('utf-8'))>max_bytes: raise IFormatError('document too large')
    if '\r' in source: raise IFormatError('physical CR not canonical')
    lines=source.split('\n')
    if not lines or lines[0]!=MAGIC or lines[-1]!='': raise IFormatError('invalid header or missing final LF')
    doc=Document()
    dict_code={}
    prefixes={}
    defaults={}
    section=None
    last_node=None
    phase='header'
    seen_groups=set()
    seen_data=False
    decoded_bytes=0
    for lineno, line in enumerate(lines[1:-1],2):
        if not line: raise IFormatError(f'blank line at {lineno}')
        if line.endswith(' '): raise IFormatError(f'trailing spaces at {lineno}')
        if line[0] not in (' ',) and line.endswith(':') and line[:-1] in doc.schemas:
            g=line[:-1]
            if g in seen_groups: raise IFormatError('duplicate section')
            seen_groups.add(g);section=g;last_node=None;seen_data=False;phase='section';continue
        if phase=='header':
            if line.startswith('%'):
                args=split_line(line[1:])
                if len(args)!=2 or not GROUP_RE.fullmatch(args[0]) or args[0] in doc.schemas:
                    raise IFormatError('bad schema')
                fields=[]; names=set()
                for part in args[1].split(','):
                    if part.count(':')!=1: raise IFormatError('bad schema field')
                    name,kind=part.split(':')
                    if not FIELD_RE.fullmatch(name) or name in names or kind not in ('s','n','b'):
                        raise IFormatError('bad schema field')
                    fields.append((name,kind));names.add(name)
                if not fields or len(fields)>64: raise IFormatError('invalid schema width')
                doc.schemas[args[0]]=fields
                continue
            if line.startswith('$'):
                pair=split_line(line[1:])
                if len(pair)!=2 or not pair[0] or pair[0] in dict_code:
                    raise IFormatError('bad dictionary')
                dict_code[pair[0]]=unesc(pair[1]);continue
            if line.startswith(':'):
                pair=split_line(line[1:])
                if len(pair)!=2 or pair[0] not in doc.schemas or pair[0] in prefixes:
                    raise IFormatError('bad prefix')
                if not pair[1] or not ID_RE.fullmatch(pair[1]): raise IFormatError('bad prefix')
                prefixes[pair[0]]=pair[1];continue
            raise IFormatError(f'bad header line {lineno}')
        if line.startswith(' ='):
            if seen_data: raise IFormatError('default after node')
            pair=split_line(line[2:])
            if len(pair)!=2 or not pair[0].isascii() or not pair[0].isdigit() or len(pair[0])>3 or (len(pair[0])>1 and pair[0][0]=='0'): raise IFormatError('bad default')
            idx=int(pair[0]); schema=doc.schemas[section]
            if idx>=len(schema) or idx in defaults.get(section,{}): raise IFormatError('default index invalid')
            val=from_text(pair[1],schema[idx][1],dict_code)
            defaults.setdefault(section,{})[idx]=val;continue
        if line.startswith(' @'):
            parts=split_line(line[2:])
            if parts[0].count(':')!=1: raise IFormatError('bad domain declaration')
            local,rev_text=parts[0].split(':')
            if not ID_RE.fullmatch(local) or not rev_text.isascii() or not rev_text.isdigit() or rev_text.startswith('0') or len(rev_text)>19:
                raise IFormatError('bad domain id or rev')
            schema=doc.schemas[section]
            expected=len(schema)-len(defaults.get(section,{}))
            if len(parts)-1!=expected: raise IFormatError(f'wrong field count at {lineno}')
            data={}
            j=1
            for idx,(name,typ) in enumerate(schema):
                if idx in defaults.get(section,{}):
                    data[name]=defaults[section][idx]
                else:
                    data[name]=from_text(parts[j],typ,dict_code);j+=1
            decoded_bytes += sum(len(v.encode('utf-8')) for v in data.values() if type(v) is str)
            if decoded_bytes > MAX_DECODED_BYTES: raise IFormatError('decoded content too large')
            full=prefixes.get(section,'')+local
            doc.add(section,full,data,rev=int(rev_text))
            if len(doc.nodes)>200_000: raise IFormatError('node count too large')
            last_node=section+'/'+full;seen_data=True;continue
        if line.startswith('  >'):
            if last_node is None: raise IFormatError('edge has no parent')
            pair=split_line(line[3:])
            if len(pair)!=2 or not FIELD_RE.fullmatch(pair[1]):
                raise IFormatError('bad edge')
            # Resolve destinations after all nodes are read; links can be forward refs.
            if not hasattr(doc, '_pending'): doc._pending=[]
            if len(doc._pending)>=400_000: raise IFormatError('edge count too large')
            doc._pending.append((last_node,_ref_decode(pair[0],prefixes),pair[1]))
            continue
        raise IFormatError(f'invalid indentation or syntax at {lineno}')
    for src,dst,rel in getattr(doc,'_pending',[]):doc.link(src,dst,rel)
    if hasattr(doc,'_pending'): del doc._pending
    return doc
