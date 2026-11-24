"""Optional per-angle 2D comparison. Registered reference evidence is mandatory.
No false pass from numeric manifest entries or self-render data.
Usage: python3 art/ariadne/v142/compare_references.py /path/to/approved/reference_registry.json
JSON registry entries: camera id, approved reference image path, SHA256 and human approval.
Requires independent approved reference assets; absent assets -> BLOCKED.
"""
import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[3]
out=ROOT/"artifacts"/"ariadne_v142"
manifest=json.loads((out/"V142_CAMERA_MANIFEST.json").read_text())
if len(sys.argv)<2:
 print(json.dumps({"status":"BLOCKED","reason":"missing approved reference registry","computed_art_scores":0},indent=2))
 sys.exit(0)
registry_path=Path(sys.argv[1]).resolve()
registry=json.loads(registry_path.read_text())
lookup={(r["azimuth_deg"],r["elevation_deg"]):r for r in registry["references"]}
results=[]
for view in manifest["views"]:
 key=(view["azimuth_deg"],view["elevation_deg"])
 ref=lookup.get(key)
 if not ref or ref.get("approval")!="HUMAN_APPROVED":
  results.append({"azimuth_deg":key[0],"elevation_deg":key[1],"status":"BLOCKED_REFERENCE_MISSING"})
  continue
 art=Path(ref["path"]).resolve()
 if not art.is_file():raise FileNotFoundError(art)
 art_bytes=art.read_bytes()
 actual_art_hash=hashlib.sha256(art_bytes).hexdigest()
 if actual_art_hash!=ref["sha256"]:raise RuntimeError("Art reference hash mismatch")
 if actual_art_hash==view["png_sha256"]:raise RuntimeError("Model self-render cannot be art authority")
 # Pixel correspondence is only valid after explicit matching camera registration.
 if not ref.get("camera_calibration_id") or ref.get("camera_calibration_id")!=view.get("camera_calibration_id"):
  results.append({"azimuth_deg":key[0],"elevation_deg":key[1],"status":"BLOCKED_UNREGISTERED_CAMERA"})
  continue
 img=Image.open(out/view["png"]).convert("RGBA")
 target=Image.open(art).convert("RGBA")
 if img.size!=target.size:raise ValueError("Reference must be calibrated at same pixel dimensions")
 # Diagnostic-only: alpha silhouette IoU. Cannot be 95% multi-component ART score.
 a=img.getchannel("A").point(lambda x:255 if x>=128 else 0)
 b=target.getchannel("A").point(lambda x:255 if x>=128 else 0)
 intersection=ImageChops.multiply(a,b).getbbox()
 from PIL import ImageStat,ImageChops
 inter=ImageStat.Stat(ImageChops.multiply(a,b)).sum[0]/255
 union=ImageStat.Stat(ImageChops.lighter(a,b)).sum[0]/255
 iou=inter/union if union else 0
 results.append({"azimuth_deg":key[0],"elevation_deg":key[1],"status":"DIAGNOSTIC_ONLY","silhouette_iou":iou,"art_95_pass":False})
(out/"V142_REFERENCE_DIAGNOSTICS.json").write_text(json.dumps({"results":results,"art_approved":False},indent=2))
print("Computed diagnostic references:",sum(r["status"]=="DIAGNOSTIC_ONLY" for r in results))
