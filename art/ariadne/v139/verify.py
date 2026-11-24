import json,hashlib
from pathlib import Path
out=Path("artifacts/ariadne_v139")
q=json.loads((out/"quality.json").read_text())
models=list(out.glob("*.glb"))
assert len(models)==1
assert hashlib.sha256(models[0].read_bytes()).hexdigest()==q["model_sha256"]
assert q["vertex_count"]>10000 and q["morph_modified_vertices"]>1000
assert len(q["render_views"])==10
assert all((out/v["file"]).stat().st_size>10000 for v in q["render_views"])
assert all(hashlib.sha256((out/v["file"]).read_bytes()).hexdigest()==v["sha256"] for v in q["render_views"])
assert q["target_pose_completed"] is False and q["art_similarity_gt_95_verified"] is False
assert q["status"]=="ANATOMICAL_FOUNDATION_ONLY_ART_APPROVAL_BLOCKED"
print("PASS: actual official-source round anatomy GLB + 10 PNG renders, art gate remains blocked")
