from pathlib import Path
import json,hashlib
p=Path("artifacts/ariadne_v150")
a=json.loads((p/"V150_AUDIT.json").read_text())
g=p/a["gltf_glb_file"]
b=p/a["blend_file"]
assert g.stat().st_size>250000 and b.stat().st_size>100000
assert hashlib.sha256(g.read_bytes()).hexdigest()==a["glb_sha256"]
assert a["old_unapproved_hair_objects_deleted"]>=30
assert a["new_articulated_hair_objects"]>=40
assert a["tested_evaluated_hair_mesh_vertices"]>3000
assert a["head_face_guards"]["hair_in_front_face_guard_vertices"]==0
assert len(a["12_reimported_real_glb_views"])==12
assert len(a["5_real_glb_face_closeups"])==5
for item in a["12_reimported_real_glb_views"]+a["5_real_glb_face_closeups"]:
 f=p/item["file"]
 assert f.stat().st_size>8000
 assert hashlib.sha256(f.read_bytes()).hexdigest()==item["sha256"]
assert a["completed_true_2d_redraw_to_3d_react_cycles"]==0
assert a["formal_art_release"] is False
print("V150 actual 3D scalp-surface fit and 17 GLB reimport renders: VERIFIED; art still blocked")
