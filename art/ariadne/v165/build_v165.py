"""V165 candidate: modify actual V154 sculpt source, never certify artwork from output."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
src=(ROOT/"art/ariadne/v154/build_v154.py").read_text()
# Capture actual posed bone landmarks before rig destruction.
needle="palm=wp(bs);ball.location=palm+Vector((0,.027,.074))"
assert src.count(needle)==1
src=src.replace(needle, """palm=wp(bs);ball.location=palm+Vector((0,.027,.074))
wrist_bone=rig.pose.bones["wrist."+bs]
wrist_head=rig.matrix_world@wrist_bone.head
wrist_tail=rig.matrix_world@wrist_bone.tail
finger_roots=[rig.matrix_world@b.head for b in rig.pose.bones if b.name.endswith("."+bs) and b.name.split(".")[0] in ("finger2-1","finger3-1","finger4-1","finger5-1")]
print("V165_PALM_LANDMARKS",tuple(wrist_head),tuple(wrist_tail),[tuple(p) for p in finger_roots],flush=True)
""")
marker="# Before export: remove all animation"
assert src.count(marker)==1
# Execute verified base source, stop before its export.
exec(compile(src.split(marker)[0],str(ROOT/"art/ariadne/v154/build_v154.py"),"exec"))
import random, numpy as np
from mathutils.bvhtree import BVHTree
OUT=ROOT/"artifacts/ariadne_v165";OUT.mkdir(parents=True,exist_ok=True)
audit={"source":"V154 builder with actual V153 official CC0 rig",
       "status":"ENGINEERING_CANDIDATE_NOT_ART_APPROVED","completed_art_react_rounds":0}
bpy.context.view_layer.update()
def world_bvh(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    m=ev.to_mesh()
    v=[ev.matrix_world@x.co for x in m.vertices]
    f=[list(p.vertices) for p in m.polygons]
    b=BVHTree.FromPolygons(v,f,all_triangles=False)
    ev.to_mesh_clear()
    return b
bodytree=world_bvh(frozen)
# Palm contact from real surface, in between wrist and non-thumb knuckles.
assert len(finger_roots)>=3,("missing finger bone anchors",len(finger_roots))
knuckles=sum(finger_roots,Vector())/len(finger_roots)
axis=(knuckles-wrist_head); assert axis.length>.025
axis.normalize()
palm_center=wrist_head.lerp(knuckles,.57)
# Search a small palm interior neighborhood for an upward-facing contact.
up=Vector((0,0,1)); lateral=axis.cross(up)
if lateral.length<.1:lateral=Vector((1,0,0))
lateral.normalize()
options=[]
for along in (-.012,-.006,0,.006,.012):
 for across in (-.012,-.006,0,.006,.012):
  p=palm_center+axis*along+lateral*across
  hit,n,_,_=bodytree.ray_cast(p+up*.10,-up,.18)
  if hit is not None and (hit-palm_center).length<.055 and n.dot(up)>.15:
   options.append(((hit-palm_center).length+.012*(1-n.dot(up)),hit,n))
assert options,"no valid upward palm mesh hit; do not substitute wrist proxy"
_,contact,normal=min(options,key=lambda x:x[0])
radius=max(ball.dimensions)*.5
assert .025<radius<.12, radius
center=contact+up*radius
# If central palm is not flat enough, keep physical penetration evidence explicit.
audit["palm"]={"wrist":list(wrist_head),"knuckles":list(knuckles),
 "surface_contact":list(contact),"surface_normal":list(normal),"center":list(center),
 "radius":radius,"palm_proxy":False,"five_finger_support_certified":False}
# Remove old solid sphere and legacy thread.
bpy.data.objects.remove(ball,do_unlink=True)
for ob in list(bpy.data.objects):
 if ob.name.startswith("V154_One_Gold_Thread"):bpy.data.objects.remove(ob,do_unlink=True)
# Actual metallic wound strand; one continuous polyline with fine section.
gold.diffuse_color=(.83,.52,.16,1)
p=gold.node_tree.nodes.get("Principled BSDF")
p.inputs["Base Color"].default_value=(.83,.52,.16,1)
p.inputs["Metallic"].default_value=1
p.inputs["Roughness"].default_value=.29
def tube(name,pts,r,material):
 cu=bpy.data.curves.new(name,"CURVE");cu.dimensions="3D"
 cu.bevel_depth=r;cu.bevel_resolution=2
 s=cu.splines.new("POLY");s.points.add(len(pts)-1)
 for a,v in zip(s.points,pts):a.co=(*v,1)
 ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);cu.materials.append(material)
 return ob
# Deterministic winding in successive rotated planes, continuously joined.
strand_radius=radius*.028
rng=random.Random(165)
wind=[]
for k in range(36):
 a=k*2.399963229728653
 n=Vector((math.cos(a)*.78,math.sin(a)*.78,.62 if k%2 else -.62)).normalized()
 u=n.cross(up).normalized();v=n.cross(u).normalized()
 pts=[]
 for j in range(81):
  t=j/80; phi=2*math.pi*(t+.15*k)
  rr=radius*(.88+.08*k/35)+strand_radius*.45*math.sin(5*phi+k)
  pts.append(center+rr*(u*math.cos(phi)+v*math.sin(phi)))
 if wind:
  # Join on the outer envelope, not through a solid center.
  last=wind[-1]; new=pts[0]
  for j in range(1,12):
   q=(last-center).lerp(new-center,j/12)
   if q.length>1e-6:wind.append(center+q.normalized()*radius*.96)
 wind.extend(pts)
# Actual pedestal attachment via raycast to named mesh, choose visible upper border.
ped=[o for o in scene.objects if o.type=="MESH" and "pedestal" in o.name.lower()]
assert ped,"no pedestal mesh"
hits=[]
for ob in ped:
 b=world_bvh(ob)
 for j in range(48):
  a=j*math.tau/48; p0=Vector((cx+.32*math.cos(a),cy+.32*math.sin(a),base+.2))
  hit,n,_,_=b.ray_cast(p0,-up,.7)
  if hit is not None and n.dot(up)>.5:hits.append((ob,hit))
assert hits,"no pedestal top attachment"
ped_ob,end=min(hits,key=lambda x:(x[1]-center).length)
# Reuse smooth external route, now surface-anchored at both ends.
# start at actual last wound strand and finish at actual pedestal top.
exit_pt=wind[-1]; free=[]
for i in range(201):
 t=i/200
 ang=math.atan2(exit_pt.y-cy,exit_pt.x-cx)+math.tau*1.15*t
 r=.37+.025*math.sin(math.pi*t)
 q=Vector((cx+r*math.cos(ang),cy+r*math.sin(ang),exit_pt.z*(1-t)+end.z*t))
 if t<.16:
  s=t/.16;s=s*s*(3-2*s);q=exit_pt.lerp(q,s)
 if t>.82:
  s=(t-.82)/.18;s=s*s*(3-2*s);q=q.lerp(end,s)
 free.append(q)
free[0]=exit_pt;free[-1]=end
tube("V165_One_Continuous_Wound_Gold_Thread_To_Pedestal",wind+free[1:],strand_radius,gold)
audit["gold"]={"winding_points":len(wind),"continuous_curve":True,
 "strand_radius":strand_radius,"pedestal":ped_ob.name,"endpoint":list(end),
 "endpoint_surface_verified":True,"collision_and_art_path_certified":False}
# Add finer surface-following strand relief to existing hair locks,
# using each actual centerline plus local tangent and multiple micro strands.
hair_curves=[o for o in scene.objects if o.type=="CURVE" and
             o.name.startswith(("V154_EarRear_Braided_Lock_","V154_Greek_Princess_Back_Braid_"))]
assert hair_curves,"missing actual hair locks"
hair_count=0
for ob in hair_curves:
 for sp in ob.data.splines:
  if sp.type!="BEZIER":continue
  pts=[ob.matrix_world@p.co for p in sp.bezier_points]
  if len(pts)<3:continue
  r=ob.data.bevel_depth
  for k in range(7):
   fine=[]
   for j,p0 in enumerate(pts):
    tang=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
    ref=Vector((0,1,0)) if abs(tang.y)<.9 else Vector((1,0,0))
    u=tang.cross(ref).normalized();v=tang.cross(u).normalized()
    a=math.tau*k/7+.45*j/(len(pts)-1)
    fine.append(p0+(u*math.cos(a)+v*math.sin(a))*r*.91)
   tube("V165_Fine_Sculpted_Hair_%04d"%hair_count,fine,r*.12,hairmat)
   hair_count+=1
audit["hair"]={"micro_strand_mesh_curves":hair_count,"reference_likeness_certified":False}
# Eyes: preserve existing anatomy. Only add iris/pupil if actual mesh object
# names and surfaces support eye positioning; never guess eye centers from head bbox.
eye_objects=[o for o in scene.objects if o.type=="MESH" and
             any(x in o.name.lower() for x in ("eyeball","eye_ball","eye.l","eye.r","eye_left","eye_right"))]
eye_result=[]
for ob in eye_objects:
 b=world_bvh(ob);bb=[ob.matrix_world@Vector(p) for p in ob.bound_box]
 c=sum(bb,Vector())/8;rr=max(ob.dimensions)*.5
 if not .005<rr<.04:continue
 # V154 convention +Y front. Check actual surface hit.
 front=Vector((0,1,0));hit,n,_,_=b.ray_cast(c+front*.08,-front,.15)
 if hit is None:continue
 u=Vector((1,0,0));v=Vector((0,0,1))
 for ring,frac in (("Iris",.43),("Pupil",.18)):
  rp=rr*frac; pts=[]
  for j in range(65):
   a=math.tau*j/64;pos=hit+rp*(u*math.cos(a)+v*math.sin(a))
   h,_,_,_=b.ray_cast(pos+front*.025,-front,.05)
   if h is not None:pts.append(h+front*.00015)
  if len(pts)==65:tube("V165_"+ring+"_"+ob.name,pts,.00025,white)
 eye_result.append(ob.name)
audit["eyes"]={"actual_eye_meshes":eye_result,"status":"RELIEF_RINGS_CANDIDATE" if len(eye_result)==2 else "BLOCKED_NO_VERIFIED_SEPARATE_EYE_MESH",
 "recessed_pupil_certified":False}
# Export actual static candidate and render all 266 calibrated directions.
bpy.context.view_layer.update()
blend=OUT/"Ariadne_V165_EDITABLE.blend";bpy.ops.wm.save_as_mainfile(filepath=str(blend))
glb=OUT/"Ariadne_V165_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_animations=False,export_cameras=False,export_lights=False)
assert glb.stat().st_size>1000000
audit["glb_sha256"]=hashlib.sha256(glb.read_bytes()).hexdigest()
audit["input_art"]={"GIF":"REQUIRED_INDEPENDENT_INPUT","SVG":"REQUIRED_INDEPENDENT_INPUT","ARGB":"REQUIRED_INDEPENDENT_INPUT","availability":"NOT_VERIFIED","no_self_validation":True}
(OUT/"audit.json").write_text(json.dumps(audit,indent=2))
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=384;scene.render.resolution_y=512
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
target=Vector((cx,cy,base+.83))
cam=bpy.data.objects.new("V165_Camera",bpy.data.cameras.new("V165_Camera"))
scene.collection.objects.link(cam);scene.camera=cam
cam.data.type="ORTHO";cam.data.ortho_scale=2.5
views=[(a,e) for e in range(-75,76,15) for a in range(0,360,15)]+[(0,-90),(0,90)]
assert len(views)==266 and len(set(views))==266
records=[]
for a,e in views:
 az,el=map(math.radians,(a,e))
 d=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
 cam.location=target+d*4.7;cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 f=OUT/("AZ%03d_EL%+03d.png"%(a,e));scene.render.filepath=str(f)
 bpy.ops.render.render(write_still=True)
 records.append({"azimuth":a,"elevation":e,"file":f.name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
 (OUT/"camera_records.json").write_text(json.dumps(records))
audit["actual_spherical_views"]=len(records)
(OUT/"audit.json").write_text(json.dumps(audit,indent=2))
