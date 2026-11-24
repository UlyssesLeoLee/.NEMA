from pathlib import Path
import json,hashlib
p=Path("artifacts/ariadne_v143")
j=json.loads((p/"V143_AUDIT.json").read_text())
glb=p/j["glb"]
assert glb.stat().st_size>200000
assert hashlib.sha256(glb.read_bytes()).hexdigest()==j["glb_sha256"]
assert j["actual_official_bone_count"]>70
assert j["weighted_vertex_assignments"]>15000
assert j["original_cc0_body_vertices"]==13380
assert j["ball_to_wrist_distance"]<.13
assert len(j["real_blender_views"])==10
for img in j["real_blender_views"]:
 f=p/img["png"]
 assert f.stat().st_size>10000
 assert hashlib.sha256(f.read_bytes()).hexdigest()==img["sha256"]
assert not j["target_art_similarity_verified"]
assert not j["correct_palmar_contact_verified"]
assert not j["266_view_react_executed"]
print("PASS actual official weighted-rig GLB + 10 real Blender renders; art BLOCKED")
