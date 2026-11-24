import hashlib,json
from pathlib import Path
p=Path("artifacts/ariadne_v141")
j=json.loads((p/"V141_AUDIT.json").read_text())
glbs=list(p.glob("*.glb"))
assert len(glbs)==1 and glbs[0].stat().st_size>100000
assert hashlib.sha256(glbs[0].read_bytes()).hexdigest()==j["glb_sha256"]
assert j["pose_modified_vertices"]>200
assert len(j["rendered_views"])==10
assert len(j["new_volumetric_nodes"])>25
for item in j["rendered_views"]:
 img=p/item["path"]
 assert img.exists() and img.stat().st_size>10000
 assert hashlib.sha256(img.read_bytes()).hexdigest()==item["sha256"]
assert j["art_95_percent_verified"] is False
assert j["formal_user_approval"] is False
assert "ART_REJECTED" in j["status"]
print("PASS: GLB/render/evidence consistent. ART RELEASE STILL BLOCKED.")
