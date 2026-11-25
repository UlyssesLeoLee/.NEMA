"""Separate certification action; will reject lack of 7980 non-synthetic cycle artifacts."""
import hashlib,json
from pathlib import Path
root=Path("artifacts/ariadne_v145")
manifest=root/"V145_REACT_LEDGER.json"
if not manifest.exists():
 print("BLOCKED: no real 266x30 art modification ledger")
 raise SystemExit(2)
d=json.loads(manifest.read_text())
assert len(d["views"])==266
seen=set()
for entry in d["views"]:
 k=(entry["azimuth_deg"],entry["elevation_deg"])
 assert k not in seen
 seen.add(k)
 assert len(entry["cycles"])==30
 for i,e in enumerate(entry["cycles"],1):
  assert e["cycle_index"]==i
  for field in ["independent_2d_sha256","corrected_2d_sha256","before_glb_sha256",
                "after_glb_sha256","before_render_sha256","after_render_sha256",
                "geometry_delta","global_regression"]:
   assert e.get(field),f"missing {field}"
  assert e["before_glb_sha256"]!=e["after_glb_sha256"]
  assert e["geometry_delta"]>0
  assert e.get("art_similarity",0)>.95
assert len(seen)==266
assert d.get("human_approved") is True
print("V145 human-approved art certification passes")
