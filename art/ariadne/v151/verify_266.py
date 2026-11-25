"""Fail closed: validate actual 266 renders, never promote them to art cycles."""
import hashlib,json
from pathlib import Path
p=Path("artifacts/ariadne_v151")
r=json.loads((p/"V151_SPHERE_AUDIT.json").read_text())
assert r["actual_unique_spherical_renders"]==266
assert len(r["records"])==266
assert len({(x["az"],x["el"]) for x in r["records"]})==266
assert r["actual_art_react_cycles"]==0
assert r["required_art_react_cycles_per_view"]==30
assert r["required_total_art_react_cycles"]==7980
assert r["approved_pixel_calibrated_view_count"]==0
assert all(x["real_2d_3d_2d_react_cycles_this_camera"]==0 for x in r["records"])
for x in r["records"]:
 f=p/x["image"]
 assert f.stat().st_size>1500,(str(f),f.stat().st_size)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==x["sha256"]
print("PASS: 266 actual reimported GLB views; 0/7980 qualified art ReAct — release BLOCKED")
