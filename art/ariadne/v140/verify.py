import hashlib,json
from pathlib import Path
p=Path("artifacts/ariadne_v140")
j=json.loads((p/"V140_AUDIT.json").read_text())
models=list(p.glob("*.glb"))
assert len(models)==1 and models[0].stat().st_size>100000
assert hashlib.sha256(models[0].read_bytes()).hexdigest()==j["glb_sha256"]
assert len(j["rendered_views"])==10
for v in j["rendered_views"]:
 img=p/v["path"]
 assert img.exists() and img.stat().st_size>10000
 assert hashlib.sha256(img.read_bytes()).hexdigest()==v["sha256"]
assert j["source_body_mesh"]>=10000
assert len(j["new_volumetric_nodes"])>15
assert j["art_95_percent_verified"] is False
assert j["status"]=="ENGINEERING_CANDIDATE_ONLY"
print("V140 engineering export verified; formal art approval BLOCKED")
