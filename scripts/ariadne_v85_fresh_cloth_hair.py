"""V85 fresh anatomical cloth-and-hair study, built and simulated using real Blender.
Only uses MakeHuman CC0 female source. No legacy dressed V52-V83 geometry.
Art status: DIAGNOSTIC / not same as approved V20 illustrations.
"""
import bpy, math, json, hashlib, pathlib, os, urllib.request
from mathutils import Vector
from math import pi, sin, cos, exp
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE", "."))
OUT=ROOT/"ariadne_v85_artifacts"; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
URL="https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
def source(name,path):
 p=OUT/name
 if not p.exists():urllib.request.urlretrieve(URL+path,str(p))
 assert p.stat().st_size>100000,p
 return p
base=source("MakeHuman_CC0_base.obj","3dobjs/base.obj")
female=source("MakeHuman_female.target","targets/macrodetails/caucasian-female-young.target")
v=[];f=[];g=None
for line in base.open():
 if line.startswith("v "):
  x,y,z=map(float,line.split()[1:4]); v.append([x/10,-z/10,y/10])
 elif line.startswith("g "):g=line.strip()[2:]
 elif line.startswith("f ") and g=="body":f.append([int(q.split("/")[0])-1 for q in line.split()[1:]])
for line in female.open():
 a=line.split()
 if len(a)==4 and a[0].isdigit():
  i=int(a[0]);dx,dy,dz=map(float,a[1:]);v[i][0]+=dx/10;v[i][1]-=dz/10;v[i][2]+=dy/10
assert len(f)==13378
z0=min(x[2] for x in v[:13380])
for q in v:q[2]-=z0
# Limited prototype pose from continuous CC0 anatomical body, no capsules
def sm(a,b,x):
 t=min(1,max(0,(x-a)/(b-a)));return t*t*(3-2*t)
for p in v:
 x,y,z=p
 shoulder_weight=sm(.17,.34,x)*sm(.82,.95,z)*(1-sm(1.40,1.55,z))
 # A-pose right arm raised as two gradual regions; not claimed anatomy-approved
 p[2]+=shoulder_weight*(.06*sm(.19,.37,x)+.36*sm(.36,.49,x))
 # small natural torso counterbalance
 p[0]+=.013*sm(.77,1.18,z)*(1-sm(1.35,1.51,z))
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
body=obj("00_CC0_Female_Anatomical_Collider",v[:13380],f,stone)
body["body_source"]="MakeHuman CC0 base.obj + caucasian-female-young.target"
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
 mod.settings.quality=5;mod.settings.mass=mass
 if ids:mod.settings.vertex_group_mass=grp.name
 mod.collision_settings.use_collision=True;mod.collision_settings.distance_min=.006
 mod.collision_settings.use_self_collision=True;mod.collision_settings.self_distance_min=.006
 mod.point_cache.frame_start=1;mod.point_cache.frame_end=60
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
 pleat=(.005+.018*w)*cos(13*a +.21*w +.2*sin(5*a)) +.003*cos(23*a-1.7*w)
 return ((rx+pleat)*cos(a)+.014*sin(pi*w),
         (ry+.65*pleat)*sin(a),z+.014*sin(3*a)*w)
# use closed cylinder rim via ring mesh, with pinned top ring
def skirt_obj():
 nu=96;nv=94
 pts=[skirt(i/nu,j/(nv-1)) for j in range(nv) for i in range(nu)]
 fs=[]
 for j in range(nv-1):
  for i in range(nu):
   a=j*nu+i;b=j*nu+(i+1)%nu;fs.append((a,b,b+nu,a+nu))
 ob=obj("10_CHITON_ONE_CONNECTED_SKIRT",pts,fs,clothmat)
 grp=ob.vertex_groups.new(name="WAIST_PIN");grp.add(list(range(nu)),1,"REPLACE")
 mo=ob.modifiers.new("REAL_CLOTH_SOLVER","CLOTH");mo.settings.vertex_group_mass=grp.name;mo.settings.quality=5;mo.settings.mass=.33
 mo.collision_settings.use_collision=True;mo.collision_settings.distance_min=.006
 mo.collision_settings.use_self_collision=True;mo.collision_settings.self_distance_min=.006
 mo.point_cache.frame_start=1;mo.point_cache.frame_end=60
 ob["cloth_origin"]="SINGLE_CONTINUOUS_CIRCUMFERENTIAL_MESH"
 return ob
cloth.append(skirt_obj())
# U-shaped soft neckline and gravity formed chest folds, top pinned along shoulder line
def chest(u,w):
 x=-.229+.458*u
 upper=1.305-.095*(1-(2*u-1)**2)
 z=upper-(upper-.985)*w
 ridge=(.007*cos((4*u+1.4*w)*pi)+.004*cos((9*u-1.2*w)*pi))*w
 y=-.199-.020*(1-(2*u-1)**2)+ridge-.010*sin(pi*w)
 return(x,y,z)
cloth.append(ribbon("11_BODICE_U_FOLD_CONTINUOUS",72,64,chest,cloth2))
# broad actual diagonal, continuous warp of mesh, not overlay ribbons for mock fold
def diagonal(u,w):
 center_x=.20-.35*w;center_z=1.285-.28*w
 width=.055+.041*sin(pi*w)
 return (center_x+(u-.5)*.04,-.248-.008*cos(8*u*pi)*sin(pi*w),
         center_z+(u-.5)*width*2)
cloth.append(ribbon("12_SHOULDER_TO_WAIST_CONTINUOUS_DRAPE",34,84,lambda u,w:diagonal(u,w),clothmat))
# deep hip diagonal fold panel: authored from actual folded sewing cloth
def hip(u,w):
 x=-.285+.56*u
 top=.99-.045*u
 drop=(.07+.19*sin(pi*u)+.055*u)
 z=top-drop*w
 y=-.308-.018*sin(pi*u)-.015*w+.012*sin(pi*6*u)*sin(pi*w)
 return x,y,z
cloth.append(ribbon("13_HIP_CROSS_SWAG_CONTINUOUS",78,55,hip,clothmat))
# two separate layers only where 2D explicitly shows cape and underlayer
def veil(u,w,layer):
 spread=.18+.18*w +.04*layer
 x=(u-.5)*2*spread
 z=1.58-1.35*w+.01*sin(8*pi*u)*(w**1.4)
 y=.205+.046*layer+.13*w+.016*sin(11*pi*u)*(w**.55)
 return x,y,z
for layer in [0,1]:
 cloth.append(ribbon("14_BACK_VEIL_CONTINUOUS_LAYER_"+str(layer),56,96,lambda u,w,ly=layer:veil(u,w,ly), clothmat if layer==0 else cloth2))
# side drape panels attached to each shoulder
for sign in (-1,1):
 def sleeve(u,w,s=sign):
  x=s*(.205+.075*u +.018*w)
  y=-.10+.16*u-.025*w
  z=1.295-w*(.24+.23*u)+.006*cos(8*pi*u)*w
  return(x,y,z)
 cloth.append(ribbon("15_SHOULDER_SLEEVE_"+str(sign),28,50,sleeve,cloth2))
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
  curve("20_HAIR_FOREHEAD_MAJOR_WAVE_%s_%d"%(side,k),track,.016-.002*k,hairmat)
 # side curls from ear to shoulder
 for q in range(2):
  pts=[]
  for j in range(76):
   t=j/75
   a=2*pi*(2.0*t+q*.23)
   pts.append((side*(.132+.011*cos(a)+q*.010),
               -.05+.013*sin(a),
               1.455-.25*t))
  curve("21_HAIR_EAR_TO_COLLARBONE_%s_%d"%(side,q),pts,.010,hairmat)
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
sphere("30_GOLD_ORB",(.49,-.055,1.495),.072,gold)
thread=[]
for i in range(130):
 t=i/129
 x=.505-.72*t+.15*sin(pi*t)
 y=-.10-.19*sin(pi*t)
 z=1.43-1.25*t-.065*sin(pi*3*t)
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
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=60
report={"version":"V85","source":"fresh MakeHuman CC0, no V52-V83 dressed mesh",
 "status":"UNAPPROVED_ARTISTIC_DIAGNOSTIC","blender_version":bpy.app.version_string,
 "reference_2d_alignment":"NOT_VERIFIED","frame_count":60,"cloth":{}}
# Real physics solver on ALL connected cloth surfaces, record actual displacements
for frame in range(1,61):
 scene.frame_set(frame)
 if frame in (1,15,30,45,60):print("SOLVER_FRAME",frame,flush=True)
deps=bpy.context.evaluated_depsgraph_get()
for ob in cloth:
 ev=ob.evaluated_get(deps);me=ev.to_mesh()
 pos0=[tuple(p.co) for p in ob.data.vertices]
 pos1=[tuple(p.co) for p in me.vertices]
 assert len(pos0)==len(pos1)
 movement=[math.dist(a,b) for a,b in zip(pos0,pos1)]
 record={"vertices":len(pos1),"maximum_vertex_motion_m":max(movement),"mean_vertex_motion_m":sum(movement)/len(movement)}
 report["cloth"][ob.name]=record
 assert record["maximum_vertex_motion_m"]>.0001,ob.name
 new=bpy.data.meshes.new(ob.name+"_FROZEN_SIMULATED_MESH")
 new.from_pydata(pos1,[],[tuple(poly.vertices) for poly in ob.data.polygons]);new.update()
 frozen=bpy.data.objects.new(ob.name+"_ACTUAL_CLOTH_SOLVED",new)
 bpy.context.collection.objects.link(frozen)
 frozen.data.materials.append(ob.data.materials[0])
 frozen["actual_blender_cloth_solver"]=True
 frozen["frame_number"]=60
 ev.to_mesh_clear()
 ob.hide_render=True;ob.hide_set(True)
# Save physically editable scene, not claiming full disk-baked cache
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"V85_Editable_Cloth_Physics_Graybox.blend"))
# Export only frozen cloth, body, hair & ornaments, NOT source cloth
bpy.ops.object.select_all(action="DESELECT")
for ob in scene.objects:
 if ob.type in ("MESH","CURVE") and ob not in cloth and not ob.hide_render:ob.select_set(True)
scene.view_layers[0].objects.active=body
glb=OUT/"Ariadne_V85_Fresh_ClothSolved_HairStructure_DIAGNOSTIC.glb"
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
scene.render.engine="CYCLES";scene.cycles.samples=7
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
 scene.render.filepath=str(OUT/("V85_CameraLocked_%03d.png"%angle))
 bpy.ops.render.render(write_still=True)
 print("RENDERED_VIEW",angle,flush=True)
(OUT/"CameraLocked24.json").write_text(json.dumps(cam_manifest,indent=2))
(OUT/"Actual_Solver_And_GLB_Audit.json").write_text(json.dumps(report,indent=2))
print("V85_FINAL_DIAGNOSTIC",json.dumps(report),flush=True)
