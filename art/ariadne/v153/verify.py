from pathlib import Path
import hashlib,json
p=Path("artifacts/ariadne_v153")
a=json.loads((p/"V153_AUDIT.json").read_text())
g=p/a["one_shared_glb_file"]
assert g.stat().st_size>1500000
assert hashlib.sha256(g.read_bytes()).hexdigest()==a["glb_sha256"]
assert (p/a["editable_blend"]).stat().st_size>100000
assert a["old_garment_objects_discarded"]>=20
assert a["pose_solved_using_true_armature_and_baked_IK"]
assert a["rebuilt_purple_wrap_components"]==3
assert a["rebuilt_white_sculptural_shells"]==2
assert len(a["actual_reimported_glb_views"])==16
assert len(a["actual_face_closeups"])==6
for x in a["actual_reimported_glb_views"]+a["actual_face_closeups"]:
 f=p/x["file"]
 assert f.stat().st_size>2500
 assert hashlib.sha256(f.read_bytes()).hexdigest()==x["sha256"]
assert a["completed_266x30_artist_reacts"]==0
assert a["user_art_approval"] is False
print("V153 REAL GLB VERIFIED 16 FULL VIEWS + 6 FACE CLOSEUPS; art certification BLOCKED")
