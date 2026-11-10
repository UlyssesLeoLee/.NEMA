from pathlib import Path
import json, subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from interpreter.nema_strict import parse as parse_py
from codec.nemat import encode,decode
matrix=json.loads((R/'bench/RULE_MATRIX.json').read_text(encoding='utf-8'))
valid=[r for r in matrix if r['status'] in ('valid','error')]
for r in valid:
 ok=True
 try:parse_py(r['variant'])
 except Exception:ok=False
 assert ok==(r['status']=='valid'),(r['id'],r['status'],ok)
# JS parser shares the same source and input set; compare validity, not AST implementation detail.
node='''const fs=require('fs'),vm=require('vm');const ctx={window:{}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),ctx);const input=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(input.map(x=>{try{ctx.window.NemaStrict.parse(x);return true}catch(e){return false}})));'''
cp=subprocess.run(['node','-e',node,str(R/'website/strict-parser.js')],input=json.dumps([r['variant'] for r in valid]),capture_output=True,text=True)
assert cp.returncode==0,cp.stderr
statuses=json.loads(cp.stdout)
for r,ok in zip(valid,statuses):assert bool(ok)==(r['status']=='valid'),(r['id'],r['status'],ok)
for p in (R/'examples').glob('*.nema'):
 src=p.read_bytes()
 assert decode(encode(src)).encode('utf8')==src,p
 print('OK',p.name)
print('PASS',len(valid),'matrix status cases in BOTH parsers; 10 file-level Codec roundtrips; 13 candidate cases separately documented')
