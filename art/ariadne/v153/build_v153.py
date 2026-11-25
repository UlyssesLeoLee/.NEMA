"""Ariadne V153 true physical GLB rebuild from V152 priorities:
(1) whole-body hands/ball pose, (2) preserve unobstructed face and rooted hair,
(3) reconstruct side/back tailoring with true sculpted surfaces and gold trims.
Sources: original user-approved 8-view art, official MakeHuman CC0 weighted skeleton.
This is a real Blender build and multi-camera art candidate, NOT 7980 proven ReActs.
"""
import bpy, math, runpy, hashlib, json, traceback
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v149/build_v149.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v153"
OUT.mkdir(parents=True,exist_ok=True)
# V149 rebuild leaves the true reimported-GLB scene.
scene=bpy.context.scene
body=[o for o in bpy.data.objects if o.type=="MESH" and "Anatomy" in o.name]
armatures=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(body)==1 and len(armatures)==1,(len(body),len(armatures))
body=body[0];rig=armatures[0]
bcoords=[body.matrix_world@Vector(v) for v in body.bound_box]
cx=sum((min(p.x for p in bcoords),max(p.x for p in bcoords)))/2
cy=sum((min(p.y for p in bcoords),max(p.y for p in bcoords)))/2
base=min(p.z for p in bcoords)
height=max(p.z for p in bcoords)-base
print("V153_BODY_FRAME",cx,cy,base,height,flush=True)
def mat(name,color,metal=0,rough=.68):
 m=bpy.data.materials.new(name)
 m.use_nodes=True;m.diffuse_color=(*color,1)
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*color,1)
 bs.inputs["Metallic"].default_value=metal
 bs.inputs["Roughness"].default_value=rough
 return m
white=mat("V153_Authentic_Chiton_Carved_Marble",(.86,.83,.77),0,.54)
violet=mat("V153_Purple_Royal_Himation_Sculpture",(.25,.105,.32),0,.66)
violet_edge=mat("V153_Royal_Layer_Shadow",(.15,.065,.21),0,.73)
gold=mat("V153_Gold_Inlay",(.73,.46,.19),.7,.34)
hair=mat("V153_Layered_Bronze_Hair",(.39,.27,.18),.16,.59)

def make_surface(name,vertices,quads,material,solid=.004,sub=1):
 mesh=bpy.data.meshes.new(name+"_mesh")
 mesh.from_pydata(vertices,[],quads);mesh.update()
 o=bpy.data.objects.new(name,mesh)
 bpy.context.collection.objects.link(o)
 mesh.materials.append(material)
 for pol in mesh.polygons:pol.use_smooth=True
 if solid:
  m=o.modifiers.new("TrueLayeredClothThickness","SOLIDIFY");m.thickness=solid
 if sub:
  m=o.modifiers.new("FoldSculptSubsurf","SUBSURF");m.levels=sub
 return o

def wire(name,points,r,material,closed=False):
 cu=bpy.data.curves.new(name+"_curve","CURVE");cu.dimensions="3D"
 cu.resolution_u=14;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new("BEZIER");sp.bezier_points.add(len(points)-1)
 for bp,p in zip(sp.bezier_points,points):
  bp.co=p;bp.handle_left_type="AUTO";bp.handle_right_type="AUTO"
 sp.use_cyclic_u=closed
 obj=bpy.data.objects.new(name,cu)
 bpy.context.collection.objects.link(obj);cu.materials.append(material)
 return obj

# 1. Reject old procedurally hanging costume and its trim in entirety.
old_garment_prefixes=(
 "V147_White_Chiton_CutGore_","V147_White_Chiton_Crossed_Bodice",
 "V147_Amethyst_Himation_","V147_Purple_Waist_",
 "V147_Gold_Front_Hem","V147_Gold_Back_Hem")
deleted=[]
for o in list(bpy.data.objects):
 if any(o.name.startswith(p) for p in old_garment_prefixes):
  deleted.append(o.name)
  bpy.data.objects.remove(o,do_unlink=True)
assert len(deleted)>=20,len(deleted)
print("V153_OLD_CLOTH_REMOVED",len(deleted),flush=True)
# 2. Armature-driven whole-arm pose. The ball-side is determined by the
# existing sphere's proximity, not an arbitrary 'which side is left' guess.
orb=[o for o in bpy.data.objects if o.type=="MESH" and "Golden_Orb_Actual_Sphere" in o.name]
assert len(orb)==1
orb=orb[0]
def wrist_position(side):
 b=rig.pose.bones["wrist."+side]
 return rig.matrix_world@b.tail
wpos={side:wrist_position(side) for side in ("L","R")}
ball_side=min(("L","R"),key=lambda s:(wpos[s]-orb.location).length)
rest_side="R" if ball_side=="L" else "L"
print("V153_WRISTS",ball_side,list(wpos[ball_side]),rest_side,list(wpos[rest_side]),flush=True)
goals=[]
for side,is_orb in ((ball_side,True),(rest_side,False)):
 pb=rig.pose.bones["wrist."+side]
 current=wrist_position(side)
 xsign=-1 if current.x<cx else 1
 # For ball, bring elbow inward to a bent natural arc with palm at chest height.
 # For relaxed arm, place hand near the side of hip, rather than T-pose.
 aim=Vector((cx+xsign*(.245 if is_orb else .175),
              cy+(.14 if is_orb else .072),
              base+(1.36 if is_orb else .835)))
 goal=bpy.data.objects.new("V153_RealPose_IK_"+side,None)
 scene.collection.objects.link(goal);goal.location=aim;goals.append(goal)
 ik=pb.constraints.new("IK")
 ik.target=goal;ik.chain_count=5;ik.iterations=240;ik.use_rotation=False
bpy.context.view_layer.update()
error_before_bake={s:float((wrist_position(s)-next(g.location for g in goals if g.name.endswith("_"+s))).length) for s in ("L","R")}
# Important: bake the global solved bone pose so GLB does not require
# Blender-only IK target objects to reproduce the silhouette.
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
scene.frame_set(1)
bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,only_selected=True,
                 visual_keying=True,clear_constraints=True,use_current_action=True,
                 bake_types={"POSE"})
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()
pose_error={s:float((wrist_position(s)-next(g.location for g in goals if g.name.endswith("_"+s))).length) for s in ("L","R")}
print("V153_IK_POSE_ERRORS",pose_error,flush=True)
# Correct ball to lie above the actual palm joint; this remains a wrist
# articulation proxy, NOT yet certified 5-finger palmar physics contact.
palmar=wrist_position(ball_side)
ball_center=palmar+Vector((0,.025,.073))
orb.location=ball_center
orb["V153_contact_status"]="WRIST_BASED_PROXY_NOT_PALM_CERTIFIED"
for g in goals:bpy.data.objects.remove(g,do_unlink=True)

# 3. Designer-sculpted chiton uses a continuous 3D connected surface with
# asymmetrically warped directional folds; NOT independent radial paper gores.
# 192 angular subdivisions and 48 height rings establish visible 3D folds.
N=192;R=48
v=[];f=[]
def skirt_radius(z,theta):
 t=max(0,min(1,(base+1.075-z)/.97))
 waist=.164;hip=.215;hem=.313
 r=(waist+(hip-waist)*min(t/.28,1)) if t<.28 else (hip+(hem-hip)*((t-.28)/.72)**1.0)
 # Directionally nonperiodic broad carved folds, carrying around side/back.
 wave=(.006+.023*t**.9)*(math.sin(13*theta+.6*t)+.30*math.sin(21*theta-1.7*t))
 ridge=(.004+.015*t**1.4)*math.sin(7*theta+2*t)
 return r+wave+ridge
for i in range(R):
 t=i/(R-1)
 z=base+1.075-t*.96
 for j in range(N):
  th=2*math.pi*j/N
  r=skirt_radius(z,th)
  v.append((cx+r*math.cos(th),cy+.83*r*math.sin(th),z+(.004+.013*t)*math.sin(5*th+1.8*t)))
for i in range(R-1):
 for j in range(N):
  a=i*N+j;b=i*N+(j+1)%N
  f.append((a,b,b+N,a+N))
make_surface("V153_White_Royal_Chiton_Sculpted_HemAndMultiFold",v,f,white,.005,1)
# white upper bodice is an actual continuous form, follows anatomical upper-torso
N=128;R=23;v=[];f=[]
for i in range(R):
 z=base+1.038+i/(R-1)*.385
 t=i/(R-1)
 r=.17+.052*math.sin(math.pi*t)
 for j in range(N):
  a=2*math.pi*j/N
  pleat=.010*math.cos(9*a+3*t)+.006*math.sin(14*a-2*t)
  v.append((cx+(r+pleat)*math.cos(a),
            cy+.81*(r+pleat)*math.sin(a),
            z+.005*math.cos(5*a+3*t)))
for i in range(R-1):
 for j in range(N):
  a=i*N+j;b=i*N+(j+1)%N
  f.append((a,b,b+N,a+N))
make_surface("V153_Structural_Bodice_White_Chiton",v,f,white,.004,1)
# Sculptural asymmetric fabric crossing chest: design path anchored to shoulder
# and banded around waist. Vertex columns are fabric width and anatomical depth.
def fabric_path(name,path,widths,ma,radialwave=.009):
 U=33;verts=[];faces=[]
 for i,(px,py,pz) in enumerate(path):
  w=widths[i]
  tangent=Vector(path[min(i+1,len(path)-1)])-Vector(path[max(i-1,0)])
  # side vector horizontal perpendicular to 2D pathway, forming free 3D pleats
  axis=Vector((-tangent.z,0,tangent.x))
  if axis.length<.001:axis=Vector((1,0,0))
  axis.normalize()
  for j in range(U):
   u=2*j/(U-1)-1
   d=(.012+.010*i/max(len(path)-1,1))*math.cos(4*math.pi*u+.18*i)
   verts.append((px+axis.x*w*u*.5,
                 py+d+radialwave*math.cos(2*math.pi*u+.3*i),
                 pz+axis.z*w*u*.5))
 for i in range(len(path)-1):
  for j in range(U-1):
   a=i*U+j;faces.append((a,a+1,a+U+1,a+U))
 return make_surface(name,verts,faces,ma,.007,2)
def interpolate(path,count):
 result=[]
 for j in range(count):
  t=j/(count-1)*(len(path)-1);i=min(int(t),len(path)-2);u=t-i
  result.append(tuple((1-u)*a+u*b for a,b in zip(path[i],path[i+1])))
 return result
strap=interpolate([
 (cx+.09,cy+.09,base+1.445),
 (cx+.01,cy+.205,base+1.32),
 (cx-.12,cy+.17,base+1.13),
 (cx-.12,cy+.13,base+1.057)],30)
fabric_path("V153_White_Chiton_Cross_Chest_Folds",strap,[.13+.04*math.sin(math.pi*i/29) for i in range(30)],white)

# 4. Volumetric royal himation, authored as anchored cloak with continuous
# torso-to-hip wrapping and actual side/back 3D thickness, not 2D hanging sheets.
# Main back mantle follows true circumferential body surface.
N=110;R=54;verts=[];quad=[]
for i in range(R):
 t=i/(R-1);z=base+1.475-t*1.32
 rbase=skirt_radius(max(z,base+.115),math.pi) if z<base+1.075 else .188
 # upper shoulder start and back sweep: vary width according to drape length
 theta_lo=2.86-.25*math.sin(math.pi*t)
 theta_hi=6.04-.70*t
 for j in range(N):
  u=j/(N-1)
  th=theta_lo+(theta_hi-theta_lo)*u
  # Actual sculptural major folds: long, asymmetrical ridges down the back
  wave=(.017+.034*t)*math.sin(5.5*math.pi*u+1.0*t)
  wave+=(.009+.018*t)*math.sin(12*math.pi*u+2.3*t)
  r=rbase+.040+wave+.025*t
  # Upper mantle pinned at shoulder; lower fabric falls around hip
  x=cx+r*math.cos(th)
  y=cy+.84*r*math.sin(th)
  zz=z+.020*t*math.sin(4*math.pi*u)+.015*u*t
  verts.append((x,y,zz))
for i in range(R-1):
 for j in range(N-1):
  a=i*N+j;quad.append((a,a+1,a+N+1,a+N))
make_surface("V153_Purple_Himation_Sculpted_Back_Cloak",verts,quad,violet,.010,1)
# Front sweeping diagonal purple shoulder-to-waist overfold that actually
# wraps side and transitions into back, layered on top of primary cloak.
N=50;R=58;verts=[];quad=[];gold_edge=[]
for i in range(R):
 t=i/(R-1)
 z=base+1.445-1.21*t
 # upper pin at right shoulder transitions around waist to side of hip
 theta_mid=.61+2.2*t
 theta_width=(.28+.75*math.sin(math.pi*(t*.82+.08)))
 for j in range(N):
  u=j/(N-1)-.5
  th=theta_mid+theta_width*u
  rbase=.205 if z>=base+1.075 else skirt_radius(z,th)
  # Furrowed diagonal fold shoulders -> pelvis -> side hanging
  ridge=(.015+.029*t)*math.sin(6*math.pi*(u+.5)+4*t)
  r=rbase+.039+ridge
  zvertex=z+.10*u*math.sin(math.pi*t)+.025*(u**2)*math.sin(7*t)
  p=(cx+r*math.cos(th),cy+.85*r*math.sin(th),zvertex)
  verts.append(p)
  if j==0:gold_edge.append(p)
for i in range(R-1):
 for j in range(N-1):
  a=i*N+j;quad.append((a,a+1,a+N+1,a+N))
make_surface("V153_Purple_Himation_Side_Integrated_Royal_Swath",verts,quad,violet,.012,2)
wire("V153_Golden_Embroidered_RealHem_Edge",gold_edge,.004,gold)
# Secondary front low violet sweep, anchored to same waist and moves toward
# back/side; designed drapery rather than independent detached panels.
N=45;R=35;verts=[];quads=[]
for i in range(R):
 t=i/(R-1);z=base+.90-.68*t;theta_mid=1.85+1.62*t
 for j in range(N):
  u=j/(N-1)-.5;th=theta_mid+.76*u
  rb=skirt_radius(z,th)+.050
  r=rb+(.009+.023*t)*math.sin(5*math.pi*u+2*t)
  verts.append((cx+r*math.cos(th),cy+.84*r*math.sin(th),z+.055*u*math.sin(math.pi*t)))
for i in range(R-1):
 for j in range(N-1):
  a=i*N+j;quads.append((a,a+1,a+N+1,a+N))
make_surface("V153_Purple_Hip_Sculptural_OverlapLayer",verts,quads,violet_edge,.007,1)
# Royal waist piping and carved clasp.
for z,rad in ((base+1.068,.176),(base+1.085,.184)):
 wire("V153_Gold_Waist_Band_"+str(round(z,3)),[
 (cx+rad*math.cos(2*math.pi*i/60),
  cy+.82*rad*math.sin(2*math.pi*i/60),z+.004*math.sin(2*math.pi*i/60))
 for i in range(60)],.003,gold,closed=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=14,radius=.029,
 location=(cx-.105,cy+.197,base+1.107))
clasp=bpy.context.object;clasp.name="V153_Gold_Waist_Binding_Clasp"
clasp.data.materials.append(gold)

# 5. Finish hair at anatomically safe scalp. The V149 posterior roots pass the
# central face guard. Add side head-braids only behind cheek/ear hemisphere.
for side in (-1,1):
 for i in range(7):
  ps=[]
  for j in range(28):
   t=j/27
   a=math.pi*(.28+.45*t)
   x=cx+side*(.100+.005*math.cos(5*t))*math.sin(a)
   y=cy-.051-.017*math.sin(math.pi*t)+.004*i
   z=base+1.667-.18*t-.012*i
   ps.append((x,y,z))
  wire(f"V153_EarBack_ArtDirected_Braid_{side}_{i}",ps,.0047,hair)
# Back braided bundle curves with true 3D mass: no front-face vertices.
for i in range(16):
 ps=[]
 for j in range(46):
  t=j/45;ang=math.pi*2*(3.2*t+i/16)
  ps.append((cx+.039*math.cos(ang),
             cy-.125-.032*math.sin(ang),
             base+1.54-.47*t))
 wire(f"V153_Royal_Deep_Back_Braid_{i:02d}",ps,.0048,hair)

# 6. Rebuild ONE continuous gold thread ending on the actual, retargeted orb.
for o in list(bpy.data.objects):
 if o.name.startswith("V147_ONE_Continuous_3D_Gold_Thread"):
  bpy.data.objects.remove(o,do_unlink=True)
curve=[]
for i in range(125):
 t=i/124;ang=2*math.pi*(1.52*t+.07)
 r=(.345-.075*t)
 z=base+.12+1.23*t
 p=Vector((cx+r*math.cos(ang),cy+.83*r*math.sin(ang),z))
 if t>.875:
  w=(t-.875)/.125
  w=w*w*(3-2*w)
  p=p.lerp(ball_center,w)
 curve.append(tuple(p))
wire("V153_Single_Gold_Thread_Actual_3D_Curve",curve,.0038,gold)
# Drop all legacy technical targets before export.
for o in list(bpy.data.objects):
 if o.type=="EMPTY" and "Target" in o.name:
  bpy.data.objects.remove(o,do_unlink=True)

# 7. Save editable BLEND, actual GLB, roundtrip and camera evidence.
scene.frame_set(1)
bpy.context.view_layer.update()
blend=OUT/"Ariadne_V153_Pose_Hair_SideCloth_Sculpt.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
glb=OUT/"Ariadne_V153_Real_Sculpture_Engineering_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                          export_cameras=False,export_lights=False)
assert glb.stat().st_size>1500000
glbsha=hashlib.sha256(glb.read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
assert len([o for o in bpy.data.objects if o.type=="ARMATURE"])==1
required_names=("V153_Purple_Himation_Sculpted_Back_Cloak",
 "V153_Purple_Himation_Side_Integrated_Royal_Swath",
 "V153_Purple_Hip_Sculptural_OverlapLayer",
 "V153_White_Royal_Chiton_Sculpted_HemAndMultiFold",
 "V153_Single_Gold_Thread_Actual_3D_Curve")
names=[o.name for o in bpy.data.objects]
assert all(any(n.startswith(p) for n in names) for p in required_names),required_names

scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.render.resolution_x=640
scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
target=Vector((cx,cy,base+.84))
camdata=bpy.data.cameras.new("V153_Orthographic_Review")
cam=bpy.data.objects.new("V153_Orthographic_Review",camdata)
scene.collection.objects.link(cam);scene.camera=cam
camdata.type="ORTHO";camdata.ortho_scale=2.45
views=[(a,0) for a in (0,30,45,60,90,120,150,180,210,240,270,300,315,330)]+[(0,90),(0,-90)]
photos=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 unit=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 cam.location=target+unit*4.5
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V153_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 photos.append({"az":az,"el":el,"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
camdata.ortho_scale=.65
head=Vector((cx,cy,base+1.52))
headviews=[]
for az in (0,30,45,90,270,315):
 a=math.radians(az)
 cam.location=head+Vector((math.sin(a),math.cos(a),.06))*4
 cam.rotation_euler=(head-cam.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V153_FACE_AZ{az:03d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 headviews.append({"az":az,"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
audit={
 "status":"V153_REAL_REBUILT_GLB_ART_NOT_APPROVED",
 "source":"V149 official CC0 anatomy and real rig, art target original eight-view board",
 "old_garment_objects_discarded":len(deleted),
 "pose_solved_using_true_armature_and_baked_IK":True,
 "ball_arm_side":ball_side,
 "relaxed_arm_side":rest_side,
 "postbake_ik_wrist_target_errors_m":pose_error,
 "ball_contact":"WRIST_PROXY_NOT_FINGER_SUPPORT_CERTIFIED",
 "whole_body_still_requires_art_review":True,
 "rebuilt_white_sculptural_shells":2,
 "rebuilt_purple_wrap_components":3,
 "sculpted_art_folds_are_physical_geometry":True,
 "face_hair_no_intrusion_claim":"NOT_INDEPENDENTLY_APPROVED",
 "one_shared_glb_file":glb.name,
 "glb_sha256":glbsha,
 "editable_blend":blend.name,
 "actual_reimported_glb_views":photos,
 "actual_face_closeups":headviews,
 "source_2d_art_camera_registration_certified":False,
 "completed_266x30_artist_reacts":0,
 "required_266x30_artist_reacts":7980,
 "user_art_approval":False
}
(OUT/"V153_AUDIT.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False))
print("V153_GLB_REBUILD_FINISHED",json.dumps({
 "glb":glb.name,"deleted_old":len(deleted),
 "pose_errors":pose_error,
 "views":len(photos),"face_views":len(headviews)
 }),flush=True)
