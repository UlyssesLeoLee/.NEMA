"""Offline CPU rasterization of the distributed actual GLB geometry (NOT a Three.js screenshot).
Usage: python models/render_mesh_preview.py
Requires trimesh, numpy, numba, pillow. Renders matching front and modest angle from GLB.
"""
import sys
from pathlib import Path
import numpy as np, trimesh
from numba import njit
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
S=trimesh.load(ROOT/'website/assets/ariadne-relief-3d.glb',process=False,force='scene')
front=S.geometry['sculpture_front'];tex=np.asarray(front.visual.material.baseColorTexture.convert('RGBA'))
W,H=760,980
# rebuild more simply
VV=np.concatenate([np.asarray(mesh.vertices,dtype=np.float32) for mesh in S.geometry.values()])
I=[];U=[];C=[];T=[];offset=0
for name,mesh in S.geometry.items():
 v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces)
 I.append(f+offset);offset+=len(v)
 kind=0 if name=='sculpture_front' else 2 if name.startswith('skein') or name in ('gold_orb','gold_thread') else 1
 T.extend([kind]*len(f))
 U.append(np.asarray(mesh.visual.uv,dtype=np.float32) if kind==0 else np.zeros((len(v),2),np.float32))
 try: C.append(np.asarray(mesh.visual.vertex_colors,dtype=np.uint8))
 except: C.append(np.tile(np.array([230,221,210,255],dtype=np.uint8),(len(v),1)))
tri=np.concatenate(I).astype(np.int32);UV=np.concatenate(U);COL=np.concatenate(C);TYPE=np.asarray(T,dtype=np.uint8)
print('CPU preview faces',len(tri),'texture',tex.shape)

@njit(cache=True)
def raster(vertices,tri,uv,col,types,texture,canvas,zbuf):
 H,W=canvas.shape[:2]
 light=np.array([-0.28,0.6,0.86],np.float32);light=light/(np.sum(light*light)**.5)
 for k in range(len(tri)):
  a,b,c=tri[k];x0,y0,z0=vertices[a];x1,y1,z1=vertices[b];x2,y2,z2=vertices[c]
  if max(x0,x1,x2)<0 or min(x0,x1,x2)>=W or max(y0,y1,y2)<0 or min(y0,y1,y2)>=H:continue
  ax=int(max(0,min(x0,x1,x2)));bx=int(min(W-1,max(x0,x1,x2)));ay=int(max(0,min(y0,y1,y2)));by=int(min(H-1,max(y0,y1,y2)))
  den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
  if abs(den)<.00002:continue
  # Lighting comes primarily from the baked comic drawing; separate gold meshes get toon bands.
  shade=.96
  if types[k] !=0:
   dx1=x1-x0;dy1=y1-y0;dx2=x2-x0;dy2=y2-y0
   # minor front-biased shading based on depth slope
   side=.25+min(1.0,abs((z0+z1+z2)/3))*1.5
   shade=.83+side*.22
  for yy in range(ay,by+1):
   for xx in range(ax,bx+1):
    px=xx+.5;py=yy+.5
    wa=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/den
    wb=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/den
    wc=1-wa-wb
    if wa<0 or wb<0 or wc<0:continue
    depth=wa*z0+wb*z1+wc*z2
    if depth<=zbuf[yy,xx]:continue
    if types[k]==0:
     uu=wa*uv[a,0]+wb*uv[b,0]+wc*uv[c,0]
     vv=wa*uv[a,1]+wb*uv[b,1]+wc*uv[c,1]
     tx=max(0,min(texture.shape[1]-1,int(uu*(texture.shape[1]-1))))
     ty=max(0,min(texture.shape[0]-1,int(vv*(texture.shape[0]-1))))
     rgba=texture[ty,tx];
     if rgba[3]<36:continue
     for j in range(3):canvas[yy,xx,j]=min(255,int(rgba[j]*shade))
    else:
     for j in range(3):
      cc=wa*col[a,j]+wb*col[b,j]+wc*col[c,j]
      canvas[yy,xx,j]=min(255,int(cc*shade))
    zbuf[yy,xx]=depth

def draw(yaw,label):
 c=np.cos(yaw);s=np.sin(yaw)
 v=VV.copy();v[:,0]=c*VV[:,0]+s*VV[:,2];v[:,2]=-s*VV[:,0]+c*VV[:,2]
 factor=H/7.18
 screen=v.copy();screen[:,0]=W/2+v[:,0]*factor;screen[:,1]=H/2-v[:,1]*factor
 canvas=np.empty((H,W,3),dtype=np.uint8)
 yy,xx=np.indices((H,W));rad=((xx-W*.5)/W)**2+((yy-H*.45)/H)**2
 canvas[:,:,0]=np.clip(14+rad*22,0,255).astype('u1')
 canvas[:,:,1]=np.clip(39+rad*18,0,255).astype('u1')
 canvas[:,:,2]=np.clip(63+rad*12,0,255).astype('u1')
 zbuf=np.full((H,W),-99999.,dtype=np.float32)
 raster(screen,tri,UV,COL,TYPE,tex,canvas,zbuf)
 im=Image.fromarray(canvas)
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((18,19,W-18,79),radius=11,fill=(11,30,49),outline=(183,143,78),width=2)
 d.text((37,36),label,fill=(243,217,157))
 out=ROOT/'previews'/('actual-3d-mesh-'+('front' if yaw==0 else 'angle')+'.png')
 out.parent.mkdir(parents=True,exist_ok=True)
 im.save(out)
 print(out,round(float(np.count_nonzero(zbuf>-9000))/(H*W),3))
if __name__=='__main__':
 draw(0,'ACTUAL GLB MESH / FRONT / CPU RASTER')
 draw(.25,'ACTUAL GLB MESH / 14 DEGREE PARALLAX / CPU RASTER')
