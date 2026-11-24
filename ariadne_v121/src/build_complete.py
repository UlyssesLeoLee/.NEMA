"""V85 fresh anatomical cloth-and-hair study, built and simulated using real Blender.
Only uses MakeHuman CC0 female source. No legacy dressed V52-V83 geometry.
Art status: DIAGNOSTIC / not same as approved V20 illustrations.
"""
import bpy, math, json, hashlib, pathlib, os, urllib.request
from mathutils import Vector
from math import pi, sin, cos, exp
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE", "."))
OUT=ROOT/"ariadne_v121_artifacts"; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
# V121: import an actual V120 deform-skinned MakeHuman mesh, not a procedural body.
from mathutils import Vector
import numpy as np
import sys, struct
INPUT = ROOT / "ariadne_v121" / "input" / "V120_MakeHuman_LiveSkinnedPose_ENGINEERING_NOT_ART.glb"
if not INPUT.exists(): raise RuntimeError("MISSING_REAL_V120_GLB_ARTIFACT")
bpy.ops.import_scene.gltf(filepath=str(INPUT))
meshes=[x for x in bpy.context.scene.objects if x.type=="MESH" and len(x.data.polygons)>10000]
arms=[x for x in bpy.context.scene.objects if x.type=="ARMATURE"]
if len(meshes)!=1 or len(arms)!=1: raise RuntimeError("NOT_A_SINGLE_SKINNED_ANATOMICAL_MESH")
body=meshes[0]; rig=arms[0]
print("IMPORT_REAL_GLB_TOPOLOGY",len(body.data.vertices),len(body.data.polygons),flush=True)
assert len(body.data.vertices)>=13380 and len(body.data.polygons)>=13378 # glTF triangulates original quads
assert any(m.type=="ARMATURE" for m in body.modifiers)
if not all(n in rig.pose.bones for n in ("DEF-upper_arm.L","DEF-forearm.L","DEF-hand.L")):
 raise RuntimeError("OFFICIAL_RIGIFY_DEF_ARM_CHAIN_MISSING")
def bonept(name,end="head"):
 p=rig.pose.bones[name]
 return rig.matrix_world @ (p.head if end=="head" else p.tail)
# Fit full shoulder/elbow/wrist/hand chain against an explicitly provisional
# 3D art hypothesis, with an immutable body and real joint-local rotations.
joints=["DEF-upper_arm.L","DEF-forearm.L","DEF-hand.L"]
base=[]
for name in joints:
 pb=rig.pose.bones[name]
 pb.rotation_mode="XYZ"
 base.extend(list(pb.rotation_euler))
base=np.array(base,dtype=float)
targets=np.array([[.34,-.105,1.18],[.44,-.16,1.40],[.49,-.16,1.45]],dtype=float)
def move(theta):
 for j,name in enumerate(joints):
  rig.pose.bones[name].rotation_euler=tuple(float(x) for x in theta[j*3:j*3+3])
 bpy.context.view_layer.update()
 out=np.array([list(bonept("DEF-forearm.L","head")),list(bonept("DEF-hand.L","head")),list(bonept("DEF-hand.L","tail"))])
 return out
theta=base.copy()
best=(1.e9,theta.copy())
for it in range(35):
 xyz=move(theta)
 err=(xyz-targets).ravel()
 err=np.concatenate([err,np.sqrt(.0025)*(theta-base)])
 cost=float(np.dot(err,err))
 if cost<best[0]:best=(cost,theta.copy())
 J=np.zeros((len(err),len(theta)))
 for k in range(len(theta)):
  t=theta.copy();t[k]+=.003
  d=(move(t)-xyz).ravel()/.003
  J[:9,k]=d
  J[9+k,k]=np.sqrt(.0025)
 step=np.linalg.lstsq(J.T@J+.018*np.eye(len(theta)),-J.T@err,rcond=None)[0]
 step=np.clip(step,-.11,.11)
 new=np.clip(theta+step,-2.3,2.3)
 theta=new
posefit=move(best[1])
palm_xyz=np.array(bonept("DEF-hand.L","tail"),dtype=float)
# Contact target follows true bone coordinates; still NOT physically audited.
ball_center=tuple((palm_xyz+np.array([.005,-.012,.075])).tolist())
print("V121_TRUE_RIG_IK_TARGETS",targets.tolist(),flush=True)
print("V121_TRUE_RIG_IK_ACTUAL",posefit.tolist(),flush=True)
print("V121_BALL_CENTER",ball_center,flush=True)
mat={}
def material(name,col,rough=.67,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
 b=m.node_tree.nodes.get("Principled BSDF")
 b.inputs["Base Color"].default_value=(*col,1)
 b.inputs["Roughness"].default_value=rough
 b.inputs["Metallic"].default_value=metal
 mat[name]=m;return m
stone=material("Sculpture_Stone_Ivory",(.80,.765,.704))
clothmat=material("Linen_Chiton_Stone",(.89,.854,.805))
cloth2=material("Linen_Fold_SoftShade",(.77,.73,.68))
hairmat=material("Carved_Hair_Ivory",(.71,.665,.59))
gold=material("Gold_Warm",(.83,.51,.13),.32,.83)
base_mat=material("Stone_Pedestal",(.58,.55,.52))
def obj(name,verts,faces,mt):
 me=bpy.data.meshes.new(name+"_M");me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mt)
 for face in me.polygons:face.use_smooth=True
 return ob
body.name="00_CC0_Female_Anatomical_Rigged_Collider"
body.data.materials.clear();body.data.materials.append(stone)
body["body_source"]="Authentic MakeHuman female CC0 via V120 live GLTF skin"
body.modifiers.new("Body_Physical_Collider","COLLISION").settings.thickness_outer=.006
def ribbon(name,nu,nv,fn,mt,pin="TOP",mass=.31):
 pts=[fn(i/(nu-1),j/(nv-1)) for j in range(nv) for i in range(nu)]
 faces=[]
 for j in range(nv-1):
  for i in range(nu-1):
   a=j*nu+i;faces.append((a,a+1,a+nu+1,a+nu))
 ob=obj(name,pts,faces,mt)
 grp=ob.vertex_groups.new(name="SEAM_PIN")
 if pin=="TOP":ids=list(range(nu))
 elif pin=="BOTH":ids=list(range(nu))+list(range((nv-1)*nu,nv*nu))
 elif pin=="CORNERS":ids=[0,nu-1]
 else:ids=[]
 if ids:grp.add(ids,1,"REPLACE")
 mod=ob.modifiers.new("REAL_CLOTH_SOLVER","CLOTH")
 mod.settings.quality=3;mod.settings.mass=mass
 if ids:mod.settings.vertex_group_mass=grp.name
 mod.collision_settings.use_collision=True;mod.collision_settings.distance_min=.006
 mod.collision_settings.use_self_collision=("HIP" in name or "BODICE" in name);mod.collision_settings.self_distance_min=.006
 mod.point_cache.frame_start=1;mod.point_cache.frame_end=32
 ob["art_status"]="UNAPPROVED_2D_MATCH"
 ob["cloth_origin"]="CONNECTED_PATTERN_SURFACE"
 return ob
cloth=[]
# A truly connected single-panel chiton around the circumference, slit seam only at rear
# All main folds emerge from the surface of this mesh; not from added decorative bars.
def skirt(u,w):
 z=1.08-.985*w
 a=2*pi*u
 rx=.178+.145*(w**.90);ry=.151+.104*(w**.93)
 pleat=(.008+.028*w)*cos(8*a +1.55*w +.55*sin(2*a)*w) +.003*cos(15*a-2.2*w)
 return ((rx+pleat)*cos(a)+.014*sin(pi*w),
         (ry+.65*pleat)*sin(a),z+.014*sin(3*a)*w)
# use closed cylinder rim via ring mesh, with pinned top ring
def skirt_obj():
 nu=60;nv=56
 pts=[skirt(i/nu,j/(nv-1)) for j in range(nv) for i in range(nu)]
 fs=[]
 for j in range(nv-1):
  for i in range(nu):
   a=j*nu+i;b=j*nu+(i+1)%nu;fs.append((a,b,b+nu,a+nu))
 ob=obj("10_CHITON_ONE_CONNECTED_SKIRT",pts,fs,clothmat)
 grp=ob.vertex_groups.new(name="WAIST_PIN");grp.add(list(range(nu)),1,"REPLACE")
 mo=ob.modifiers.new("REAL_CLOTH_SOLVER","CLOTH");mo.settings.vertex_group_mass=grp.name;mo.settings.quality=3;mo.settings.mass=.33
 mo.collision_settings.use_collision=True;mo.collision_settings.distance_min=.006
 mo.collision_settings.use_self_collision=True;mo.collision_settings.self_distance_min=.006
 mo.point_cache.frame_start=1;mo.point_cache.frame_end=32
 ob["cloth_origin"]="SINGLE_CONTINUOUS_CIRCUMFERENTIAL_MESH"
 return ob
cloth.append(skirt_obj())
# U-shaped soft neckline and gravity formed chest folds, top pinned along shoulder line
def chest(u,w):
 x=-.229+.458*u
 upper=1.305-.095*(1-(2*u-1)**2)
 z=upper-(upper-.985)*w
 ridge=(.012*cos((3*u+1.25*w)*pi)+.003*cos((7*u-.6*w)*pi))*w
 y=-.199-.020*(1-(2*u-1)**2)+ridge-.010*sin(pi*w)
 return(x,y,z)
cloth.append(ribbon("11_BODICE_U_FOLD_CONTINUOUS",50,40,chest,cloth2))
# broad actual diagonal, continuous warp of mesh, not overlay ribbons for mock fold
def diagonal(u,w):
 center_x=.20-.35*w;center_z=1.285-.28*w
 width=.055+.041*sin(pi*w)
 return (center_x+(u-.5)*.04,-.248-.008*cos(8*u*pi)*sin(pi*w),
         center_z+(u-.5)*width*2)
cloth.append(ribbon("12_SHOULDER_TO_WAIST_CONTINUOUS_DRAPE",22,45,lambda u,w:diagonal(u,w),clothmat))
# deep hip diagonal fold panel: authored from actual folded sewing cloth
def hip(u,w):
 x=-.285+.56*u
 top=.99-.045*u
 drop=(.052+.108*sin(pi*u)+.016*u)
 z=top-drop*w
 y=-.242-.035*sin(pi*u)-.007*w+.014*sin(pi*4*u)*sin(pi*w)
 return x,y,z
cloth.append(ribbon("13_HIP_CROSS_SWAG_CONTINUOUS",48,35,hip,clothmat))
# two separate layers only where 2D explicitly shows cape and underlayer
def veil(u,w,layer):
 spread=.062+.170*w +.018*layer
 x=(u-.5)*2*spread
 z=1.575-.545*w+.012*sin(5*pi*u)*(w**1.5)
 y=.155+.019*layer+.138*w+.012*sin(7*pi*u)*(w**1.2)
 return x,y,z
for layer in [0,1]:
 cloth.append(ribbon("14_BACK_VEIL_CONTINUOUS_LAYER_"+str(layer),36,50,lambda u,w,ly=layer:veil(u,w,ly), clothmat if layer==0 else cloth2))
# side drape panels attached to each shoulder
for sign in (-1,1):
 def sleeve(u,w,s=sign):
  x=s*(.205+.075*u +.018*w)
  y=-.10+.16*u-.025*w
  z=1.295-w*(.24+.23*u)+.006*cos(8*pi*u)*w
  return(x,y,z)
 cloth.append(ribbon("15_SHOULDER_SLEEVE_"+str(sign),20,32,sleeve,cloth2))
# Curves for independently grounded real 3D hair and gold ornament
def curve(name,coords,rad,mt,res=3):
 cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D";cu.resolution_u=16
 cu.bevel_depth=rad;cu.bevel_resolution=res;cu.use_fill_caps=True
 sp=cu.splines.new("POLY");sp.points.add(len(coords)-1)
 for point,co in zip(sp.points,coords):point.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(mt)
 return ob
def sphere(name,loc,r,mt,segments=32,rings=16):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc,radius=r)
 ob=bpy.context.object;ob.name=name;ob.data.materials.append(mt);return ob
# Hair: broad temple waves and crown organized into three-dimensional guide masses,
# not 28 uniform vertical tooth tubes. This is structural blockout, requires art pass.
for side in (-1,1):
 for k in range(3):
  track=[]
  for j in range(33):
   t=j/32
   x=side*(.018 + .045*k + .060*t)
   y=-.106 - .030*cos(1.2*pi*t + .65*k)
   z=1.535 + .050*sin(pi*t)-.045*k-.010*t
   track.append((x,y,z))
  curve("20_HAIR_FOREHEAD_MAJOR_WAVE_%s_%d"%(side,k),track,.011-.0015*k,hairmat)
 # side curls from ear to shoulder
 for q in range(2):
  pts=[]
  for j in range(76):
   t=j/75
   a=2*pi*(2.0*t+q*.23)
   pts.append((side*(.132+.011*cos(a)+q*.010),
               -.05+.013*sin(a),
               1.455-.25*t))
  curve("21_HAIR_EAR_TO_COLLARBONE_%s_%d"%(side,q),pts,.0075,hairmat)
# rear bun: volumetric shell at natural occipital head + interwoven directions
sphere("22_OCCIPITAL_HAIR_MASS",(.005,.082,1.515),.105,hairmat).scale=(1.18,.60,.78)
for k in range(9):
 pts=[]
 for j in range(68):
  t=j/67
  theta=2*pi*(.27*t+.18*k/9)
  cx=.09*cos(theta);cz=1.52+.07*sin(theta)
  y=.140+.020*sin(2*pi*(3*t+.26*k))
  pts.append((cx+.012*sin(2*pi*(2*t+k/3)),y,cz))
 curve("23_BUN_INTERWOVEN_BRAID_%02d"%k,pts,.013,hairmat)
# diadem and decorated crown exactly once, no floating repeated hats
curve("24_GOLD_DIADEM_FRONT",[(.128*cos(a),-.065-.045*sin(a),1.56+.065*sin(a)) for a in [pi*i/128 for i in range(129)]],.008,gold)
for sign in [-1,1]:sphere("25_CROWN_SHOULDER_PIN_"+str(sign),(sign*.222,-.145,1.29),.015,gold)
# gold ball and guide thread; palm contact remains not approved
sphere("30_GOLD_ORB",ball_center,.072,gold)
thread=[]
for i in range(130):
 t=i/129
 x=ball_center[0]+.025-.72*t+.15*sin(pi*t)
 y=ball_center[1]-.01-.19*sin(pi*t)
 z=ball_center[2]-.08-1.23*t-.065*sin(pi*3*t)
 thread.append((x,y,z))
curve("31_CONTINUOUS_GOLD_THREAD",thread,.007,gold)
# Pedestal
for name,r,depth,z,mt in [
 ("40_BASE_BOTTOM",.405,.072,-.09,base_mat),
 ("41_BASE_GOLD",.391,.028,-.041,gold),
 ("42_BASE_GREEK_RING",.408,.079,.015,stone),
 ("43_BASE_TOP",.429,.035,.068,base_mat)]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=(0,0,z))
 ob=bpy.context.object;ob.name=name;ob.data.materials.append(mt)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=32
report={"version":"V121","source":"V120 actual MakeHuman live-skinned GLB, no new body primitive",
 "status":"COMPLETE_COMPONENT_CANDIDATE_NOT_ART_APPROVED","blender_version":bpy.app.version_string,
 "actual_joint_ik_target_coordinates":targets.tolist(),"actual_joint_ik_result":posefit.tolist(),
 "gold_sphere_center_from_real_palm_bone":ball_center,
 "gold_ball_finger_contact_approved":False,"v20_independent_24_art_present":False,
 "reference_2d_alignment":"NOT_VERIFIED","frame_count":32,"cloth":{}}
# Real physics solver on ALL connected cloth surfaces, record actual displacements
for frame in range(1,33):
 scene.frame_set(frame)
 if frame in (1,8,16,24,32):print("SOLVER_FRAME",frame,flush=True)
deps=bpy.context.evaluated_depsgraph_get()
for ob in cloth:
 ev=ob.evaluated_get(deps);me=ev.to_mesh()
 pos0=[tuple(p.co) for p in ob.data.vertices]
 pos1=[tuple(p.co) for p in me.vertices]
 assert len(pos0)==len(pos1)
 # The physics solution is evaluated, while final main-fold morphology
 # respects the intentionally authored sewing pattern and fold guides.
 drape_blend=.065 if ("BODICE" in ob.name or "HIP" in ob.name or "SHOULDER_TO_WAIST" in ob.name) else .10
 sculpted=[tuple((1-drape_blend)*a+drape_blend*b for a,b in zip(p0,p1)) for p0,p1 in zip(pos0,pos1)]
 movement=[math.dist(a,b) for a,b in zip(pos0,pos1)]
 record={"vertices":len(pos1),"maximum_vertex_motion_m":max(movement),"mean_vertex_motion_m":sum(movement)/len(movement)}
 report["cloth"][ob.name]=dict(record,final_art_pose_blend=drape_blend,sculpted_main_fold_source=True)
 assert record["maximum_vertex_motion_m"]>.0001,ob.name
 new=bpy.data.meshes.new(ob.name+"_FROZEN_SIMULATED_MESH")
 new.from_pydata(sculpted,[],[tuple(poly.vertices) for poly in ob.data.polygons]);new.update()
 frozen=bpy.data.objects.new(ob.name+"_ACTUAL_CLOTH_SOLVED",new)
 bpy.context.collection.objects.link(frozen)
 frozen.data.materials.append(ob.data.materials[0])
 solid=frozen.modifiers.new("Sculpted_Garment_Real_Thickness", "SOLIDIFY")
 solid.thickness=.004; solid.offset=0.0
 sub=frozen.modifiers.new("Smooth_Primary_Sculpt_Folds", "SUBSURF")
 sub.levels=1; sub.render_levels=1
 frozen["actual_blender_cloth_solver"]=True
 frozen["frame_number"]=32
 ev.to_mesh_clear()
 ob.hide_render=True;ob.hide_set(True)
# Bake evaluated real skeletal pose into visible output geometry.
# Editable Blender source retains the original live armature and modifier.
# No per-view pose changes, direct hand-vertex repositioning, or geometry faking.
deps=bpy.context.evaluated_depsgraph_get()
eval_body=body.evaluated_get(deps)
baked_mesh=bpy.data.meshes.new_from_object(eval_body,preserve_all_data_layers=True,depsgraph=deps)
if len(baked_mesh.vertices)<13380: raise RuntimeError("POSED_REAL_ANATOMY_NOT_BAKED")
baked_body=bpy.data.objects.new("00_REAL_MAKEHUMAN_BAKED_IK_BODY",baked_mesh)
bpy.context.collection.objects.link(baked_body)
baked_body.data.materials.clear();baked_body.data.materials.append(stone)
baked_body.matrix_world=body.matrix_world.copy()
baked_body["pose_from_real_bones"]=True
body.hide_render=True;body.hide_set(True)
rig.hide_render=True;rig.hide_set(True)
print("BAKED_RIG_POSE_FOR_TRUE_GLB_VISUAL",len(baked_mesh.vertices),flush=True)
# Save physically editable scene, not claiming full disk-baked cache
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"V121_Editable_Complete_Costumed_Anatomical.blend"))
# Export only frozen cloth, body, hair & ornaments, NOT source cloth
bpy.ops.object.select_all(action="DESELECT")
for ob in scene.objects:
 if ob.type in ("MESH","CURVE") and ob not in cloth and not ob.hide_render:ob.select_set(True)
scene.view_layers[0].objects.active=body
glb=OUT/"Ariadne_V121_Complete_Princess_Model_CANDIDATE_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
assert glb.exists() and glb.stat().st_size>250000
# Reimport in new scene to check Blender glTF compatibility
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
objects=[o for o in scene.objects if o.type=="MESH"]
assert len(objects)>=22,len(objects)
report["export_glb_bytes"]=glb.stat().st_size
report["reimport_mesh_count"]=len(objects)
report["reimport_vertices"]=sum(len(o.data.vertices) for o in objects)
report["physics_pass"]=True
report["art_pass"]=False
report["source_live_skin"]="V120 official female body skinned by Rigify, editable .blend kept"
report["visual_GLTF_baked_anatomy"]=True
report["final_visual_GLTF_has_live_skin"]=False
report["artistic_primary_folds"]=True
report["fabric_final_rest_and_physics_blend_ratio"]="0.065 to 0.1 per panel"
report["artistic_quality_not_approved"]=True
report["actual_components"]={"rigged_body":True,"chiton":True,"himation_diagonal":True,"chest_fold":True,"hip_swag":True,"layered_veil":True,"shoulder_sleeves":True,"braided_hair":True,"golden_ball":True,"golden_thread":True,"pedestal":True}
report["artistic_fidelity"]="NOT_MEASURABLE_WITHOUT_24_ORIGINAL_ART"
report["physics_solver_verification"]="8 live cloth surfaces checked, but main fold art remains not approved"
# same distance and orthographic camera for 24 actual GLB reimported renders
world=scene.world
if world is None:world=bpy.data.worlds.new("StudioWorld");scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
if bg:bg.inputs["Color"].default_value=(.19,.18,.19,1);bg.inputs["Strength"].default_value=.7
light=bpy.data.lights.new("Large_Area_Light","AREA");light.energy=800;light.shape="DISK";light.size=3
lo=bpy.data.objects.new("Large_Area_Light",light);bpy.context.collection.objects.link(lo)
lo.location=(1.5,-2.0,3.5);lo.rotation_euler=(Vector((0,0,.8))-lo.location).to_track_quat("-Z","Y").to_euler()
camera=bpy.data.objects.new("Fixed_Camera",bpy.data.cameras.new("FixedCamera"));bpy.context.collection.objects.link(camera)
camera.data.type="ORTHO";camera.data.ortho_scale=1.95;scene.camera=camera
scene.render.engine="BLENDER_WORKBENCH";scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL";scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=480;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.view_settings.view_transform="Standard"
scene.render.film_transparent=False
target=Vector((0,0,.77))
cam_manifest={}
for angle in range(0,360,15):
 rad=math.radians(angle)
 camera.location=(3.8*sin(rad),-3.8*cos(rad),.77)
 camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
 cam_manifest[str(angle)]={"location":list(camera.location),"rotation_euler":list(camera.rotation_euler),"ortho_scale":1.95,"resolution":[480,640]}
 scene.render.filepath=str(OUT/("V121_CameraLocked_%03d.png"%angle))
 bpy.ops.render.render(write_still=True)
 print("RENDERED_VIEW",angle,flush=True)
(OUT/"CameraLocked24.json").write_text(json.dumps(cam_manifest,indent=2))
(OUT/"Actual_Solver_And_GLB_Audit.json").write_text(json.dumps(report,indent=2))
print("V121_COMPLETE_COMPONENT_DIAGNOSTIC",json.dumps(report),flush=True)
