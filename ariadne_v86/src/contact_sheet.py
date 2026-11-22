#!/usr/bin/env python3
"""Render contact sheet from only actual scene renders; never synthetic art proxies."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
views=ROOT/'output'/'render_24'
files=sorted(views.glob('VIEW_*.png'))
assert [p.stem for p in files]==[f'VIEW_{a:03d}' for a in range(0,360,15)], 'MISSING_REAL_BLENDER_RENDERS'
thumbs=[]
for p in files:
    with Image.open(p) as image:
        im=image.convert('RGB')
        im.thumbnail((320,460))
        thumbs.append(im.copy())
w=max(i.width for i in thumbs);h=max(i.height for i in thumbs)
cols=6;rows=4;label=28
sheet=Image.new('RGB',(cols*w,rows*(h+label)),(231,230,227))
d=ImageDraw.Draw(sheet)
for i,(p,im) in enumerate(zip(files,thumbs)):
    x=i%cols*w;y=i//cols*(h+label)
    sheet.paste(im,(x,y+label));d.text((x+8,y+6),p.stem,fill=(30,28,28))
out=ROOT/'output'/'Ariadne_V86_24View_Engineering_NOT_ART.png'
sheet.save(out,optimize=True)
print('Contact sheet from 24 actual Blender render PNGs:',out)
