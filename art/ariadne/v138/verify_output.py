import json,hashlib
from pathlib import Path
base=Path("artifacts/ariadne_v138")
report=json.loads((base/"quality_gate.json").read_text())
manifest=json.loads((base/"camera_manifest.json").read_text())
views=manifest["views"]
assert len(views)==266, "266 distinct viewpoint records required"
assert len({(v["azimuth"],v["elevation"]) for v in views})==266
assert all((base/v["image"]).exists() for v in views)
assert all(hashlib.sha256((base/v["image"]).read_bytes()).hexdigest()==v["sha256"] for v in views)
assert report["views_rendered"]==266
assert report["art_similarity_95pct_verified"] is False
assert report["status"]=="ENGINEERING_RENDER_ONLY_ART_BLOCKED"
print("PASS: 266 distinct real renders, checksummed, art approval correctly blocked")
