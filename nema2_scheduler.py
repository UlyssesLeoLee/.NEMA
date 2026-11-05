"""Deterministic concurrency admission for domain blocks.
uses = read references, touches = write references, depends = hard dependency.
This only plans work; real file writes still require worktree isolation and hash-CAS at merge.
"""
from i_codec import IFormatError

def conflict(a, b, doc):
    def touches(ref):
        read={v for u,v,r in doc.edges if u==ref and r=='uses'}
        write={v for u,v,r in doc.edges if u==ref and r=='touches'}
        return read,write
    ar,aw=touches(a);br,bw=touches(b)
    return bool(aw & (br|bw) or bw & ar)

def ready_batch(doc, candidate_refs, completed=frozenset()):
    """One wave of domains safe to execute in parallel, only among supplied candidates.
    Prior completed dependencies must be explicit; no implicit executing of dependency nodes.
    """
    ids=sorted(set(candidate_refs))
    for ref in ids:
        if ref not in doc.nodes:raise IFormatError('unknown candidate')
    valid=[]
    for ref in ids:
        deps={v for u,v,r in doc.edges if u==ref and r=='depends'}
        if not deps.issubset(completed):continue
        if all(not conflict(ref,other,doc) for other in valid):valid.append(ref)
    return valid
