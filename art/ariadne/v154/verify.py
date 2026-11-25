from pathlib import Path
import hashlib,json,struct
p=Path("artifacts/ariadne_v154")
a=json.loads((p/"V154_AUDIT.json").read_text())
g=p/a["actual_static_frozen_glb"]
assert g.stat().st_size>1200000
assert hashlib.sha256(g.read_bytes()).hexdigest()==a["actual_glb_sha256"]
assert (p/a["blender_editable_file"]).stat().st_size>100000
assert a["glb_skin_count"]==0
assert a["glb_animation_count"]==0
assert a["true_cc0_baked_anatomy_vertex_count"]>=10000
assert a["old_floating_hair_parts_discarded"]>38
assert a["old_purple_vertical_cloth_panels_discarded"]==3
assert len(a["rendered_from_reimported_glb"])==12
assert len(a["face_views_from_reimported_glb"])==6
for x in a["rendered_from_reimported_glb"]+a["face_views_from_reimported_glb"]:
 f=p/x["file"];assert f.stat().st_size>2500
 assert hashlib.sha256(f.read_bytes()).hexdigest()==x["sha256"]
assert a["completed_266x30_art_react_cycles"]==0
assert a["art_final_approved"] is False
print("V154 FREEZE PASS: true static original CC0 female anatomy, 0 glTF skin/animation, 18 renders")
