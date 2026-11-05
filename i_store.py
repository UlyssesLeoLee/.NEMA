"""SQLite WAL CAS store: isolated independent domain commits, durable audit log."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from i_codec import Document, Conflict, IFormatError, validate_type, Node

DDL='''
CREATE TABLE IF NOT EXISTS schemas (group_id TEXT PRIMARY KEY, spec TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nodes (ref TEXT PRIMARY KEY, group_id TEXT NOT NULL, local_id TEXT NOT NULL, rev INTEGER NOT NULL, values_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS edges (src TEXT NOT NULL, dst TEXT NOT NULL, relation TEXT NOT NULL, PRIMARY KEY(src,dst,relation));
CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT NOT NULL, ref TEXT NOT NULL, rev_before INTEGER NOT NULL, rev_after INTEGER NOT NULL);
'''

class DomainStore:
    def __init__(self,path):
        self.path=str(path)
        conn=self.connect()
        try: conn.executescript(DDL);conn.commit()
        finally:conn.close()

    def connect(self):
        conn=sqlite3.connect(self.path,timeout=20,isolation_level=None)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=20000')
        return conn

    def load_initial(self,doc:Document):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT 1 FROM nodes LIMIT 1').fetchone():raise Conflict('store is already initialized')
            for group,schema in doc.schemas.items():
                c.execute('INSERT INTO schemas VALUES (?,?)',(group,json.dumps(schema,ensure_ascii=False)))
            for node in doc.nodes.values():
                c.execute('INSERT INTO nodes VALUES (?,?,?,?,?)',(node.ref,node.group,node.local_id,node.rev,json.dumps(node.values,ensure_ascii=False)))
            for a,b,rel in doc.edges:c.execute('INSERT INTO edges VALUES (?,?,?)',(a,b,rel))
            c.commit()
        except Exception:c.rollback();raise
        finally:c.close()

    def edit_many(self,edits: list[tuple[str,int,dict]],actor:str):
        """Atomic CAS. Distinct domains may commit independently at any time.
        Writers serialize briefly under SQLite, but there is no document-wide revision gate.
        """
        if not actor or len(actor)>128:raise IFormatError('invalid actor')
        if len({ref for ref,_,_ in edits})!=len(edits):raise Conflict('duplicate ref in batch')
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            schemas={g:dict(json.loads(raw)) for g,raw in c.execute('SELECT group_id,spec FROM schemas')}
            for ref,base,values in edits:
                row=c.execute('SELECT group_id, rev, values_json FROM nodes WHERE ref=?',(ref,)).fetchone()
                if row is None or row[1]!=base:raise Conflict('missing or stale domain')
                g,rev,existing=row
                if not values:raise IFormatError('empty edit')
                for key,value in values.items():
                    if key not in schemas[g]:raise IFormatError('unknown field')
                    validate_type(value,schemas[g][key])
                merged=json.loads(existing);merged.update(values)
                updated=c.execute('UPDATE nodes SET rev=?,values_json=? WHERE ref=? AND rev=?',
                                  (rev+1,json.dumps(merged,ensure_ascii=False),ref,rev))
                if updated.rowcount!=1:raise Conflict('concurrent change')
                c.execute('INSERT INTO audit(actor,ref,rev_before,rev_after) VALUES(?,?,?,?)',(actor,ref,rev,rev+1))
            c.commit()
        except Exception:
            c.rollback(); raise
        finally: c.close()

    def read(self,ref):
        c=self.connect()
        try:
            row=c.execute('SELECT group_id,local_id,rev,values_json FROM nodes WHERE ref=?',(ref,)).fetchone()
            return None if row is None else Node(row[0],row[1],row[2],json.loads(row[3]))
        finally:c.close()

    def snapshot(self):
        d=Document();c=self.connect()
        try:
            d.schemas={g:[tuple(pair) for pair in json.loads(schema)] for g,schema in c.execute('SELECT group_id,spec FROM schemas')}
            for g,local,rev,values in c.execute('SELECT group_id,local_id,rev,values_json FROM nodes'):
                d.add(g,local,json.loads(values),rev)
            for a,b,rel in c.execute('SELECT src,dst,relation FROM edges'):d.link(a,b,rel)
            return d
        finally:c.close()

    def audit_count(self):
        c=self.connect()
        try:return c.execute('SELECT COUNT(*) FROM audit').fetchone()[0]
        finally:c.close()
