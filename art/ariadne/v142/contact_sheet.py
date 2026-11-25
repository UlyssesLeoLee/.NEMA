"""Assemble real Blender captures into contact sheet; no generated art."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path("artifacts/ariadne_v142")
views=json.loads((OUT/"V142_CAMERA_MANIFEST.json").read_text())["views"]
key=[(0,0),(45,0),(90,0),(135,0),(180,0),(225,0),(270,0),(315,0),(0,90),(0,-90)]
w,h=384,430
img=Image.new("RGB",(5*w,2*h),(24,26,32));pen=ImageDraw.Draw(img)
for i,(a,e) in enumerate(key):
 ref=next(v for v in views if (v["azimuth_deg"],v["elevation_deg"])==(a,e))
 tile=Image.open(OUT/ref["png"]).convert("RGBA").resize((358,358))
 x=(i%5)*w+12;y=(i//5)*h+12
 bg=Image.new("RGBA",tile.size,(39,41,49,255));bg.alpha_composite(tile)
 img.paste(bg.convert("RGB"),(x,y))
 pen.text((x,y+368),f"GLB CAMERA AZ {a:03d}  EL {e:+04d}",fill=(236,226,207))
img.save(OUT/"V142_REAL_GLB_10VIEW_CONTACT_SHEET.jpg",quality=90)
print("Created true Blender projection contact sheet")
