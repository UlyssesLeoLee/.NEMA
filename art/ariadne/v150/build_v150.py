"""V150: V148 face-visibility hard gate on the actual V147 source GLB.
Runs original V147 rebuild, deletes its invalid anterior 'hair growing on face',
builds a posterior scalp shell, temple/ear roots and a posterior long braid.
All edits affect ONE exported GLB. This is a repair candidate, not 266x30 art passes.
"""
import bpy, math, json, hashlib, runpy
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v147/build_v147.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v149"
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene

# Source V147 has exported and reimported real GLB. It is safe to discard the
# invalid artistic HAIR, while retaining physical anatomy/armature and 3D garments.
hair_roots=("V147_Carved_Hair_Scalp_Cap","V147_Head_Rooted_Lock_",
            "V147_Interlaced_Back_Braid_","V147_Crown_Diadem","V147_Crown_Gold_Jewel_")
removed=[]
for o in list(bpy.data.objects):
 if any(o.name.startswith(n) for n in hair_roots):
  removed.append(o.name)
  bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)>24, len(removed)

body=[o for o in bpy.data.objects if o.type=="MESH" and ("Anatomy" in o.name or "Anatomy" in o.data.name)]
assert len(body)==1
body=body[0]
arm=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(arm)==1
world_box=[body.matrix_world@Vector(v) for v in body.bound_box]
cx=(min(p.x for p in world_box)+max(p.x for p in world_box))/2
cy=(min(p.y for p in world_box)+max(p.y for p in world_box))/2
base=min(p.z for p in world_box)
hz=base+1.57

def material(name,rgba,metallic=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 m.diffuse_color=(rgba[0],rgba[1],rgba[2],1)
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=(*rgba,1)
 bs.inputs["Metallic"].default_value=metallic
 bs.inputs["Roughness"].default_value=.58 if metallic==0 else .30
 return m
hair=material("V150_Rooted_Hair_Sculpture",(0.32,.22,.15))
gold=material("V150_Crown_Gold",(.68,.42,.15),.70)
def strand(name,pts,r,ma,cyclic=False):
 cu=bpy.data.curves.new(name+"_geometry","CURVE")
 cu.dimensions="3D";cu.bevel_depth=r
 cu.bevel_resolution=3;cu.resolution_u=14
 spl=cu.splines.new("BEZIER");spl.bezier_points.add(len(pts)-1)
 spl.use_cyclic_u=cyclic
 for be,p in zip(spl.bezier_points,pts):
  be.co=p;be.handle_left_type="AUTO";be.handle_right_type="AUTO"
 ob=bpy.data.objects.new(name,cu)
 bpy.context.collection.objects.link(ob)
 ob.data.materials.append(ma)
 return ob

# V150 physically conforms hair-shell triangles to the ACTUAL evaluated human skull
# instead of introducing the old posterior hemispherical floating bowl.
# Keep a front-facing hairline only at upper skull; avoid eyes/nose/lips entirely.
deps=bpy.context.evaluated_depsgraph_get()
human_eval=body.evaluated_get(deps)
evaluated=human_eval.to_mesh()
try:
 wmat=human_eval.matrix_world
 normalmat=wmat.to_3x3()
 srcverts=[]
 for v in evaluated.vertices:
  pos=wmat@v.co
  norm=(normalmat@v.normal).normalized()
  srcverts.append((pos,norm))
 def scalp_valid(p):
  return (abs(p.x-cx)<.118 and hz-.137<p.z<hz+.130 and
          (p.y<=cy-.009 or (p.z>hz+.067 and p.y<=cy+.085)))
 original_face_polys=[]
 usedids=set()
 for polygon in evaluated.polygons:
  inds=tuple(polygon.vertices)
  if all(scalp_valid(srcverts[i][0]) for i in inds):
   original_face_polys.append(inds)
   usedids.update(inds)
 assert len(original_face_polys)>200, f"not enough actual scalp triangles {len(original_face_polys)}"
 sortedids=sorted(usedids)
 remap={old:i for i,old in enumerate(sortedids)}
 # A sculpted hair layer 3mm above the source skull, not a fake scalp proxy.
 verts=[tuple(srcverts[i][0]+srcverts[i][1]*.0035) for i in sortedids]
 faces=[[remap[x] for x in f] for f in original_face_polys]
 scalpmesh=bpy.data.meshes.new("V150_Exact_Skull_Surface_Hair_Mesh")
 scalpmesh.from_pydata(verts,[],faces)
 scalpmesh.update()
finally:
 human_eval.to_mesh_clear()
scalp=bpy.data.objects.new("V150_True_Anatomy_Conforming_Hair_Cap",scalpmesh)
bpy.context.collection.objects.link(scalp)
scalp.data.materials.append(hair)
for f in scalpmesh.polygons:f.use_smooth=True
th=scalp.modifiers.new("Real_Scalp_Coating_Thickness","SOLIDIFY")
th.thickness=.003
hair_objects=[scalp]
from mathutils.bvhtree import BVHTree
scalp_bvh=BVHTree.FromPolygons([Vector(p) for p in verts],faces,all_triangles=False)
def scalp_point(guess):
 hit=scalp_bvh.find_nearest(Vector(guess),.095)
 if hit is not None and hit[0] is not None and hit[1] is not None:
  location,normal,_,_=hit
  p=location+normal.normalized()*.009
 else:
  # At triangle-border/degenerate BVH spots snap to an ACTUAL scalp vertex;
  # fail if the head topology is missing, never invent a space root.
  assert verts, "Missing actual source-scalp vertices"
  seed=Vector(guess)
  nearest=min((Vector(v) for v in verts),key=lambda v:(v-seed).length_squared)
  norm=nearest-Vector((cx,cy,hz))
  if norm.length<1e-6:norm=Vector((0,0,1))
  p=nearest+norm.normalized()*.008
 # Front facial reserve is stricter than head shell itself.
 if p.z<hz+.065 and p.y>cy-.008:
  p.y=cy-.011
 return p
# Strands follow a real full head surface; posterior roots are in scalp topology.
for i in range(24):
 theta=math.pi+math.pi*(i+.5)/24
 pts=[]
 for j in range(18):
  t=j/17
  phi=.19+1.34*t
  guess=(cx+.093*math.sin(phi)*math.cos(theta),
         cy+.075*math.sin(phi)*math.sin(theta)-.005,
         hz+.110*math.cos(phi))
  pts.append(tuple(scalp_point(guess)))
 hair_objects.append(strand(f"V150_True_Scalp_Rooted_Hair_{i:02d}",pts,.0055,hair))
# Ear-adjacent locks originate on lateral scalp and remain behind facial skin.
for side in (-1,1):
 for k in range(4):
  pts=[]
  for j in range(13):
   t=j/12
   guess=(cx+side*(.082+.012*t),
          cy-.041-.013*k-.010*t,
          hz+.053-.185*t)
   pts.append(tuple(scalp_point(guess)))
  hair_objects.append(strand(f"V150_Postauricular_Rooted_{side}_{k:02d}",pts,.0049,hair))
# Braided side/back mass is anchored to the posterior bound head shape.
for i in range(12):
 pts=[]
 for j in range(38):
  t=j/37
  angle=2*math.pi*(3*t+i/12)
  x=cx+.026*math.sin(angle)+.01*math.sin(math.pi*t)
  y=cy-.087-.023*math.cos(angle)-.018*t
  z=hz-.075-.51*t
  pts.append((x,y,z))
 hair_objects.append(strand(f"V150_Interwoven_Long_Braid_{i:02d}",pts,.0047,hair))
# Fixed per-camera art truth not available; geometry is anatomical scalp-derived.
# Gold crown integrated with hair crest and away from face plane.
for radius,z,depth in [(.110,hz+.088,-.013),(.105,hz+.107,-.020)]:
 points=[]
 for i in range(49):
  t=i/48
  a=math.pi*t
  points.append((cx+radius*math.cos(a),cy+depth-.007*math.sin(a),z+.014*math.sin(a)))
 strand(f"V150_Gold_Crown_Arc_{z:.3f}",points,.0044,gold)
for i in range(11):
 angle=math.pi*(i+.5)/11
 x=cx+.099*math.cos(angle)
 y=cy-.013-.005*math.sin(angle)
 z=hz+.127+.018*math.sin(angle)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.008,location=(x,y,z))
 jewel=bpy.context.object;jewel.name=f"V150_Diadem_Boss_{i:02d}"
 jewel.data.materials.append(gold)

# Diagnostic geometric invariant on newly generated hair geometry.
# The face guard sits in front-center of head; back scalp and ear hair
# should not intersect this conservative forbidden ROI.
# This is NOT independent art mask agreement.
FACE_CENTER_HALF_WIDTH=.075
FACE_FRONT_Y=cy+.002
FACE_Z_MIN=hz-.14
FACE_Z_MAX=hz+.065
violations=[]
samples_checked=0
deps=bpy.context.evaluated_depsgraph_get()
for ob in hair_objects:
 eo=ob.evaluated_get(deps)
 mesh=eo.to_mesh()
 try:
  # Actual triangulated evaluated mesh, not spline control points only.
  for v in mesh.vertices:
   p=eo.matrix_world@v.co
   samples_checked+=1
   if(abs(p.x-cx)<FACE_CENTER_HALF_WIDTH and
      p.y>FACE_FRONT_Y and
      FACE_Z_MIN<p.z<FACE_Z_MAX):
    violations.append((ob.name,tuple(round(float(q),5) for q in p)))
    if len(violations)>12:break
 finally:
  eo.to_mesh_clear()
assert not violations, f"HAIR_INSIDE_FACE_GUARD {violations[:4]}"
assert samples_checked>3000

# New real GLB and Blender source file (editable geometry).
srcblend=OUT/"Ariadne_V150_Face_Hair_Protected.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(srcblend))
glb=OUT/"Ariadne_V150_Corrected_Face_Hair_Engineering_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                           export_cameras=False,export_lights=False)
assert glb.stat().st_size>200000
# GLB exported from real Blender, reimported before all screenshots.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
assert len([o for o in bpy.data.objects if o.type=="ARMATURE"])==1

scene.render.engine="CYCLES";scene.cycles.device="CPU"
scene.cycles.samples=8
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=680;scene.render.resolution_y=850
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=True
look_at=Vector((cx,cy,base+.79))
def area(location,power,size):
 bpy.ops.object.light_add(type="AREA",location=location)
 o=bpy.context.object;o.data.energy=power;o.data.size=size
 o.rotation_euler=(look_at-o.location).to_track_quat("-Z","Y").to_euler()
area((cx+3,cy+2,base+4.5),850,3.5)
area((cx-3,cy-2,base+3.7),700,3)
c=bpy.data.cameras.new("V150_Actual_GLB_Camera")
cam=bpy.data.objects.new("V150_Locked_Camera",c)
scene.collection.objects.link(cam)
scene.camera=cam
c.type="ORTHO";c.ortho_scale=2.54
renders=[]
angles=[(0,0),(15,0),(30,0),(45,0),(90,0),(135,0),
        (180,0),(225,0),(270,0),(315,0),(0,90),(0,-90)]
for az,el in angles:
 azr=math.radians(az);elr=math.radians(el)
 d=Vector((math.sin(azr)*math.cos(elr),math.cos(azr)*math.cos(elr),math.sin(elr)))
 cam.location=look_at+d*4.8
 cam.rotation_euler=(look_at-cam.location).to_track_quat("-Z","Y").to_euler()
 f=OUT/f"V150_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(f)
 bpy.ops.render.render(write_still=True)
 renders.append({"az":az,"el":el,"file":f.name,
                 "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})

# More legible head close-ups across five views.
c.ortho_scale=.61
face_center=Vector((cx,cy,base+1.52))
face=[]
for az in (0,30,60,90,330):
 a=math.radians(az)
 cam.location=face_center+Vector((math.sin(a),math.cos(a),.06))*3
 cam.rotation_euler=(face_center-cam.location).to_track_quat("-Z","Y").to_euler()
 f=OUT/f"V150_FACE_AZ{az:03d}.png"
 scene.render.filepath=str(f)
 bpy.ops.render.render(write_still=True)
 face.append({"az":az,"file":f.name,
              "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
audit={
 "build_state":"V150_REAL_GLB_FACE_GUARD_ENGINEERING_CANDIDATE",
 "upstream_source":"V147 official CC0 rig V146/V148 design-first constraints",
 "old_unapproved_hair_objects_deleted":len(removed),
 "new_articulated_hair_objects":len(hair_objects),
 "tested_evaluated_hair_mesh_vertices":samples_checked,
 "head_face_guards": {"face_guard_width_m":FACE_CENTER_HALF_WIDTH*2,
                      "face_front_blender_y":FACE_FRONT_Y,
                      "face_vertical_bounds": [FACE_Z_MIN,FACE_Z_MAX],
                      "hair_in_front_face_guard_vertices":len(violations)},
 "gltf_glb_file":glb.name,
 "glb_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
 "blend_file":srcblend.name,
 "source_2d_authority":"V147 structural candidate, NOT high-resolution independent approved 266 references",
 "12_reimported_real_glb_views":renders,
 "5_real_glb_face_closeups":face,
 "scalp_bvh_surface_attachment_independently_proven":False,
 "camera_image_art_similarity_95pct":False,
 "anatomical_facial_sculpt_quality_approved":False,
 "finger_ball_actual_support_verified":False,
 "garment_main_folds_art_approved":False,
 "required_true_react_cycles":7980,
 "completed_true_2d_redraw_to_3d_react_cycles":0,
 "formal_art_release":False
}
(OUT/"V150_AUDIT.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
print("V150_FACE_HAIR_GUARD_AND_GLB",json.dumps({
 "mesh_vertex_tests":samples_checked,
 "face_guard_violations":len(violations),
 "new_gltf_file":glb.name,
 "original_wrong_hair_deleted":len(removed)
}),flush=True)
