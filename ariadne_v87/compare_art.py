"""Engineering comparison against independent historical 24-frame silhouette masks.

Photographic camera registration is UNKNOWN; normalized IoU is diagnostic only,
never release evidence. Never derives a target from current 3D output.
"""
import json,base64,zlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
data=json.loads((ROOT/'guides/independent_art_masks24.json').read_text())
result=[]
for entry in data['frames']:
    w,h=entry['mask_size_px']
    raw=zlib.decompress(base64.b64decode(entry['mask_1bit_zlib_base64']))
    if len(raw)!=((w+7)//8)*h:raise ValueError('corrupt reference silhouette')
    bits=[]
    for b in raw:
        bits.extend(255 if b & (1<<(7-bit)) else 0 for bit in range(8))
    original=Image.frombytes('L',(w,h),bytes(bits[:w*h]))
    actual=Image.open(OUT/'render_24'/f"VIEW_{entry['angle_deg']:03d}.png").convert('RGBA').getchannel('A')
    # Camera match not independently known. Resize only for rough engineering diagnostic.
    actual=actual.resize((w,h),Image.Resampling.NEAREST)
    ma=original.point(lambda x:255 if x>=128 else 0)
    mb=actual.point(lambda x:255 if x>=128 else 0)
    a=ma.tobytes();b=mb.tobytes()
    inter=sum(bool(x) and bool(y) for x,y in zip(a,b));union=sum(bool(x) or bool(y) for x,y in zip(a,b))
    result.append({'angle_deg':entry['angle_deg'],'rough_mask_iou':round(inter/union,4) if union else 0.,'camera_registered':False,'art_approved':False})
report={'kind':'ENGINEERING_DIAGNOSTIC_NOT_RELEASE','independent_source':'historical V18 24 art files (art_*png)','camera_registered':False,
        'per_view':result,'mean_rough_iou':round(sum(x['rough_mask_iou'] for x in result)/24,4),'all_24_art_pass':False}
(OUT/'art_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'mean_rough_iou':report['mean_rough_iou'],'release_approved':False}))
