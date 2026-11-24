#!/usr/bin/env python3
"""Ariadne V123 full CC0 rig: V122.2 adversarial repair, bilateral gesture, multi-contact and real high-angle checks.
Scientific/engineering candidate, NOT approved against independent V20 art anchors.
"""
import bpy, math, json, os, pathlib, hashlib
import numpy as np
from mathutils import Vector
from math import sin,cos,pi,sqrt
R=pathlib.Path(os.environ.get("GITHUB_WORKSPACE",pathlib.Path(__file__).resolve().parents[2]))
IN=R/"ariadne_v129"/"input"; OUT=R/"ariadne_v129"/"output";OUT.mkdir(parents=True,exist_ok=True)
for name in ("base.obj","caucasian-female-young.target","default.mhskel","default_weights.mhw"):
    assert (IN/name).is_file() and (IN/name).stat().st_size>100000, ("MISSING_OFFICIAL_ASSET",name)
sk=json.loads((IN/"default.mhskel").read_text())
wt=json.loads((IN/"default_weights.mhw").read_text())
assert len(sk["bones"])==163 and sk["license"]==wt["license"]=="CC0"
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
def clamp(x,a,b):return max(a,min(b,x))
def vec(*args):return Vector(args)
def norm(x):
 v=Vector(x);return v.normalized() if v.length>1e-9 else Vector((0,0,1))
def newmat(name,color,metal=0,rough=.55):
 m=bpy.data.materials.new(name);m.use_nodes=True
 m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*color,1)
 bs.inputs["Metallic"].default_value=metal
 bs.inputs["Roughness"].default_value=rough
 return m
ivory=newmat("Ancient_Ivory_Marble",(.79,.73,.63))
chiton_mat=newmat("Royal_Crete_Chiton_Limestone",(.85,.77,.62))
himation_mat=newmat("Royal_Sculpted_Himation",(.74,.67,.56))
hair_mat=newmat("Marble_Hair_Carving",(.69,.63,.53))
gold=newmat("Gold_Ariadne_Thread",(.8,.48,.11),.83,.26)
base_mat=newmat("Basalt_Pedestal",(.45,.43,.42))
def meshobj(name,points,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(points,[],faces);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 o.data.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 return o
def lineobj(name,points,thickness,mat):
 cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D";cu.bevel_depth=thickness;cu.bevel_resolution=4
 sp=cu.splines.new("POLY");sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 return o
def sphere(name,pos,r,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,radius=r,location=pos)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat);return o
# Official MakeHuman source is Y-up; Blender is Z-up with front -Y.
verts=[]
for line in (IN/"base.obj").open():
 if line.startswith("v "):
  x,y,z=map(float,line.split()[1:4]);verts.append([x/10,-z/10,y/10])
verts=np.asarray(verts,dtype=np.float64)
assert len(verts)==19158
for line in (IN/"caucasian-female-young.target").open():
 t=line.split()
 if len(t)==4 and t[0].isdigit():
  k=int(t[0]);dx,dy,dz=map(float,t[1:])
  verts[k]+=np.array([dx/10,-dz/10,dy/10])
z0=float(verts[:13380,2].min());verts[:,2]-=z0
g=None;faces=[]
for line in (IN/"base.obj").open():
 if line.startswith("g "):g=line.strip()[2:]
 elif line.startswith("f ") and g=="body":
  faces.append(tuple(int(q.split("/")[0])-1 for q in line.split()[1:]))
assert len(faces)==13378 and max(max(f) for f in faces)<13380
body=meshobj("01_OFFICIAL_MAKEHUMAN_CC0_FEMALE",verts[:13380].tolist(),faces,ivory)
body["license"]="MakeHuman CC0";body["geometry_source"]="official base.obj + macrodetails female young target"
# Create actual source bone transforms from the official indexed topology,
# never from an approximate Rigify metarig.
jointpoints={}
for key,ids in sk["joints"].items():
 jointpoints[key]=Vector(np.mean(verts[np.asarray(ids,dtype=int)],axis=0).tolist())
armdata=bpy.data.armatures.new("OFFICIAL_163_BONE_REST")
rig=bpy.data.objects.new("Ariadne_Official_CC0_163_Bone_Rig",armdata)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for name,info in sk["bones"].items():
 bone=armdata.edit_bones.new(name)
 h=jointpoints[info["head"]];t=jointpoints[info["tail"]]
 if (t-h).length<0.001:
  t=h+Vector((0,.005,0))
 bone.head=h;bone.tail=t;bone.use_deform=True
for name,info in sk["bones"].items():
 parent=info.get("parent")
 if parent and parent in armdata.edit_bones:
  armdata.edit_bones[name].parent=armdata.edit_bones[parent]
# Define source anatomical roll based on official bone rotation planes.
for name,info in sk["bones"].items():
 refs=sk["planes"].get(info.get("rotation_plane"),[])
 if len(refs)==3 and all(r in jointpoints for r in refs):
  p,q,r=(jointpoints[j] for j in refs)
  n=(q-p).cross(r-p)
  if n.length>.0001:
   try:armdata.edit_bones[name].align_roll(n.normalized())
   except Exception:pass
bpy.ops.object.mode_set(mode="OBJECT")
# Bind every official source index+weight. These are NOT historical Rigify weights.
valid_weights={};totals=np.zeros(13380,dtype=np.float64)
for name,entries in wt["weights"].items():
 selected=[(int(i),float(w)) for i,w in entries if 0<=int(i)<13380 and float(w)>.0009]
 valid_weights[name]=selected
 for i,w in selected:totals[i]+=w
assert np.min(totals)>.9,("ZERO_WEIGHT_BODY_VERTICES",int(np.sum(totals<.9)))
for name,entries in valid_weights.items():
 vg=body.vertex_groups.new(name=name)
 for i,w in entries:vg.add([i],float(w/totals[i]),"REPLACE")
skin=body.modifiers.new("OFFICIAL_MAKEHUMAN_LBS_SKIN","ARMATURE")
skin.object=rig;skin.use_vertex_groups=True;skin.use_bone_envelopes=False
# DQS preserves cylindrical forearm cross-section during pronation/supination.
skin.use_deform_preserve_volume=True
def official_weight_audit():
 out={}
 for side in ("L","R"):
  names=["lowerarm01","lowerarm02","wrist"]+[f"finger{i}-{n}" for i in range(1,6) for n in range(1,4)]
  out[side]={name:{"sum":round(sum(w/totals[i] for i,w in valid_weights.get(f"{name}.{side}",[])),5),
                   "vertices":len(valid_weights.get(f"{name}.{side}",[]))}
             for name in names}
  assert all(v["sum"]>3 and v["vertices"]>10 for v in out[side].values()),out[side]
 return out
skin_audit=official_weight_audit()
print("OFFICIAL_SKIN_FULL_FINGER_FOREARM_AUDIT",json.dumps(skin_audit),flush=True)
# K-shaped royal sculpture. Angles are actual local joint rotations with joint
# types explicit; forearm pronation/supination distributed across two bones.
params=[
 ("shoulder01.L",0,-.5,.5),("shoulder01.L",2,-.65,.65),
 ("upperarm01.L",0,-1.1,1.1),("upperarm01.L",2,-1.15,1.15),
 ("upperarm02.L",0,-.65,.65),("upperarm02.L",2,-.75,.75),
 ("lowerarm01.L",0,-1.5,1.5),("lowerarm01.L",2,-1.2,1.2),
 ("FOREARM_ROLL",1,-1.57,1.57),
 ("wrist.L",0,-.45,.45),("wrist.L",2,-.45,.45),
 ("shoulder01.L",1,-.55,.55),
 ("upperarm01.L",1,-.92,.92),
 ("upperarm02.L",1,-.65,.65),
 ("wrist.L",1,-.38,.38)]
lower=np.asarray([a for _,_,a,b in params]);upper=np.asarray([b for _,_,a,b in params])
def boneset(x):
 for nm in ("shoulder01.L","upperarm01.L","upperarm02.L","lowerarm01.L","lowerarm02.L","wrist.L"):
  pb=rig.pose.bones[nm];pb.rotation_mode="XYZ";pb.rotation_euler=(0,0,0)
 for i,(name,axis,lo,hi) in enumerate(params):
  if name=="FOREARM_ROLL":
   rig.pose.bones["lowerarm01.L"].rotation_euler.y=float(x[i])*.58
   rig.pose.bones["lowerarm02.L"].rotation_euler.y=float(x[i])*.42
  else:rig.pose.bones[name].rotation_euler[axis]=float(x[i])
 bpy.context.view_layer.update()
def bhead(name):return rig.pose.bones[name].head.copy()
def btail(name):return rig.pose.bones[name].tail.copy()
def landmarks():
 w=bhead("wrist.L")
 e=bhead("lowerarm01.L")
 index=bhead("finger2-1.L");pinky=bhead("finger5-1.L")
 knuckle=np.mean([np.array(bhead(f"finger{i}-1.L")) for i in (2,3,4,5)],axis=0)
 fingertip=btail("finger3-3.L")
 along=fingertip-w
 transverse=index-pinky
 # V124 independent 2D palmar-vs-dorsal correction: the old cross
 # PRODUCT WAS THE DORSAL HALF-SPACE despite having world-Z positive.
 # This false label let dorsal skin vertices cradle the ball. Reverse
 # tangent basis using actual anatomical LEFT thumb/index/little mapping.
 up=along.cross(transverse)
 if up.length<.0001:raise RuntimeError("PALM_NORMAL_DEGENERATE")
 up.normalize()
 # Reference: hand-authored TOP2D_LEFT_PALM_UP_AUTHOR_TARGET.svg,
 # calibrated anatomical left: thumb-side index and palm creases visible.
 # This is explicitly provisional 2D, not user-approved V20 art.
 palm=Vector((.24*w.x+.76*knuckle[0],.24*w.y+.76*knuckle[1],.24*w.z+.76*knuckle[2]))
 return e,w,palm,up
target_elbow=np.array([.32,-.16,1.255])
target_wrist=np.array([.465,-.20,1.50])
target_palm=np.array([.495,-.21,1.535])
target_up=Vector((.03,-.07,.997)).normalized()
def residual(x):
 boneset(x);e,w,p,n=landmarks()
 r=np.concatenate([
  (np.array(e)-target_elbow)/.17,
  (np.array(w)-target_wrist)/.15,
  (np.array(p)-target_palm)/.13,
  (np.array(n)-np.array(target_up))*3.5,
  x*.19,
  np.array([x[8]*.11])
 ])
 return r
x=np.zeros(len(params)); best=(1e9,x.copy()); lamb=.05
for k in range(120):
 r=residual(x);cost=float(r@r)
 if cost<best[0]:best=(cost,x.copy())
 J=np.zeros((len(r),len(x)))
 for i in range(len(x)):
  xx=x.copy();xx[i]+=.006
  J[:,i]=(residual(xx)-r)/.006
 a=J.T@J + lamb*np.eye(len(x))
 step=np.linalg.lstsq(a,-J.T@r,rcond=None)[0]
 trial=np.clip(x+np.clip(step,-.22,.22),lower,upper)
 trialcost=float(residual(trial)@residual(trial))
 if trialcost<cost: x=trial; lamb=max(.004,lamb*.72)
 else:lamb=min(2.,lamb*2.5)
 if np.linalg.norm(step)<.0005:break
if float(residual(x)@residual(x))<best[0]:best=(float(residual(x)@residual(x)),x.copy())
boneset(best[1])
# Pose finger curl gently around an orb. These are source-specific joints with
# proven source weights, and remain small to avoid tendon distortion.
for finger in range(2,6):
 for seg,angle in ((1,.10),(2,.17),(3,.10)):
  pb=rig.pose.bones[f"finger{finger}-{seg}.L"]
  pb.rotation_mode="XYZ";pb.rotation_euler.x=angle
for seg,angle in ((1,.10),(2,-.09),(3,.04)):
 pb=rig.pose.bones[f"finger1-{seg}.L"]
 pb.rotation_mode="XYZ";pb.rotation_euler.x=angle
bpy.context.view_layer.update()
elbow,wrist,palm,palm_normal=landmarks()
palm_dot=float(palm_normal.dot(Vector((0,0,1))))
print("OFFICIAL_ARM_SOLVE",json.dumps({"elbow":list(elbow),"wrist":list(wrist),"palm":list(palm),"normal":list(palm_normal),"up_dot":palm_dot,"pose":best[1].tolist()}),flush=True)
if palm_dot<.82:raise RuntimeError("P0_LEFT_PALM_NOT_UP")
if elbow.z>1.56 or elbow.z<.95 or wrist.z<1.30:raise RuntimeError("P0_FOREARM_POSE_OUTSIDE_ANATOMICAL_SCENE")
# P03/P06: free anatomical RIGHT hand must be an independent anatomical
# solver, not the unchanged A-pose. References are not yet independently
# approved, so these targets can only produce an engineering candidate.
right_params=[
 ("shoulder01.R",0,-.38,.38),("shoulder01.R",2,-.55,.55),
 ("upperarm01.R",0,-.85,.85),("upperarm01.R",2,-1.05,1.05),
 ("upperarm02.R",0,-.48,.48),
 ("lowerarm01.R",0,-1.20,1.20),("lowerarm01.R",2,-.85,.85),
 ("wrist.R",0,-.42,.42),("wrist.R",2,-.35,.35)]
right_lower=np.array([p[2] for p in right_params])
right_upper=np.array([p[3] for p in right_params])
right_names={nm for nm,_,_,_ in right_params}
def set_right(xx):
 for name in right_names:
  pb=rig.pose.bones[name];pb.rotation_mode="XYZ";pb.rotation_euler=(0,0,0)
 for k,(name,axis,lo,hi) in enumerate(right_params):
  rig.pose.bones[name].rotation_euler[axis]=float(xx[k])
 bpy.context.view_layer.update()
def right_landmark():
 e=np.asarray(rig.pose.bones["lowerarm01.R"].head)
 w=np.asarray(rig.pose.bones["wrist.R"].head)
 k=np.mean([np.asarray(rig.pose.bones[f"finger{a}-1.R"].head) for a in (2,3,4,5)],axis=0)
 return e,w,k
right_e=np.array([-.35,-.12,1.05]);right_w=np.array([-.50,-.16,.805])
right_k=np.array([-.54,-.195,.78])
right_pose=np.zeros(len(right_params))
right_best=(1.e12,right_pose.copy());right_lambda=.08
for _itr in range(58):
 set_right(right_pose);ee,ww,kk=right_landmark()
 rv=np.r_[(ee-right_e)/.18,(ww-right_w)/.13,(kk-right_k)/.20,right_pose*.20]
 sc=float(rv@rv)
 if sc<right_best[0]:right_best=(sc,right_pose.copy())
 jac=np.zeros((len(rv),len(right_pose)))
 for j in range(len(right_pose)):
  t=right_pose.copy();t[j]+=.006;set_right(t)
  a,b,c=right_landmark()
  val=np.r_[(a-right_e)/.18,(b-right_w)/.13,(c-right_k)/.20,t*.20]
  jac[:,j]=(val-rv)/.006
 step=np.linalg.lstsq(jac.T@jac+right_lambda*np.eye(len(t)),-jac.T@rv,rcond=None)[0]
 trial=np.clip(right_pose+np.clip(step,-.12,.12),right_lower,right_upper)
 set_right(trial);a,b,c=right_landmark()
 val=np.r_[(a-right_e)/.18,(b-right_w)/.13,(c-right_k)/.20,trial*.20]
 if float(val@val)<sc:right_pose=trial.copy();right_lambda=max(.005,right_lambda*.75)
 else:right_lambda=min(3.,right_lambda*2)
 if np.linalg.norm(step)<.002:break
set_right(right_best[1])
# Articulated individual fingers (no joined mitten), conservative curl.
for finger in range(1,6):
 for segment in range(1,4):
  pb=rig.pose.bones[f"finger{finger}-{segment}.R"]
  pb.rotation_mode="XYZ"
  pb.rotation_euler.x=float((.08,.12,.055)[segment-1])
  pb.rotation_euler.z=float((finger-3)*.019 if segment==1 else 0)
bpy.context.view_layer.update()
right_final=right_landmark()
right_target_error=float(np.linalg.norm(right_final[1]-right_w))
right_pose_changed=bool(np.linalg.norm(right_best[1])>.08)
print("V129_RIGHT_GESTURE_ENGINEERING",json.dumps({
 "9dof":right_best[1].tolist(),
 "elbow":right_final[0].tolist(),"wrist":right_final[1].tolist(),
 "fingers_center":right_final[2].tolist(),
 "right_target_error_m":right_target_error,
 "right_pose_changed":right_pose_changed,
 "independent_right_art_reference":False}),flush=True)
# Check actual deform evaluated skin deformation and no extreme collapse.
def evaluated_body():
 dg=bpy.context.evaluated_depsgraph_get()
 ev=body.evaluated_get(dg);me=ev.to_mesh()
 a=np.array([list(ev.matrix_world @ vert.co) for vert in me.vertices])
 ev.to_mesh_clear()
 return a
actual=evaluated_body()
rest=np.asarray([list(body.matrix_world @ v.co) for v in body.data.vertices])
disp=np.linalg.norm(actual-rest,axis=1)
assert np.max(disp)>.025 and np.all(np.isfinite(actual))
# Adversarial forearm deformation audit: do not let IK fit sacrifice arm
# cylindrical continuity to move an orb. Search small physically meaningful
# reductions in anatomical roll, elbow bend and wrist flexion and KEEP the
# palm-up constraint.  Do not lower the acceptance threshold.
edge_region=set(i for name in ("lowerarm01.L","lowerarm02.L") for i,w in valid_weights[name] if w/totals[i]>.35)
audit_edges=set()
for f in faces:
 if len(edge_region.intersection(f))>=3:
  for i in range(len(f)):
   a,b=int(f[i]),int(f[(i+1)%len(f)])
   audit_edges.add((min(a,b),max(a,b)))
audit_edges=sorted(audit_edges)
ix=np.asarray([e[0] for e in audit_edges],dtype=int)
iy=np.asarray([e[1] for e in audit_edges],dtype=int)
rest_edge=np.linalg.norm(rest[ix]-rest[iy],axis=1)
good_edges=rest_edge>1e-5;ix=ix[good_edges];iy=iy[good_edges];rest_edge=rest_edge[good_edges]
assert len(ix)>=200
seed=best[1].copy()
candidates=[]
for roll_fraction in (1,.88,.75,.62,.50,.38,.25,.13,0):
 for elbow_fraction in (1,.93,.84,.75):
  for wrist_fraction in (1,.85,.70):
   cc=seed.copy();cc[8]*=roll_fraction;cc[6]*=elbow_fraction;cc[9]*=wrist_fraction
   boneset(cc)
   ee,ww,pp,nn=landmarks()
   up=float(nn.z)
   arr=evaluated_body()
   ratio=np.linalg.norm(arr[ix]-arr[iy],axis=1)/rest_edge
   q02=float(np.quantile(ratio,.02));q98=float(np.quantile(ratio,.98))
   err=float(np.linalg.norm(np.asarray(ww)-target_wrist)+np.linalg.norm(np.asarray(ee)-target_elbow))
   severe=int(np.sum(ratio<.50))
   accepted=(up>=.82 and q02>=.65 and q98<=1.6 and severe==0 and err<.24)
   score=err+.23*np.linalg.norm(cc-seed)+8*max(0,.82-up)+8*max(0,.65-q02)+.22*severe
   candidates.append((not accepted,score,q02,q98,up,err,cc,arr,severe))
candidates.sort(key=lambda x:(x[0],x[1]))
choice=candidates[0]
print("V129_ADVERSARIAL_FOREARM_SELECTION",json.dumps({
 "tested":len(candidates),"valid":sum(1 for c in candidates if not c[0]),
 "selected":{"p02_edge_ratio":choice[2],"p98_edge_ratio":choice[3],
 "palm_up_dot":choice[4],"elbow_wrist_error_m":choice[5],
 "severe_edges_below_half":choice[8],
 "pose":choice[6].tolist()},"P0_pass":not choice[0]}),flush=True)
forearm_candidate_p0=not choice[0]
if choice[0]: print("P0_FOREARM_ZERO_SEVERE_GATE_FAIL: retain only engineering candidate",flush=True)
boneset(choice[6]);actual=evaluated_body()
elbow,wrist,palm,palm_normal=landmarks();palm_dot=float(palm_normal.z)
disp=np.linalg.norm(actual-rest,axis=1)
assert palm_dot>=.82 and float(np.max(disp))>.025
# V122.2 mandatory BILATERAL audit: original V123 trial improved LEFT but
# independently detected FOUR collapsed RIGHT forearm edges (<0.5). Right
# artistic pose must be re-solved under the same strict edge/volume gate.
right_fids=set(i for name in ("lowerarm01.R","lowerarm02.R")
 for i,w in valid_weights[name] if w/totals[i]>.35)
right_edges=set()
for f in faces:
 if len(right_fids.intersection(f))>=3:
  for j in range(len(f)):
   a,b=int(f[j]),int(f[(j+1)%len(f)])
   right_edges.add((min(a,b),max(a,b)))
right_edges=sorted(right_edges)
rix=np.asarray([e[0] for e in right_edges],dtype=int)
riy=np.asarray([e[1] for e in right_edges],dtype=int)
rr0=np.linalg.norm(rest[rix]-rest[riy],axis=1)
rkeep=rr0>1e-5;rix=rix[rkeep];riy=riy[rkeep];rr0=rr0[rkeep]
assert len(rix)>=200
right_seed=right_best[1].copy()
right_trials=[]
for f_forearm in (1.,.88,.74,.60,.45,.30,.16,0):
 for f_wrist in (1.,.82,.62,.40):
  for f_upper in (1.,.85,.67):
   t=right_seed.copy()
   t[5:7]*=f_forearm;t[7:9]*=f_wrist;t[4]*=f_upper
   set_right(t)
   tri=evaluated_body()
   rr=np.linalg.norm(tri[rix]-tri[riy],axis=1)/rr0
   q02=float(np.quantile(rr,.02));q98=float(np.quantile(rr,.98))
   nsev=int(np.sum(rr<.5))
   re,rw,rh=right_landmark()
   err=float(np.linalg.norm(rw-right_w))
   safe=bool(nsev==0 and q02>=.65 and q98<=1.6 and err<.14
             and np.linalg.norm(t)>.08)
   score=float(err+.19*np.linalg.norm(t-right_seed)
     +.20*nsev+8*max(0,.65-q02))
   right_trials.append((not safe,score,nsev,q02,q98,err,t))
right_trials.sort(key=lambda item:(item[0],item[1]))
rchoice=right_trials[0];set_right(rchoice[6])
right_final=right_landmark()
right_target_error=float(np.linalg.norm(right_final[1]-right_w))
right_pose_changed=bool(np.linalg.norm(rchoice[6])>.08)
right_forearm_quality={
 "unique_edges":len(rix),"p02_edge_ratio":rchoice[3],
 "p98_edge_ratio":rchoice[4],
 "severe_edges_below_0p5":rchoice[2],
 "wrist_target_error_m":rchoice[5],
 "accepted_zero_severe":not rchoice[0],
 "search_candidates":len(right_trials),
 "valid_pose_count":sum(1 for item in right_trials if not item[0])}
actual=evaluated_body()
print("V129_RIGHT_FOREARM_P0_96_TRIAL_REPAIR",json.dumps(right_forearm_quality),flush=True)
# If no acceptable right pose exists, the candidate may be archived for
# diagnosis but cannot be marked ANATOMY_PASS or released as finished.
# Palm support surface must be actual official wrist and metacarpal semantic patch,
# NOT an arbitrary x/y/z bounding box.
palm_ids=set()
for name in ["wrist.L","metacarpal1.L","metacarpal2.L","metacarpal3.L","metacarpal4.L"]:
 palm_ids.update(i for i,w in valid_weights.get(name,[]) if w/totals[i]>.25)
palm_ids=sorted(palm_ids)
assert len(palm_ids)>80
# Source-rest palmar normal is NOT the earlier dorsal cross-product.
def rest_joint(bone,end="head"):
 return jointpoints[sk["bones"][bone][end]].copy()
rest_w=rest_joint("wrist.L");rest_i=rest_joint("finger2-1.L")
rest_l=rest_joint("finger5-1.L");rest_f=rest_joint("finger3-3.L","tail")
rest_palmar_normal=(rest_f-rest_w).cross(rest_i-rest_l).normalized()
# Two distinct anatomical surface classes on actual CC0 rest skin:
# the normal from rest CC0 topology separates palm from back of hand.
# No mesh vertices are fabricated or reindexed.
palmar_ids=sorted(i for i in palm_ids
 if body.data.vertices[i].normal.dot(rest_palmar_normal)>.35)
dorsal_ids=sorted(i for i in palm_ids
 if body.data.vertices[i].normal.dot(rest_palmar_normal)<-.35)
assert len(palmar_ids)>=55 and len(dorsal_ids)>=55, (
 "INSUFFICIENT_PALMAR_DORSAL_SOURCE_SURFACE_IDS",
 len(palmar_ids),len(dorsal_ids))
palm_all_ids=palm_ids
palm_ids=palmar_ids
palmpoints=actual[palm_ids]
# Top-orthographic self-occlusion audit: palmar surface must be ABOVE
# dorsal shell for coinciding XY positions, not merely wrist direction.
def top_surface_side_audit(positions):
 pal=positions[palmar_ids];dor=positions[dorsal_ids]
 diffs=[]
 for xyz in pal:
  xy=np.linalg.norm(dor[:,:2]-xyz[:2],axis=1)
  k=int(np.argmin(xy))
  if xy[k]<.017:diffs.append(float(xyz[2]-dor[k,2]))
 vals=np.asarray(diffs,dtype=float)
 if len(vals)<12:
  return {"matched_pairs":int(len(vals)),"positive_fraction":0.,
          "median_palmar_above_dorsal_mm":-999.,
          "reason":"TOP2D_SURFACE_CORRESPONDENCE_INSUFFICIENT"}
 return {"matched_pairs":len(vals),
  "positive_fraction":float(np.mean(vals>.002)),
  "median_palmar_above_dorsal_mm":float(np.median(vals)*1000),
  "minimum_signed_difference_mm":float(np.min(vals)),
  "top_palmar_side_visible_by_depth":bool(np.mean(vals>.002)>=.70
     and np.median(vals)>=.003)}
top2d_surface_audit=top_surface_side_audit(actual)
print("V129_TOP2D_PALMAR_NOT_DORSAL_SOURCE_AUDIT",
 json.dumps(top2d_surface_audit),flush=True)

# Place the ball on the anatomically oriented palm-facing surface.
# Keep explicit penetration and multiple-contact audit, no fake PASS.
ballradius=.068
palm_avg=np.mean(palmpoints,axis=0)
projected=(palmpoints-np.array(palm)) @ np.array(palm_normal)
palmar_height=float(np.quantile(projected,.88))
center=np.array(palm)+np.array(palm_normal)*(ballradius+palmar_height+.003)
for j in range(12):
 d=np.linalg.norm(palmpoints-center,axis=1)
 gap=float(np.min(d)-ballradius)
 if abs(gap)<.002:break
 center-=np.array(palm_normal)*clamp(gap,-.012,.012)
gaps=np.linalg.norm(palmpoints-center,axis=1)-ballradius
contact={"surface_gap_min_mm":float(gaps.min()*1000),
 "near_surface_points_5mm":int(np.sum(np.abs(gaps)<.005)),
 "negative_interpenetrating_points":int(np.sum(gaps<-.003)),
 "palm_mesh_semantic_ids_count":len(palm_ids)}
print("OFFICIAL_PALM_BALL_CONTACT",json.dumps(contact),flush=True)
# V122.2 genuine multi-patch finger articulation against one FIXED
# provisional gold ball. The sphere stays at the already-calculated position;
# optimize only the official individual finger joints. Do not claim art pass
# without user-approved V20 hand closeups/top art.
provisional_seed_ball_center=center.copy()
pad_regions={}
for digit in (1,2,3,4,5):
 key=f"finger{digit}-3.L"
 pad_regions[key]=sorted(i for i,w in valid_weights[key]
  if w/totals[i]>.38 and
  body.data.vertices[i].normal.dot(rest_palmar_normal)>.12)
 assert len(pad_regions[key])>=10,(key,len(pad_regions[key]))

# V122.2 ART REFERENCE ABSENT: obtain ONE provisional, geometrically
# plausible sphere center from frozen anatomical palm + distinct index/middle
# distal pad surfaces before finger fitting. Lock it thereafter. Never call
# this user-approved art; position is not adapted during finger IK optimization.
# This replaces V122's flawed palm-centroid-only guess.
initial_skin=evaluated_body()
frozen_contact_patches={
 "palm":initial_skin[palm_ids],
 "index":initial_skin[pad_regions["finger2-3.L"]],
 "middle":initial_skin[pad_regions["finger3-3.L"]]}
def provisional_center_cost(cc):
 score=0.
 for name,pts in frozen_contact_patches.items():
  dd=np.linalg.norm(pts-cc,axis=1)-ballradius
  close=float(np.min(np.abs(dd)))
  penetration=np.maximum(0,-dd-.001)
  score+=(close/.0018)**2+650.*np.sum((penetration/.001)**2)
 score+=.10*(np.linalg.norm((cc-provisional_seed_ball_center)/.05)**2)
 return float(score)
candidate_centers=[]
for dx in np.linspace(-.020,.072,13):
 for dy in np.linspace(-.044,.018,9):
  for dz in np.linspace(-.042,.052,9):
   cc=provisional_seed_ball_center+np.array([dx,dy,dz])
   candidate_centers.append((provisional_center_cost(cc),cc))
candidate_centers.sort(key=lambda item:item[0])
ball_locked=candidate_centers[0][1].copy()
for step_size in (.008,.004,.002,.001,.00045):
 improved=True
 for _ in range(4):
  base_score=provisional_center_cost(ball_locked)
  scores=[(base_score,ball_locked.copy())]
  for axis in range(3):
   for sign in (-1,1):
    tmp=ball_locked.copy();tmp[axis]+=sign*step_size
    scores.append((provisional_center_cost(tmp),tmp))
  val,chosen=min(scores,key=lambda item:item[0])
  if val>=base_score-1e-8:break
  ball_locked=chosen.copy()
center=ball_locked.copy()
print("V129_LOCKED_PROVISIONAL_BALL_TARGET",json.dumps({
 "source":"FROZEN_REAL_PALM_AND_DISTINCT_INDEX_MIDDLE_PADS_NOT_APPROVED_ART",
 "target":center.tolist(),
 "difference_from_old_palm_only_seed_mm":float(np.linalg.norm(center-provisional_seed_ball_center)*1000),
 "provisional_objective_score":provisional_center_cost(center)}),flush=True)
def contact_pad_measure(digit):
 a=evaluated_body()
 ids=pad_regions[f"finger{digit}-3.L"]
 radial=np.linalg.norm(a[ids]-ball_locked,axis=1)-ballradius
 # Metric uses a distinct official distal phalanx, never aggregates same patch.
 return {"minimum_gap_mm":float(radial.min()*1000),
         "within_5mm":int(np.sum(np.abs(radial)<.005)),
         "deep_penetration_points":int(np.sum(radial<-.003)),
         "vertex_count":len(ids)}
finger_grid_trials=0
for digit in (1,2,3,4):
 jointnames=[f"finger{digit}-{n}.L" for n in range(1,4)]
 for jn in jointnames:rig.pose.bones[jn].rotation_mode="XYZ"
 for iteration in range(2):
  for jn in jointnames[:2]:
   pb=rig.pose.bones[jn]
   baseline=float(pb.rotation_euler.x)
   best_ang=baseline;best_obj=float("inf")
   for offset in (-.24,-.12,0,.12,.24):
    ang=clamp(baseline+offset,-.48,.72)
    pb.rotation_euler.x=ang
    bpy.context.view_layer.update()
    m=contact_pad_measure(digit);finger_grid_trials+=1
    gap=m["minimum_gap_mm"]
    # Prefer a near-surface, noninterpenetrating pad. Strongly penalize
    # crushing or moving fingers through gold instead of cupping it.
    obj=abs(gap-1.4)+35*m["deep_penetration_points"]+4*abs(ang)
    if obj<best_obj:best_obj=obj;best_ang=ang
   pb.rotation_euler.x=best_ang
   bpy.context.view_layer.update()
digit_contact={str(k):contact_pad_measure(k) for k in (1,2,3,4,5)}
distinct_pad_count=sum(1 for k in (1,2,3,4,5)
 if abs(digit_contact[str(k)]["minimum_gap_mm"])<=2.5
 and digit_contact[str(k)]["deep_penetration_points"]==0)
actual=evaluated_body()
palmpoints=actual[palm_ids]
new_palm_gaps=np.linalg.norm(palmpoints-ball_locked,axis=1)-ballradius
palm_geometric_contact=bool(np.min(np.abs(new_palm_gaps))<=.0025)
fingers_multicontact_engineering=bool(distinct_pad_count>=2 and palm_geometric_contact)
contact.update({
 "locked_ball_center_from_pre_finger_optimization":ball_locked.tolist(),
 "ball_target_source":"FROZEN_PALM_INDEX_MIDDLE_ANATOMICAL_SUPPORT_ZONES_PROVISIONAL",
 "ball_target_is_independent_V20_art":False,
 "ball_adjustment_mm_before_finger_IK":float(np.linalg.norm(center-provisional_seed_ball_center)*1000),
 "palmar_patch_nearest_abs_gap_mm_after_finger_fit":float(np.min(np.abs(new_palm_gaps))*1000),
 "digit_pad_contact_distinct_count":int(distinct_pad_count),
 "digit_pad_per_bone_measurements":digit_contact,
 "finger_joint_search_trials":finger_grid_trials,
 "genuine_multi_patch_geometric_contact":fingers_multicontact_engineering,
 "approved_independent_hand_art":False})
print("V129_FIVE_DIGIT_SURFACE_CONTACT_AUDIT",json.dumps(contact),flush=True)
# Multi-patch engineering gate may remain FAIL; it is forbidden to move the
# ball after fitting or to call a nearest-vertex gap an art solution.
# Surface contact proximity only: distinct palmar and finger-pad patches
# need independent reference approval before ART PASS.
body.modifiers.new("Anatomical_Body_Cloth_Collider","COLLISION").settings.thickness_outer=.004
# The user's new approved fullbody image supersedes the old wrong top2D.
# Do NOT run V125 ReAct30 against an incompatible hand pose.
obsolete_old_hand_guide_not_used=True
# Freeze the evaluated anatomically deformed body for the final portable GLB
# but preserve the true official live rig in the editable .blend.
dg=bpy.context.evaluated_depsgraph_get()
evaluated=body.evaluated_get(dg)
baked=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
assert len(baked.vertices)==13380 and len(baked.polygons)==13378
sculpt=bpy.data.objects.new("REAL_OFFICIAL_CC0_SKINNED_BODY_POSE_BAKED",baked)
bpy.context.collection.objects.link(sculpt);sculpt.data.materials.append(ivory)
sculpt["source"]="official MakeHuman CC0 skin and 163 bone rest";sculpt["palm_up_dot"]=palm_dot
body.hide_render=True;rig.hide_render=True
# Sewn single-surface royal gown: each longitudinal vertex chain passes
# continuously through hip, waist, chest and neck. No free-floating bodice.
def dress_sections(z):
 if z<.98:
  t=clamp((z-.12)/.86,0,1)
  return (.36-.15*(t**.78),.275-.11*(t**.83))
 if z<1.16:
  t=(z-.98)/.18
  return (.21+.023*t,.165+.038*t)
 t=clamp((z-1.16)/.17,0,1)
 return (.233-.021*t,.203-.020*t)
# V122.2: persistent primary/secondary/tertiary 3D causal fold graph.
# Three-dimensional crests deform actual material mesh. No texture-only or
# random uniform sinusoidal waves can satisfy the folded-sculpture gate.
fold_graph={
 "authority":"PROVISIONAL_SCULPT_NO_INDEPENDENT_V20_ART",
 "source_mesh":"10_ONE_SEWN_CONTINUOUS_ROYAL_CHITON_WAIST",
 "level_1_primary":[
  {"id":"P_HEM_FRONT_L","angle":-2.45,"width":.23,"amplitude":.029,"source":"hip_belt_to_hem"},
  {"id":"P_HEM_F_LEFT","angle":-1.85,"width":.19,"amplitude":.043,"source":"underbust_to_hem"},
  {"id":"P_HEM_FRONT_C","angle":-1.32,"width":.20,"amplitude":.033,"source":"waist_frontal_centre"},
  {"id":"P_HEM_FRONT_R","angle":-.55,"width":.23,"amplitude":.038,"source":"hip_to_hem"},
  {"id":"P_HEM_SIDE_R","angle":.32,"width":.20,"amplitude":.025,"source":"side_waist_gather"},
  {"id":"P_HEM_BACK_R","angle":1.45,"width":.23,"amplitude":.027,"source":"rear_drape_root"},
  {"id":"P_HEM_BACK_L","angle":2.45,"width":.24,"amplitude":.023,"source":"rear_belt"}],
 "level_2_secondary":[
  {"id":"S_WAIST_FLEFT","angle":-2.05,"width":.12,"amplitude":.013,"source":"waist_belt"},
  {"id":"S_WAIST_FRIGHT","angle":-.70,"width":.13,"amplitude":.012,"source":"waist_sash"},
  {"id":"S_SIDE_GATHER","angle":.20,"width":.11,"amplitude":.010,"source":"side_seam"},
  {"id":"S_REAR_VEIL_FALL","angle":2.60,"width":.13,"amplitude":.009,"source":"rear_layer"}],
 "level_3_tertiary":[
  {"id":"T_HEM_EDGE_LIPS","source":"hem_fixed_outer_seam","amplitude":.004},
  {"id":"T_BELT_COMPRESS","source":"waist_sash_tension","amplitude":.003},
  {"id":"T_SLEEVE_EDGE","source":"shoulder_cuff_seam","amplitude":.003}],
 "fold_curve_coordinates":"Generated below from same actual 3D groomed mesh",
 "independent_reference_approved":False}
def cyclic_diff(a,b):
 return math.atan2(math.sin(a-b),math.cos(a-b))
def fold_profile(a,w,z):
 hem_envelope=clamp((1.14-z)/1.07,0,1)**1.5
 v=0
 for guide in fold_graph["level_1_primary"]:
  angle=guide["angle"]+(.20*(1-w))+.07*sin(pi*w)
  d=cyclic_diff(a,angle)
  width=guide["width"]
  crest=math.exp(-.5*(d/width)**2)
  valley=math.exp(-.5*((abs(d)-width*1.65)/(width*.62))**2)
  v+=guide["amplitude"]*hem_envelope*(crest-.35*valley)
 # Medium folds branch from the taut waist as curved channels.
 waist_envelope=math.exp(-((z-.96)/.225)**2)
 for guide in fold_graph["level_2_secondary"]:
  shifted=guide["angle"]+.19*(1-w)
  d=cyclic_diff(a,shifted)
  v+=guide["amplitude"]*waist_envelope*math.exp(-.5*(d/guide["width"])**2)
 # Small relief follows an actual lower hem / edge border.
 hem_lip=math.exp(-((z-.13)/.075)**2)
 v+=.0035*hem_lip*sin(13*a+3*w)
 return v
N=144;M=104; dress_v=[];dress_f=[];waist_rows=[]
for j in range(M):
 w=j/(M-1);z=.105+1.225*w
 rx,ry=dress_sections(z)
 for i in range(N):
  a=2*pi*i/N
  pleat=fold_profile(a,w,z)
  # Three guided U-shaped chest folds converge into the waist tension.
  if z>.95:
   chest_env=math.sin(pi*clamp((z-.94)/.39,0,1))
   for centre,amplitude in [(-2.05,.016),(-1.52,.019),(-.95,.013)]:
    d=cyclic_diff(a,centre+.34*(z-1.08))
    pleat+=amplitude*chest_env*math.exp(-.5*(d/.16)**2)
  r_x=rx+pleat;r_y=ry+.78*pleat
  neckline=-.088*max(0,-sin(a))**8*(w**20)
  dress_v.append((r_x*cos(a),r_y*sin(a)-.018,z+neckline))
fold_graph["sampled_3D_primary_lines"]=[]
for guide in fold_graph["level_1_primary"]:
 coords=[]
 for w in np.linspace(.08,.97,22):
  z=.105+1.225*w; a=guide["angle"]+.20*(1-w)+.07*sin(pi*w)
  rx,ry=dress_sections(z);d=fold_profile(a,w,z)
  coords.append([round(float((rx+d)*cos(a)),6),
                 round(float((ry+.78*d)*sin(a)-.018),6),
                 round(float(z),6)])
 fold_graph["sampled_3D_primary_lines"].append({"id":guide["id"],"vertices":coords})
(OUT/"V129_FOLD_CAUSAL_GRAPH.json").write_text(json.dumps(fold_graph,indent=2))

for j in range(M-1):
 for i in range(N):
  k=j*N+i;kn=j*N+(i+1)%N
  dress_f.append((k,kn,kn+N,k+N))
gown=meshobj("10_ONE_SEWN_CONTINUOUS_ROYAL_CHITON_WAIST",dress_v,dress_f,chiton_mat)
# True 3D sculptural thickness; no disconnected cylinder floating over waistband.
m=gown.modifiers.new("TrueClothSurfaceThickness","SOLIDIFY");m.thickness=.004;m.offset=0
sub=gown.modifiers.new("GarmentFineFoldSubdivision","SUBSURF");sub.levels=1;sub.render_levels=1
def gown_front(x,z,extra=.009):
 # Query the SAME sculpted 3D ridge surface used by the sewn gown.
 # The former approximation ignored the actual fold depth and could
 # float the waist ribbon above it or penetrate the skirt.
 rx,ry=dress_sections(z)
 a=-math.acos(clamp(x/rx,-.94,.94))
 w=clamp((z-.105)/1.225,0,1)
 ridge=fold_profile(a,w,z)
 r_x=rx+ridge;r_y=ry+.78*ridge
 t=clamp(x/max(.04,r_x),-.96,.96)
 return -.018-r_y*sqrt(max(.01,1-t*t))-extra
# Wide sculpted diagonal sash conforms to the underlying true chiton.
def ribbon(name,fn,nu,nv,mat,thickness=.004):
 pts=[fn(i/(nu-1),j/(nv-1)) for j in range(nv) for i in range(nu)]
 ff=[]
 for j in range(nv-1):
  for i in range(nu-1):
   a=j*nu+i;ff.append((a,a+1,a+nu+1,a+nu))
 o=meshobj(name,pts,ff,mat)
 mod=o.modifiers.new("ActualClothLayerThickness","SOLIDIFY")
 mod.thickness=thickness;mod.offset=0
 smooth=o.modifiers.new("SurfaceSculptSmooth","SUBSURF")
 smooth.levels=1;smooth.render_levels=1
 return o
def sash(u,w):
 z=1.295-.285*w+(.014*(u-.5))
 center_x=.165-.30*w
 width=.12+.035*sin(pi*w)
 x=center_x+(u-.5)*width
 # Three physical crest-and-valley bands, not a featureless flat strap.
 crest=.015*math.exp(-((u-.24)/.14)**2)-.011*math.exp(-((u-.53)/.12)**2)
 crest+=.009*math.exp(-((u-.78)/.13)**2)
 y=gown_front(x,z,.021)-crest*math.sin(pi*(.10+.85*w))
 return (x,y,z)
sash_ob=ribbon("11_SHOULDER_TO_WAIST_CARVED_HIMATION",sash,22,55,himation_mat)
def waist_swag(u,w):
 x=(u-.5)*.425
 # Royal waist is a shallow sewn wrap under tension, not a wide
 # floating U-shaped hammock crossing the abdomen.
 centerz=.992-.037*sin(pi*u)+.013*(u-.5)
 z=centerz+(w-.5)*(.047+.009*sin(pi*u))
 # Folds converge into an anchored waist seam; raised crests have
 # physical volume and two valleys toward the belt, not a floating ribbon.
 crease=.012*math.exp(-((u-.26)/.16)**2)-.009*math.exp(-((u-.53)/.13)**2)
 crease+=.006*math.exp(-((u-.77)/.16)**2)
 y=gown_front(x,z,.013)-crease*math.sin(pi*w)
 return (x,y,z)
swag=ribbon("12_WAIST_SAG_ATTACHED_TO_SHARED_CHITON",waist_swag,64,19,himation_mat)
# Real wraparound stitched belt sampled from the original SAME chest-waist-
# skirt surface, not a hovering independent decorative rectangle.
def waist_belt(u,w):
 a=2*pi*u
 z=.985+(w-.5)*.055
 rx,ry=dress_sections(z)
 elev=fold_profile(a,clamp((z-.105)/1.225,0,1),z)
 outset=.008
 x=(rx+elev+outset)*cos(a)
 y=(ry+.78*elev+outset)*sin(a)-.018
 return (x,y,z)
belt=ribbon("12A_REAL_SEWN_ROYAL_WAIST_BELT",waist_belt,108,11,himation_mat)
# Waist/belt/swag share the same anatomy-derived 3D reference surface.
# Seam audit: independent draped overlay anchored onto same underlying gown.
seam_samples=[]
for u in np.linspace(.06,.94,12):
 x=(u-.5)*.425;z=.992-.11*sin(pi*u)
 seam_samples.append(abs(waist_swag(u,.5)[1]-gown_front(x,z,0)))
seam_max_mm=max(seam_samples)*1000
if seam_max_mm>30:raise RuntimeError("P0_WAIST_SAG_NOT_ATTACHED_TO_CHITON")
# Tailored short rear veil, two layered polygonal pleats from crown to shoulder.
for layer in (0,1):
 def veil(u,w,ly=layer):
  crest=(.020*math.exp(-((u-.27)/.12)**2)
         -.013*math.exp(-((u-.51)/.10)**2)
         +.016*math.exp(-((u-.78)/.13)**2))*w
  x=(u-.5)*(.132+.355*w+.026*ly)
  z=1.59-.54*w+.009*sin(3*pi*u)*w
  y=.109+.143*w+.015*ly+crest
  return(x,y,z)
 ribbon("13_ROYAL_SHORT_REAR_VEIL_LAYER_%s"%layer,veil,36,38,chiton_mat if layer==0 else himation_mat)
# Low-profile sewn shoulder sleeves: arms remain visibly articulated.
for sign in (-1,1):
 def sleeve(u,w,sg=sign):
  x=sg*(.185+.080*u+.018*w);z=1.285-.26*w+.025*sin(pi*u)*w
  y=-.12+.135*u-.02*w
  return(x,y,z)
 ribbon("14_SHOULDER_CARVED_CUFF_%s"%sign,sleeve,18,29,himation_mat)
# Hair geometry and braid volumes (single cap, wave roots, rear bun).
head_v=[];head_f=[];rings=20;sections=72
for j in range(rings):
 theta=.0001+1.26*j/(rings-1)
 for i in range(sections):
  ph=2*pi*i/sections
  a=sin(theta)
  head_v.append((.139*a*cos(ph),.009+.116*a*sin(ph),1.525+.135*cos(theta)))
for j in range(rings-1):
 for i in range(sections):
  k=j*sections+i;kn=j*sections+(i+1)%sections
  head_f.append((k,kn,kn+sections,k+sections))
cap=meshobj("20_SCULPTED_CARVED_HAIR_CAP",head_v,head_f,hair_mat)
for side in (-1,1):
 for n in range(4):
  pts=[]
  for i in range(40):
   t=i/39
   pts.append((side*(.025+.033*n+.035*t),-.10-.022*cos(1.2*pi*t+.4*n),1.555+.045*sin(pi*t)-.029*n))
  lineobj("21_Royal_Hair_ForeheadWave_%s_%d"%(side,n),pts,.010,hair_mat)
 for n in range(2):
  pts=[]
  for i in range(66):
   t=i/65;a=2*pi*(1.45*t+n*.3)
   pts.append((side*(.139+.012*cos(a)+.012*n),-.035+.011*sin(a),1.445-.205*t))
  lineobj("22_Royal_SideBraidedLock_%s_%d"%(side,n),pts,.009,hair_mat)
sphere("23_Occipital_Hair_Bun",(.0,.086,1.537),.085,hair_mat)
lineobj("24_Fine_Gold_Diadem",[(.132*cos(a),-.06-.048*sin(a),1.568+.066*sin(a))for a in np.linspace(0,pi,130)],.005,gold)
for side in (-1,1):sphere("25_Gold_Shoulder_Brooch_%s"%side,(side*.22,-.14,1.285),.014,gold)
# Ball and uninterrupted golden thread. Fixed world placement in all 24 angles.
ball=sphere("30_SINGLE_GOLD_BALL",center,ballradius,gold)
for strand in range(4):
 pts=[]
 for i in range(160):
  t=i/159;theta=.08+(pi-.16)*t;phi=9*pi*t+pi*strand/2
  rr=ballradius+.0025
  pts.append((center[0]+rr*sin(theta)*cos(phi),center[1]+rr*sin(theta)*sin(phi),center[2]+rr*cos(theta)))
 lineobj("31_Gold_Ball_Winding_%d"%strand,pts,.0015,gold)
# Preserve one actual 3D curve running down outside the body.
thread=[]
for i in range(180):
 t=i/179
 x=float(center[0])-.62*t+.14*sin(pi*t)
 y=float(center[1])-.19*sin(pi*t)
 z=float(center[2])-1.23*t+.027*sin(2*pi*t)
 thread.append((x,y,z))
lineobj("32_SINGLE_CONTINUOUS_OUTER_GOLD_THREAD",thread,.006,gold)
for nm,r,depth,z,material in [
 ("40_PEDESTAL_BASE",.398,.065,-.082,base_mat),
 ("41_PEDESTAL_GOLD_RING",.390,.023,-.038,gold),
 ("42_PEDESTAL_MAIN",.399,.071,.009,ivory),
 ("43_PEDESTAL_CAP",.425,.031,.062,base_mat)]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=80,radius=r,depth=depth,location=(0,0,z))
 o=bpy.context.object;o.name=nm;o.data.materials.append(material)
# Blender cloth solver is retained as a separate evidence probe and is NOT
# allowed to erase authored royal garment folds.
probe=ribbon("90_REAL_PHYSICS_WAIST_SAMPLE",lambda u,w:waist_swag(u,w),40,12,himation_mat)
grp=probe.vertex_groups.new(name="Pinned_Seams")
ids=list(range(40))+list(range(40*11,40*12))
grp.add(ids,1,"REPLACE")
c=probe.modifiers.new("Genuine_Blender_Cloth_Audit","CLOTH")
c.settings.quality=3;c.settings.mass=.24;c.settings.vertex_group_mass=grp.name
c.collision_settings.use_collision=True
c.point_cache.frame_start=1;c.point_cache.frame_end=12
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=12
for frame in range(1,13):scene.frame_set(frame)
ev=probe.evaluated_get(bpy.context.evaluated_depsgraph_get())
samplemesh=ev.to_mesh()
phys=np.mean([tuple(v.co) for v in samplemesh.vertices],axis=0)
ev.to_mesh_clear()
probe.hide_render=True;probe.hide_set(True)
body.hide_render=True;rig.hide_render=True
# Verify no crude collapse of forearm: compare mean edge-length ratios on
# original source faces whose vertices were strongly assigned to forearm.
# Final result MUST use the same unique physical mesh edges as the
# 42 candidate trials. Repeated face-edge occurrences otherwise change
# the percentile distribution and make acceptance non-reproducible.
ratios=np.linalg.norm(actual[ix]-actual[iy],axis=1)/rest_edge
if len(ratios)<200:raise RuntimeError("FOREARM_EDGE_AUDIT_INSUFFICIENT")
forearm_quality={"edges_checked":len(ratios),"min_edge_ratio":float(np.min(ratios)),
 "p02_edge_ratio":float(np.quantile(ratios,.02)),
 "p98_edge_ratio":float(np.quantile(ratios,.98)),
 "max_edge_ratio":float(np.max(ratios)),
 "edges_below_0p50":int(np.sum(ratios<.5)),
 "unique_edge_pairs":True,
 "DQS_volume_preservation":skin.use_deform_preserve_volume}
print("REAL_OFFICIAL_FOREARM_EDGE_AUDIT",json.dumps(forearm_quality),flush=True)
if forearm_quality["p02_edge_ratio"]<.65 or forearm_quality["p98_edge_ratio"]>1.6:
 print("P0_FOREARM_COLLAPSE_OR_STRETCH: no art release",flush=True)
# One user-approved fullbody sheet replaces the obsolete 7-point art.
# Independent 26-camera artwork calibration is NOT claimed.
redesign=R/"ariadne_v129"/"src"/"fullbody_redesign.py"
assert redesign.is_file(),redesign
exec(compile(redesign.read_text(encoding="utf-8"),str(redesign),"exec"),globals())
report={
 "version":"129.0","status":"COMPLETE_COMPONENT_MODEL_ENGINEERING_PALMUP_NOT_ART_APPROVED",
 "anatomical_mesh":"Official MakeHuman CC0 source base.obj + caucasian-female-young.target",
 "DQS_preserve_volume_enabled":skin.use_deform_preserve_volume,
 "official_bones":len(sk["bones"]),"original_body_vertices":len(body.data.vertices),
 "original_body_faces":len(body.data.polygons),"official_weights":True,
 "all_30_left_right_finger_segment_weights_nonzero":True,
 "source_hashes":{n:hashlib.sha256((IN/n).read_bytes()).hexdigest() for n in ("base.obj","caucasian-female-young.target","default.mhskel","default_weights.mhw")},
 "top2d_palmar_surface_classification":top2d_surface_audit,
 "approved_reference_status":"USER_APPROVED_NEW_FULLBODY_CONCEPT_SINGLE_SHEET",
 "independent_26_view_art_calibration_complete":False,
 "palmar_rest_skin_vertices":len(palmar_ids),
 "dorsal_rest_skin_vertices":len(dorsal_ids),
 "palm_cross_product_flipped_from_V123":True,
 "palmar_not_dorsal_support_engineering_gate":
    bool(top2d_surface_audit.get("top_palmar_side_visible_by_depth",False)),
 "weight_summary":skin_audit,
 "forearm_zero_severe_gate":bool(forearm_quality["edges_below_0p50"]==0),
 "forearm_adversarial_108_pose_gate":bool(forearm_candidate_p0),
 "right_hand_9dof_provisional_solution":right_best[1].tolist(),
 "right_hand_target_error_m":right_target_error,
 "right_hand_gesture_changed_from_neutral":right_pose_changed,
 "right_hand_independent_art_approved":False,
 "right_forearm_mesh_edge_quality":right_forearm_quality,
 "right_forearm_zero_severe_gate":right_forearm_quality["accepted_zero_severe"],
 "support_side":"anatomical L",
 "left_palm_normal_world":list(palm_normal),"left_palm_up_dot":palm_dot,
 "left_elbow_world":list(elbow),"left_wrist_world":list(wrist),
 "left_palm_world":list(palm),"right_arm_pose_modified":right_pose_changed,
 "actual_evaluated_body_max_vertex_displacement_m":float(np.max(disp)),
 "actual_ball_center_world":list(center),"gold_ball_radius_m":ballradius,
 "contact":contact,"forearm_mesh_edge_quality":forearm_quality,
 "multi_patch_contact_engineering_gate":bool(fingers_multicontact_engineering),
 "orb_position_locked_during_finger_fit":True,
 "actual_fold_graph_primary_count":len(fold_graph["level_1_primary"]),
 "actual_fold_graph_secondary_count":len(fold_graph["level_2_secondary"]),
 "actual_fold_graph_tertiary_count":len(fold_graph["level_3_tertiary"]),
 "true_waist_wrap_circumferential_belt_mesh":True,
 "waist_swag_U_hammock_artifact_rebuilt":True,
 "waist_sash_and_belt_sample_the_real_sculpted_fold_profile":True,
 "actual_3D_fold_graph_file":"V129_FOLD_CAUSAL_GRAPH.json",
 "fold_reference_24_art_approved":False,
 "sewn_garment_connected_chiton_faces":len(dress_f),
 "waist_layer_attach_max_offset_mm":seam_max_mm,
 "new_user_approved_fullbody_sheet":"ARIADNE_V2_APPROVED_FULL_BODY_SHEET",
 "new_golden_ratio_K_pose":"TO_BE_VISUALLY_AUDITED_AGAINST_FULL_BODY_REFERENCE",
 "new_real_sculpt_audit":"V129_FULLBODY_SCULPTURAL_REDESIGN_AUDIT.json",
 "new_art_style_and_components":v129_art_design,
 "obsolete_wrong_top2d_React30_used":False,
 "true_blender_physics_probe":True,"physics_probe_final_center":phys.tolist(),
 "normal_map_does_not_mask_geometry":True,
 "art_v20_original_24_anchors_available":False,
 "new_user_approved_fullbody_v2_reference_available":True,
 "art_top_5_independent_references_available":False,
 "art_similarity_24x95_measured":False,"hand_digit_multi_contact_art_approved":False,
 "palm_surface_semantics_verified_against_V20":False,"art_approved":False}
(OUT/"V129_P0_ANATOMY_AND_GARMENT_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
# Editable source includes true 163-bone rest and official weighting.
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"V129_OFFICIAL_CC0_LIVE_RIG_EDITABLE.blend"))
# Export all finished objects; keep only authentic evaluated body, gown and
# rest of costume. Source rig and original unbaked body are not duplicated.
bpy.ops.object.select_all(action="DESELECT")
for o in scene.objects:
 if o.type in ("MESH","CURVE") and o not in (body,probe) and not o.hide_render:o.select_set(True)
bpy.context.view_layer.objects.active=sculpt
glb=OUT/"Ariadne_V129_OfficialPalmUp_FullCandidate_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.exists() and glb.stat().st_size>350000
# Clean reload is necessary; do not trust cached in-scene model.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
loaded=[o for o in scene.objects if o.type=="MESH"]
assert len(loaded)>18
# CI can use an independent actual-GLB renderer when host graphics libraries
# are unavailable. This skip is AFTER successful GLB export and fresh import.
if os.environ.get("ARIADNE_RENDER_BACKEND")=="EXTERNAL_VTK":
    report["exported_GLTF_bytes"]=glb.stat().st_size
    report["exported_sha256"]=hashlib.sha256(glb.read_bytes()).hexdigest()
    report["actual_reimported_camera_views"]=0
    report["reimport_mesh_count"]=len(loaded)
    report["render_backend"]="EXTERNAL_VTK_INDEPENDENT_ACTUAL_GLTF"
    report["P0_palm_up_gate"]="PASS" if palm_dot>=.82 else "FAIL"
    report["P0_forearm_edge_p02_gate"]="PASS" if forearm_quality["p02_edge_ratio"]>=.65 and forearm_quality["edges_below_0p50"]==0 else "FAIL"
    report["P0_waist_attached_geometry_gate"]="PASS" if seam_max_mm<=30 else "FAIL"
    report["P0_right_forearm_bilateral_gate"]="PASS" if right_forearm_quality["accepted_zero_severe"] else "FAIL"
    (OUT/"V129_P0_ANATOMY_AND_GARMENT_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print("V129_REAL_GLB_EXPORTED_AND_REIMPORTED",json.dumps({"bytes":glb.stat().st_size,
      "mesh_count":len(loaded),"forearm_p02":forearm_quality["p02_edge_ratio"],
      "palm_up_dot":palm_dot,"waist_mm":seam_max_mm}),flush=True)
    print("EXTERNAL_GLB_RENDER_REQUIRED_BACKEND_OFFLINE_VTK",flush=True)
    raise SystemExit(0)
# Art review diagnostics from one fixed YAW model coordinate system.
world=bpy.data.worlds.new("Museum_Night_Backdrop");scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.05,.065,.09,1);bg.inputs["Strength"].default_value=.7
def area(n,where,power,rgb,size):
 ld=bpy.data.lights.new(n,"AREA");ld.energy=power;ld.color=rgb;ld.shape="DISK";ld.size=size
 o=bpy.data.objects.new(n,ld);bpy.context.collection.objects.link(o)
 o.location=where;o.rotation_euler=(Vector((0,0,.9))-o.location).to_track_quat("-Z","Y").to_euler()
area("Key",(-2,-3.4,3.1),500,(1,.92,.84),3)
area("Rim",(2,2.3,3.4),460,(.89,.93,1),2.5)
cam=bpy.data.objects.new("ONE_FIXED_ORTHOGRAPHIC",bpy.data.cameras.new("AriadneCamera"))
bpy.context.collection.objects.link(cam);scene.camera=cam
cam.data.type="ORTHO";cam.data.ortho_scale=1.98
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=420;scene.render.resolution_y=560
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="Standard";scene.render.film_transparent=False
look=Vector((0,0,.79))
for deg in range(0,360,15):
 a=math.radians(deg);cam.location=(3.75*sin(a),-3.75*cos(a),.99)
 cam.rotation_euler=(look-cam.location).to_track_quat("-Z","Y").to_euler()
 scene.render.filepath=str(OUT/f"V129_Actual_GLB_{deg:03d}.png")
 bpy.ops.render.render(write_still=True)
 print("V129_RENDERED_REAL_VIEW",deg,flush=True)
report["exported_GLTF_bytes"]=glb.stat().st_size
report["exported_sha256"]=hashlib.sha256(glb.read_bytes()).hexdigest()
report["actual_reimported_camera_views"]=24
report["reimport_mesh_count"]=len(loaded)
(OUT/"V129_P0_ANATOMY_AND_GARMENT_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("V129_OFFICIAL_COMPLETE_RESULT",json.dumps({k:v for k,v in report.items() if k not in ("weight_summary","source_hashes")},default=float),flush=True)
