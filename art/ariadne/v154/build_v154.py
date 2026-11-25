"""Ariadne V154 actual immutable-static statue export.
Fix identified V153 root bug: animated skin/IK does not become default GLB pose.
Retarget CC0 true rig, EVALUATE original skinned body, bake 13,380 MakeHuman
vertices into static geometry, strip all animation/skin tracks.
Then replace unusable hanging violet panels and exposed vertical comb hair with
anatomically attached scalp/braids and side-connected sculptural royal cloth.
No false 266x30 completed art passes; independent art still governs release.
"""
import bpy,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"artifacts"/"ariadne_v154";OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/"artifacts"/"ariadne_v153"/"Ariadne_V153_Real_Sculpture_Engineering_NOT_ART_APPROVED.glb"
assert SOURCE.stat().st_size>1000000
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
scene=bpy.context.scene
body=[o for o in bpy.data.objects if o.type=="MESH" and "Anatomy" in o.name]
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(body)==1 and len(rigs)==1,(len(body),len(rigs))
body=body[0];rig=rigs[0]
coords=[body.matrix_world@Vector(c) for c in body.bound_box]
cx=(min(p.x for p in coords)+max(p.x for p in coords))/2
cy=(min(p.y for p in coords)+max(p.y for p in coords))/2
base=min(p.z for p in coords)
sphere=[o for o in bpy.data.objects if o.type=="MESH" and "Golden_Orb_Actual_Sphere" in o.name]
assert len(sphere)==1
ball=sphere[0]
def wp(side):return rig.matrix_world@rig.pose.bones["wrist."+side].tail
w0={s:wp(s) for s in ("L","R")}
bs=min(("L","R"),key=lambda s:(w0[s]-ball.location).length)
rs="R" if bs=="L" else "L"
print("V154_SOURCE_ARMS",bs,rs,flush=True)
# Destructive removal of any legacy exported actions before applying new pose.
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
for pb in rig.pose.bones:
 for constraint in list(pb.constraints):pb.constraints.remove(constraint)
 pb.rotation_mode="QUATERNION"
 pb.rotation_quaternion=(1,0,0,0)
 pb.location=(0,0,0)
 pb.scale=(1,1,1)
scene.frame_set(1);bpy.context.view_layer.update()
goals=[];targets={}
for side,is_ball in ((bs,True),(rs,False)):
 current=wp(side)
 sign= -1 if current.x<cx else 1
 t=Vector((cx+sign*(.255 if is_ball else .17),
           cy+(.16 if is_ball else .065),
           base+(1.34 if is_ball else .87)))
 targets[side]=t
 o=bpy.data.objects.new("V154_IK_GOAL_"+side,None)
 scene.collection.objects.link(o);o.location=t;goals.append(o)
 pb=rig.pose.bones["wrist."+side]
 c=pb.constraints.new("IK");c.target=o;c.chain_count=5;c.iterations=220
bpy.context.view_layer.update()
errors={s:float((wp(s)-targets[s]).length) for s in ("L","R")}
assert errors[bs]<.13,("bad wrist pose",errors)
# Evaluate original official 13k-vertex skinning AFTER actual Blender IK.
deps=bpy.context.evaluated_depsgraph_get()
eo=body.evaluated_get(deps)
world=body.matrix_world.copy()
mes=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=deps)
assert len(mes.vertices)>=10000,len(mes.vertices)
frozen=bpy.data.objects.new("V154_ACTUAL_CC0_ANATOMY_STATIC_POSE",mes)
bpy.context.collection.objects.link(frozen)
frozen.matrix_world=world
if len(mes.materials)==0:
 for m in body.data.materials:mes.materials.append(m)
frozen["official_source"]="MakeHuman_CC0_real_mesh_baked_pose_13380_topology"
frozen["pose_source"]="actual_evaluated_IK_mesh_not_animated_GLTF_rest"
frozen["skin_baked_mesh_vertex_count"]=len(mes.vertices)
palm=wp(bs);ball.location=palm+Vector((0,.027,.074))
orb_pose_target=tuple(float(x) for x in ball.location)
bpy.data.objects.remove(body,do_unlink=True)
bpy.data.objects.remove(rig,do_unlink=True)
for o in goals:
 if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
assert not [o for o in bpy.data.objects if o.type=="ARMATURE"]
print("V154_POSE_FROZEN",len(mes.vertices),errors,orb_pose_target,flush=True)

def mat(name,rgb,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(*rgb,1)
 p.inputs["Metallic"].default_value=metal
 p.inputs["Roughness"].default_value=.58 if not metal else .3
 return m
white=mat("V154_Ivory_Carving",(.83,.80,.73))
purple=mat("V154_Purple_Royal_Cloth",(.27,.115,.35))
purple2=mat("V154_Deep_Purple_Sculpture",(.18,.065,.245))
gold=mat("V154_Carved_Gold",(.72,.48,.2),.65)
hairmat=mat("V154_Authentic_Sculpted_Hair",(.37,.245,.16))
def surface(name,vertices,faces,material,thick=.008):
 mesh=bpy.data.meshes.new(name+"_geometry");mesh.from_pydata(vertices,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 mesh.materials.append(material)
 for f in mesh.polygons:f.use_smooth=True
 if thick:
  s=obj.modifiers.new("Nonzero_Cloth_Thickness","SOLIDIFY");s.thickness=thick
 su=obj.modifiers.new("Smooth_Carved_Folds","SUBSURF");su.levels=1
 return obj
def pathcurve(name,points,thickness,material,cyclic=False):
 cu=bpy.data.curves.new(name+"_real_3d","CURVE")
 cu.dimensions="3D";cu.bevel_depth=thickness;cu.bevel_resolution=3
 s=cu.splines.new("BEZIER");s.bezier_points.add(len(points)-1)
 for q,p in zip(s.bezier_points,points):
  q.co=p;q.handle_left_type="AUTO";q.handle_right_type="AUTO"
 s.use_cyclic_u=cyclic
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob)
 cu.materials.append(material)
 return ob

# Eliminate comb-looking V149/V153 hair and disconnected scalp art altogether.
bad_hair_prefixes=("V149_Protected_Back_Scalp_Shell",
 "V149_Anatomical_Posterior_Rooted_Hair_","V149_Postauricular_",
 "V149_Scalp_Connected_Back_Braid_","V149_Gold_Crown_Arc_",
 "V149_Diadem_Boss_","V153_EarBack_ArtDirected_Braid_",
 "V153_Royal_Deep_Back_Braid_")
bad_hair=[]
for o in list(bpy.data.objects):
 if any(o.name.startswith(n) for n in bad_hair_prefixes):
  bad_hair.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(bad_hair)>38,len(bad_hair)
# Real topographic scalp shell, expanding downward only in posterior hemisphere.
# Theta 0/180 point lateral +/-X. +Y frontal. Neither curls nor bands
# intersect the core forehead/eye/nose/mouth exclusion volume.
N=100;R=28;vs=[];fs=[]
hz=base+1.53
for i in range(R):
 t=i/(R-1)
 for j in range(N):
  theta=2*math.pi*j/N
  back_fraction=max(0,-math.sin(theta))
  phi=t*(1.12+.54*back_fraction)
  x=cx+.106*math.sin(phi)*math.cos(theta)
  y=cy+.089*math.sin(phi)*math.sin(theta)
  z=hz+.136*math.cos(phi)
  vs.append((x,y,z))
for i in range(R-1):
 for j in range(N):
  a=i*N+j;b=i*N+(j+1)%N
  fs.append((a,b,b+N,a+N))
surface("V154_Sculpted_Connected_Scalp_Hair",vs,fs,hairmat,.007)
# Low relief side locks centered *behind* ears on actual posterior scalp.
for side in (-1,1):
 for i in range(5):
  pts=[]
  for j in range(30):
   t=j/29;phi=.55+1.04*t
   th=(math.pi if side<0 else 0)+(.38+.042*i)*side*t
   x=cx+side*(.106+.003*i)*math.sin(phi)
   y=cy-.033-.006*i-.012*t
   z=hz+.132*math.cos(phi)
   pts.append((x,y,z))
  pathcurve(f"V154_EarRear_Braided_Lock_{side}_{i}",pts,.005,hairmat)
# Contiguous three-strand braided nape; mass grows from scalp to back.
for i in range(12):
 pts=[]
 for j in range(50):
  t=j/49
  angle=2*math.pi*(2.25*t+i/12)
  pts.append((cx+.029*math.cos(angle)+.009*math.sin(math.pi*t),
              cy-.098-.022*math.sin(angle),
              base+1.46-.42*t))
 pathcurve(f"V154_Greek_Princess_Back_Braid_{i:02d}",pts,.0052,hairmat)
# Woven crown is embedded at hair crest rather than hovering above the face.
for k in range(3):
 pts=[]
 for j in range(49):
  a=math.pi*j/48
  pts.append((cx+.100*math.cos(a),cy-.014-.007*math.sin(a),
              hz+.120+.015*math.sin(a)+k*.003))
 pathcurve(f"V154_Carved_Royal_Crown_Row_{k}",pts,.004,gold)

# Discard erroneous hanging 3D cloth from V153 and replace with connected,
# sculpture-folded actual side/back cloak that sweeps across waist.
oldcloth=("V153_Purple_Himation_Sculpted_Back_Cloak",
          "V153_Purple_Himation_Side_Integrated_Royal_Swath",
          "V153_Purple_Hip_Sculptural_OverlapLayer")
removedcloth=[]
for ob in list(bpy.data.objects):
 if any(ob.name.startswith(n) for n in oldcloth):
  removedcloth.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
assert len(removedcloth)==3
# Same body-relative radius as the V153 chiton, but finer folds.
def skirt_r(z,ang):
 t=max(0,min(1,(base+1.075-z)/.97))
 r=.164+.051*min(t/.28,1) if t<.28 else .215+.098*((t-.28)/.72)
 return r+(.006+.022*t)*(math.sin(13*ang+.6*t)+.30*math.sin(21*ang-1.7*t))
def interp(points,n):
 out=[]
 for j in range(n):
  t=j/(n-1)*(len(points)-1);i=min(len(points)-2,int(t));v=t-i
  out.append(tuple(a*(1-v)+b*v for a,b in zip(points[i],points[i+1])))
 return out
# Artist-authored wide diagonal sash: from elevated shoulder down across
# waist, hip and front opposite side, then final folds descend to hem.
path=interp([
 (cx-.165,cy+.11,base+1.45),
 (cx-.185,cy+.21,base+1.21),
 (cx-.095,cy+.258,base+1.02),
 (cx+.095,cy+.27,base+.89),
 (cx+.225,cy+.215,base+.76),
 (cx+.265,cy+.142,base+.48),
 (cx+.293,cy+.065,base+.19)],70)
U=45;vs=[];fs=[];trim=[]
for i,(x,y,z) in enumerate(path):
 t=i/(len(path)-1)
 width=.11+.22*math.sin(math.pi*t*.83)
 normal=Vector((x-cx,y-cy,0));normal.normalize()
 lateral=Vector((-normal.y,normal.x,0))
 for j in range(U):
  u=j/(U-1)-.5
  # tangential breadth but also sculptural surface displaced toward camera
  ridge=(.012+.031*t)*math.sin((u+.5)*5.4*math.pi+t*1.6)
  taper=(1-.3*abs(2*u))
  p=Vector((x,y,z))+lateral*(width*u)+normal*(ridge+.018*t)+Vector((0,0,.035*u*math.cos(math.pi*t)))
  vs.append(tuple(p))
  if j==0:trim.append(tuple(p))
for i in range(len(path)-1):
 for j in range(U-1):
  a=i*U+j;fs.append((a,a+1,a+U+1,a+U))
surface("V154_Structural_Purple_Front_CrossBody_Waist_Drape",vs,fs,purple,.011)
pathcurve("V154_Gold_Edge_FrontDiagonal",trim,.0036,gold)

# Back himation: horizontal layered *sculptural* folds derived from back view.
# Radial crest wave is directed across z, unlike the prior vertical cylinders.
N=96;R=63;vs=[];fs=[];edge=[]
for i in range(R):
 t=i/(R-1)
 z=base+1.40-1.20*t
 # upper shoulder folded drape gathers at right clasp,
 # then opens across back into long diagonal mantle
 left=2.94-.32*math.sin(math.pi*t)
 right=5.90+.07*t
 for j in range(N):
  u=j/(N-1)
  a=left+(right-left)*u
  rb=skirt_r(z,a) if z<base+1.075 else .194
  # horizontal turning folds and broad scallops (not cylindrical 3D curtain)
  ridge=(.018+.033*t)*math.sin(7.5*math.pi*t+2.1*u)
  scallop=.030*math.sin(math.pi*u)**2*math.sin(4.5*math.pi*t)
  r=rb+.031+ridge+scallop
  zz=z+.09*t*math.sin(math.pi*u)+.030*math.sin(3*math.pi*u+2*t)
  p=(cx+r*math.cos(a),cy+.88*r*math.sin(a),zz)
  vs.append(p)
  if j==N-1:edge.append(p)
for i in range(R-1):
 for j in range(N-1):
  a=i*N+j;fs.append((a,a+1,a+N+1,a+N))
surface("V154_Deep_Purple_Back_Horizontal_Sculptured_Folds",vs,fs,purple,.014)
pathcurve("V154_Back_Carved_Gold_Trim",edge,.0035,gold)

# Move the single gold-thread end to the now physically frozen hand/orb.
for ob in list(bpy.data.objects):
 if ob.name.startswith("V153_Single_Gold_Thread_Actual_3D_Curve"):
  bpy.data.objects.remove(ob,do_unlink=True)
curve=[]
for i in range(147):
 t=i/146;ang=2*math.pi*(1.43*t+.09);r=.342-.070*t
 p=Vector((cx+r*math.cos(ang),cy+.81*r*math.sin(ang),base+.09+1.29*t))
 if t>.86:
  u=(t-.86)/.14;u=u*u*(3-2*u)
  p=p.lerp(ball.location,u)
 curve.append(tuple(p))
pathcurve("V154_One_Gold_Thread_Reaching_Real_Posed_Ball",curve,.0035,gold)

# Before export: remove all animation, cameras and lights from glTF, produce
# truly STATIC sculpture geometry, no side effects from pose on import.
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
scene.frame_set(1)
blend=OUT/"Ariadne_V154_StaticPose_Sculpture_EDITABLE.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
glb=OUT/"Ariadne_V154_TrueFrozenPose_Sculpture_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
 export_cameras=False,export_lights=False,export_animations=False)
assert glb.stat().st_size>1200000
with glb.open("rb") as f:
 header=f.read(20);_,_,_,length,kind=struct.unpack("<4sIIII",header)
 j=json.loads(f.read(length))
assert not j.get("skins"),len(j.get("skins",[]))
assert not j.get("animations"),len(j.get("animations",[]))
assert len(j.get("meshes",[]))>=30
sha=hashlib.sha256(glb.read_bytes()).hexdigest()
# Real roundtrip inspection and image review from frozen exported GLB.
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
assert not [o for o in bpy.data.objects if o.type=="ARMATURE"]
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.render.resolution_x=570;scene.render.resolution_y=755
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format="PNG"
target=Vector((cx,cy,base+.83))
camdata=bpy.data.cameras.new("V154_CanonicalReview")
cam=bpy.data.objects.new("V154_CanonicalReview",camdata)
scene.collection.objects.link(cam);scene.camera=cam
camdata.type="ORTHO";camdata.ortho_scale=2.50
views=[(az,0) for az in (0,30,45,90,135,180,225,270,315,330)]+[(0,90),(0,-90)]
record=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 unit=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 cam.location=target+unit*4.7
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 f=OUT/f"V154_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(f);bpy.ops.render.render(write_still=True)
 record.append({"az":az,"el":el,"file":f.name,
                "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
camdata.ortho_scale=.67
head=Vector((cx,cy,base+1.53))
faces=[]
for az in (0,30,45,90,270,315):
 a=math.radians(az)
 cam.location=head+Vector((math.sin(a),math.cos(a),.05))*3.8
 cam.rotation_euler=(head-cam.location).to_track_quat("-Z","Y").to_euler()
 f=OUT/f"V154_FACE_AZ{az:03d}.png"
 scene.render.filepath=str(f);bpy.ops.render.render(write_still=True)
 faces.append({"az":az,"file":f.name,
               "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
audit={
 "status":"V154_REAL_STATIC_BAKED_POSE_GLB_ENGINEERING_CANDIDATE",
 "true_cc0_baked_anatomy_vertex_count":len(mes.vertices),
 "frozen_pose_from_evaluated_ik_skin":True,
 "wrist_ik_target_errors_m":errors,
 "ball_contact":"WRIST_PROXY_STILL_NOT_5_FINGER_CERTIFIED",
 "old_floating_hair_parts_discarded":len(bad_hair),
 "old_purple_vertical_cloth_panels_discarded":len(removedcloth),
 "new_connected_sculpted_hair_and_braid":True,
 "new_diagonal_front_and_horizontal_folds_back":True,
 "glb_skin_count":len(j.get("skins",[])),
 "glb_animation_count":len(j.get("animations",[])),
 "actual_static_frozen_glb":glb.name,
 "actual_glb_sha256":sha,
 "blender_editable_file":blend.name,
 "rendered_from_reimported_glb":record,
 "face_views_from_reimported_glb":faces,
 "source_art_calibrated_24_angles":False,
 "completed_266x30_art_react_cycles":0,
 "art_final_approved":False}
(OUT/"V154_AUDIT.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print("V154_STATIC_GLB_FINISHED",json.dumps({
 "glb":glb.name,"source_skinned_mesh_vertices":len(mes.vertices),
 "animations":len(j.get("animations",[])),"camera_views":len(record),
 "wrist_errors_m":errors}),flush=True)
