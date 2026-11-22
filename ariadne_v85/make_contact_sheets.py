#!/usr/bin/env python3
"""Assemble evidence from real Blender renders; never replace renders with paintings."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path(__file__).resolve().parent/"output"
def sheet(files,columns,name):
    if not files:raise RuntimeError("NO_RENDER_FILES")
    images=[Image.open(f).convert("RGB") for f in files]
    width,height=images[0].size
    border=36;rows=(len(images)+columns-1)//columns
    dest=Image.new("RGB",(width*columns,(height+border)*rows),(235,232,226))
    draw=ImageDraw.Draw(dest)
    for n,(f,img) in enumerate(zip(files,images)):
        x=(n%columns)*width;y=(n//columns)*(height+border)
        dest.paste(img,(x,y+border))
        draw.text((x+10,y+9),f.stem,fill=(30,30,30))
    dest.save(root/name,optimize=True)
sheet(sorted((root/"render_24").glob("VIEW_*.png")),6,"Ariadne_24View_REAL_Blender_ContactSheet.png")
sheet(sorted((root/"key_views").glob("VIEW_*.png")),3,"Ariadne_6KeyViews_REAL_Blender.png")
print("Real-Blender evidence sheets saved.")
