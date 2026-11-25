"""Fail-closed 266 x 30 art ReAct certification. No synthetic iterations."""
import hashlib,json
from pathlib import Path
out=Path("artifacts/ariadne_v145")
q=json.loads((out/"V145_AUDIT.json").read_text())
file=out/q["glb"]
assert file.stat().st_size>200000
assert hashlib.sha256(file.read_bytes()).hexdigest()==q["glb_sha256"]
assert len(q["actual_renders"])==10
assert all((out/r["image"]).stat().st_size>10000 for r in q["actual_renders"])
assert all(hashlib.sha256((out/r["image"]).read_bytes()).hexdigest()==r["sha256"] for r in q["actual_renders"])
geo=q["actual_mesh_corrections"]
assert geo["orb_to_skinned_anatomy_tangency_gap_m"]<.016
assert geo["gold_thread_endpoint_updates"]>=1
assert len(geo["unsupported_mantle_objects_removed"])>=2
assert geo["new_3d_mantle_panels"]==2
assert q["actually_completed_true_art_react_cycles"]==0
assert q["art_95_percent_verified"] is False
print("ENGINEERING MODEL CORRECTION: PASS. 7980-CYCLE ART CERTIFICATION: BLOCKED.")
