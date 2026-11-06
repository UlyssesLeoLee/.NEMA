"""Positional NEMA/2 patch. Whole patch is validated before any in-memory commit.
Format: 'p2 <schema_sha256>\n', then 'DOMAIN BASE_REV\n 1<TAB>VALUE\n'.
Each nonempty indented row edits a single zero-based schema slot.
"""
import hashlib, re
from i_codec import Document, IFormatError, EditDomain, apply
from nema2_codec import decode,decode_ref,escape,slot,VERSION

def schema_hash(schema):
    payload='\n'.join(g+'\t'+'\t'.join(k+':'+t for k,t in fields)
        for g,fields in sorted(schema.items()))
    return hashlib.sha256((VERSION+'\n'+payload).encode('utf-8')).hexdigest()

def parse_patch(doc:Document,src:str):
    if not src.endswith('\n') or '\r' in src:raise IFormatError('invalid patch line ending')
    lines=src[:-1].split('\n')
    if not lines or lines[0]!='p2 '+schema_hash(doc.schemas):
        raise IFormatError('schema fingerprint mismatch')
    result=[];last=None;fields=None;changes={};base=None
    def flush():
        if last is not None:
            if not changes:raise IFormatError('empty domain patch')
            result.append(EditDomain(last,base,dict(changes)))
    for line in lines[1:]:
        if not line:raise IFormatError('empty patch line')
        if not line.startswith(' '):
            flush()
            if line.count(' ')!=1 or '\t' in line:raise IFormatError('bad patch identity')
            last,ver=line.split(' ')
            last=decode_ref(last,{})
            group=last.split('/',1)[0]
            if group not in doc.schemas or last not in doc.nodes:raise IFormatError('unknown patch domain')
            if len(ver)>19 or not re.fullmatch(r'[1-9][0-9]*',ver,re.ASCII):raise IFormatError('bad version')
            base=int(ver);fields=doc.schemas[group];changes={}
        else:
            if last is None or not line.startswith(' ') or line.startswith('  '):raise IFormatError('bad patch indentation')
            cols=line[1:].split('\t')
            if len(cols)!=2 or not re.fullmatch(r'0|[1-9][0-9]*',cols[0],re.ASCII):raise IFormatError('bad patch row')
            idx=int(cols[0]);
            if idx>=len(fields) or idx in changes:raise IFormatError('unknown or duplicate patch slot')
            name,typ=fields[idx];changes[idx]=decode(cols[1],typ,{})
    flush()
    if not result:raise IFormatError('no patch domains')
    # Convert positional keys to original schema names only after schema fingerprint verification.
    for c in result:
        group=c.ref.split('/',1)[0]
        c.values={doc.schemas[group][i][0]:v for i,v in c.values.items()}
    return result

def apply_patch(doc,source):return apply(doc,parse_patch(doc,source))
