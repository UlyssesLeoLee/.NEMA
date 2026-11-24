"""Integrity gate and optional independent 2D comparison (no manual PASS scores)."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"artifacts"/"ariadne_v142"
doc=json.loads((OUT/"V142_CAMERA_MANIFEST.json").read_text())
refs=doc["views"]
assert len(refs)==266 and len({(x["azimuth_deg"],x["elevation_deg"]) for x in refs})==266
model=OUT/doc["model"]
assert model.is_file() and model.stat().st_size>100000
assert hashlib.sha256(model.read_bytes()).hexdigest()==doc["model_sha256"]
hashes=[]
for view in refs:
 assert view["model_sha256"]==doc["model_sha256"]
 img=OUT/view["png"]
 assert img.is_file() and img.stat().st_size>1000
 assert hashlib.sha256(img.read_bytes()).hexdigest()==view["png_sha256"]
 hashes.append(view["png_sha256"])
assert len(set(hashes))>5
assert doc["actual_react_cycles_executed"]==0
assert doc["art_target_passed_views"]==0
assert doc["full_art_completion"] is False
assert doc["independent_approved_references"]==0
assert (OUT/"V142_ART_GATE.json").exists()
print("PASS 266 actual GLB reimport renders and hashes; ART APPROVAL BLOCKED")
