from pathlib import Path
import hashlib,json
p=Path("artifacts/ariadne_v147")
a=json.loads((p/"V147_AUDIT.json").read_text())
g=p/a["new_glb"]
assert g.stat().st_size>150000
assert hashlib.sha256(g.read_bytes()).hexdigest()==a["glb_sha256"]
assert a["legacy_unapproved_art_objects_purged"]>30
assert a["real_official_cc0_armature_count"]>=150
assert a["new_white_gore_panels"]==16
assert a["new_purple_volumetric_panels"]==3
assert a["new_back_braid_strands"]==9
assert a["raised_hand_orb_tangency_error_m"]<.021
assert len(a["new_actual_blender_renders"])==10
for r in a["new_actual_blender_renders"]:
 f=p/r["image"]
 assert f.stat().st_size>10000
 assert hashlib.sha256(f.read_bytes()).hexdigest()==r["sha256"]
assert a["actual_2d_redraw_3d_modify_react_cycles_completed"]==0
assert a["formal_release"] is False
print("V147 rebuilt GLB + 10 actual renders verified; 266x30 and art approval BLOCKED")
