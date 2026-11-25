import json,hashlib
from pathlib import Path
p=Path("artifacts/ariadne_v144")
r=json.loads((p/"V144_AUDIT.json").read_text())
f=p/r["glb"]
assert f.stat().st_size>200000
assert hashlib.sha256(f.read_bytes()).hexdigest()==r["glb_sha256"]
assert r["actual_official_bone_count"]>70
assert r["weighted_vertex_assignments"]>15000
assert r["ik_target_error_m"]<.2
assert len(r["real_blender_views"])==10
assert all((p/x["png"]).stat().st_size>10000 for x in r["real_blender_views"])
assert not r["target_art_similarity_verified"]
assert not r["correct_palmar_contact_verified"]
print("VALID GLB with baked IK + 10 views; art not approved")
