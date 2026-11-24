"""V145 tangible anatomy-contact and garment-depth correction on V144 official CC0-rigged GLB.
This is NOT a 30-cycle art ReAct completion. Fail-closed art authority is elsewhere.
"""
import bpy,runpy,math,hashlib,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v144/build_ik.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v145"
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
# V144 build script ends with reimported GLB. Find that actual Blender geometry.
bodys=[o for o in bpy.data.objects if o.type=="MESH" and ("Anatomy" in o.name or "Anatomy" in o.data.name)]
if not bodys:
 bodys=sorted([o for o in bpy.data.objects if o.type=="MESH"],key=lambda x:len(x.data.vertices),reverse=True)[:1]
body=bodys[0]
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(rigs)==1
rig=rigs[0]
bpy.context.view_layer.update()
# Material for actual added geometry, not a projected illustration.
def mat(name,rgba,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.diffuse_color=(*rgba[:3],1);m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(*rgba[:3],1)
 p.inputs["Metallic"].default_value=metal
 return m
purple=mat("V145_Royal_Purple_Sculpture",(.21,.07,.30))
gold=mat("V145_Thread_Gold",(.75,.47,.16),.75)
# Read exact evaluated body surface from real skinned mesh to constrain the orb.
deps=bpy.context.evaluated_depsgraph_get()
body_eval=body.evaluated_get(deps)
emesh=body_eval.to_mesh()
try:
 worldcoords=[body_eval.matrix_world @v.co for v in emesh.vertices]
 polygons=[tuple(p.vertices) for p in emesh.polygons]
 bvh=BVHTree.FromPolygons(worldcoords,polygons,all_triangles=False)
 arms=[o for o in rigs[0].pose.bones if o.name.startswith("wrist.")]
 orbs=[o for o in bpy.data.objects if o.type=="MESH" and "Golden_Orb" in o.name]
 assert arms and orbs
 orb=orbs[-1]
 wrist=min(arms,key=lambda a:((rig.matrix_world@a.tail)-orb.location).length)
 wrist_world=rig.matrix_world@wrist.tail
 # Reconstruct radius in world space from its actual bounding vertices.
 orb_v=[orb.matrix_world@Vector(c) for c in orb.bound_box]
 r=max((p-orb.location).length for p in orb_v)/math.sqrt(3)
 assert .03<r<.12, "gold orb radius implausible"
 # Measure surface in neighbourhood of true wrist before moving orb.
 # use an upward and forward offset from wrist and nearest point normal,
 # so orb is tangent to real skinned anatomy, rather than floating freely.
 guess=wrist_world+Vector((0,.055,.08))
 hit=bvh.find_nearest(guess,0.26)
 assert hit and hit[0] is not None, "no anatomy surface near wrist"
 contact,normal,_,dist=hit
 assert (contact-wrist_world).length<.23, "contact is too far from wrist"
 normal.normalize()
 proposed=contact+normal*r
 orb.location=proposed
 bpy.context.view_layer.update()
 observed=bvh.find_nearest(proposed,0.23)
 assert observed
 surface_gap=abs((proposed-observed[0]).length-r)
 assert surface_gap<.016,"orb does not touch anatomical surface"
 wrist_gap=(proposed-wrist_world).length
 # Thread follows the actual orb. Update endpoint through source world space.
 curves=[o for o in bpy.data.objects if o.type=="CURVE" and "Gold_Thread" in o.name]
 updated=0
 for c in curves:
  for spl in c.data.splines:
   if spl.type=="BEZIER" and len(spl.bezier_points)>=2:
    inv=c.matrix_world.inverted()
    spl.bezier_points[-1].co=inv@proposed
    spl.bezier_points[-2].co=inv@(proposed+Vector((0,0,-.055)))
    updated+=1
 assert updated>0,"gold thread failed to follow physical orb"
finally:
 body_eval.to_mesh_clear()
# Remove visibly unsupported ribbon construction; replace with shoulder/
# waist oriented actual sculptural 3D surfaces, not flat paper card.
removed=[]
for obj in list(bpy.data.objects):
 if obj.type=="MESH" and obj!=body and (obj.name.startswith(("Himation_Front_Patterned","Himation_Back_Patterned","Purple_Himation_Sculpted","Himation_Back_Fold"))):
  removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
# Geometric sculptural panel: 18x20 grid, longitudinal folds, shoulder-to-waist
# and back-wrap volume. Fitted as stitched, thickened 3D surface.
def mantle(name,rows,side_scale):
 V=[];F=[];U=19
 for i,(x,y,z,width) in enumerate(rows):
  t=i/(len(rows)-1)
  for k in range(U):
   u=(k/(U-1)-.5)*2
   # Primary longitudinal fold hierarchy (3 broad + 7 secondary folds)
   fold=.027*math.sin((u+.25)*math.pi*3+.4*t)+.007*math.sin(u*math.pi*7+2*t)
   px=x+u*width*.5
   py=y+fold+side_scale*.015*math.sin(t*math.pi)
   pz=z+.010*math.sin(2*math.pi*u+i*.27)
   V.append((px,py,pz))
 for i in range(len(rows)-1):
  for k in range(U-1):
   a=i*U+k;F.append((a,a+1,a+U+1,a+U))
 mesh=bpy.data.meshes.new(name+"_sculpted_mesh")
 mesh.from_pydata(V,[],F);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 o.data.materials.append(purple)
 for f in mesh.polygons:f.use_smooth=True
 so=o.modifiers.new("Real_Textile_Thickness","SOLIDIFY");so.thickness=.011
 su=o.modifiers.new("Art_Drape_Curvature","SUBSURF");su.levels=2
 return o
# Figure center from actual skinned body vertices, never chosen per camera.
bpy.context.view_layer.update()
coords=[body.matrix_world@Vector(c) for c in body.bound_box]
cx=(min(p.x for p in coords)+max(p.x for p in coords))*.5
cy=(min(p.y for p in coords)+max(p.y for p in coords))*.5
zz=min(p.z for p in coords)
front=[];back=[]
for j in range(23):
 t=j/22
 z=zz+1.43-t*1.34
 width=.15+.25*math.sin(math.pi*(t*.86+.065))**.8
 x=cx-.15+.20*math.sin(math.pi*t*.76)
 front.append((x,cy+.105+.037*math.sin(math.pi*t),z,width))
 back.append((cx-.17+.22*t,cy-.145-.05*math.sin(math.pi*t),z,width*.82))
mantle("V145_Himation_Front_True_3D_Primary_Folds",front,+1)
mantle("V145_Himation_Back_True_3D_Primary_Folds",back,-1)
# Export and reimport for faithful rasterization and verifiable GLB.
glb=OUT/"Ariadne_V145_Contact_Fold_Adjustment_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
assert glb.stat().st_size>200000
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
assert len([o for o in bpy.data.objects if o.type=="ARMATURE"])==1
# Render actual revised GLB in ten critical directions.
scene.render.engine="CYCLES"
scene.cycles.device="CPU";scene.cycles.samples=4
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=512;scene.render.resolution_y=720
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=True
center=Vector((cx,cy,zz+.83))
def area(pos,energy):
 bpy.ops.object.light_add(type="AREA",location=pos)
 obj=bpy.context.object;obj.data.energy=energy;obj.data.size=3
 obj.rotation_euler=(center-obj.location).to_track_quat("-Z","Y").to_euler()
area((3,-3,4),750);area((-3,2,3),550)
camera=bpy.data.objects.new("V145_Ortho",bpy.data.cameras.new("Camera"))
scene.collection.objects.link(camera);scene.camera=camera
camera.data.type="ORTHO";camera.data.ortho_scale=2.75
views=[(a,0) for a in (0,45,90,135,180,225,270,315)]+[(0,90),(0,-90)]
renders=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 direction=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
 camera.location=center+direction*4.3
 camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V145_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 renders.append({"az":az,"el":el,"image":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
# Honest accounting: 10 diagnostics but ZERO true external 2D re-draw ReAct cycles.
audit={
 "stage":"REAL_GL_B_GEOMETRY_CORRECTION_AND_10_ACTUAL_VIEWS",
 "status":"ART_BLOCKED_MISSING_266_APPROVED_2D_REFERENCES_AND_7980_REACT",
 "source":"V144 real official CC0 weighted IK model",
 "glb":glb.name,"glb_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
 "actual_mesh_corrections":{"orb_to_skinned_anatomy_tangency_gap_m":surface_gap,
 "orb_to_wrist_m":wrist_gap,"gold_thread_endpoint_updates":updated,
 "unsupported_mantle_objects_removed":removed,
 "new_3d_mantle_panels":2},
 "actual_renders":renders,
 "required_views":266,"required_cycles_per_view":30,
 "required_individual_cycles":7980,"actually_completed_true_art_react_cycles":0,
 "camera_registered_art_refs":0,
 "palmar_finger_support_verified":False,
 "sewn_garment_art_accuracy_verified":False,
 "art_95_percent_verified":False
}
(OUT/"V145_AUDIT.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print("V145_GEOMETRY_COMMIT",json.dumps(audit["actual_mesh_corrections"]),flush=True)
