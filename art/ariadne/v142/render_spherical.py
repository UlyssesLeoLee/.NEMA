"""Render the *reimported* V141 GLB from all 266 fixed spherical cameras.
These are real geometry diagnostics. NO ART ReAct iterations are claimed without approved targets.
"""
import bpy, math, hashlib, json, runpy, shutil
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v141/build_v141.py"),run_name="__main__")
PREVIOUS=ROOT/"artifacts"/"ariadne_v141"
OUT=ROOT/"artifacts"/"ariadne_v142"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=PREVIOUS/"Ariadne_V141_Geometry_Rebuild_NOT_ART_APPROVED.glb"
assert SOURCE.is_file() and SOURCE.stat().st_size>100000, "V141 real GLB missing"
model_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
DEST=OUT/"Ariadne_V142_Spherical_Diagnostic_NOT_ART_APPROVED.glb"
shutil.copyfile(SOURCE,DEST)

# Completely remove the source sculptural scene; recreate scene FROM EXPORTED GLB.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(DEST))
objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert len(objs)>10, "GLB reimport did not recover actual meshes"
verts=[]
for o in objs:
 for corner in o.bound_box:
  verts.append(o.matrix_world@Vector(corner))
lo=Vector((min(p.x for p in verts),min(p.y for p in verts),min(p.z for p in verts)))
hi=Vector((max(p.x for p in verts),max(p.y for p in verts),max(p.z for p in verts)))
center=(lo+hi)/2
span=hi-lo
assert span.z>1.5 and span.z<3.0 and span.x>.2, "Non-physical bounding box"
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=2
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=192
scene.render.resolution_y=192
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=True
if scene.world is None:scene.world=bpy.data.worlds.new("V142_Studio")
scene.world.color=(.4,.4,.4)
def add_light(loc,power):
 bpy.ops.object.light_add(type="AREA",location=loc)
 o=bpy.context.object;o.data.energy=power;o.data.size=3.5
 o.rotation_euler=(center-o.location).to_track_quat("-Z","Y").to_euler()
add_light((center.x+3,center.y+3,center.z+3),600)
add_light((center.x-3,center.y-1,center.z+2),400)
camdat=bpy.data.cameras.new("SPHERE_LOCKED_ORTHO")
cam=bpy.data.objects.new("SPHERE_CAMERA",camdat)
scene.collection.objects.link(cam);scene.camera=cam
camdat.type="ORTHO";camdat.ortho_scale=span.length*1.17
views=[(az,el) for el in range(-75,76,15) for az in range(0,360,15)]
views.extend([(0,90),(0,-90)])
assert len(views)==266 and len(set(views))==266
records=[]
for i,(az,el) in enumerate(views):
 a=math.radians(az);e=math.radians(el)
 d=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 cam.location=center+d*5
 cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
 outfile=OUT/f"AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(outfile)
 bpy.ops.render.render(write_still=True)
 sha=hashlib.sha256(outfile.read_bytes()).hexdigest()
 records.append({
  "index":i,"azimuth_deg":az,"elevation_deg":el,
  "png":outfile.name,"png_sha256":sha,
  "camera_matrix_world":[[round(x,7) for x in row] for row in cam.matrix_world],
  "model_sha256":model_sha,
  "reference_status":"NOT_REGISTERED_APPROVED",
  "reprojection_similarity":None,"art_threshold_pass":False,
  "react_cycles_executed":0,
  "reason":"Only model re-projection. No independent approved same-camera 2D artwork."
 })
 if i%24==0:print("V142_PROJECTION",i+1,"of",len(views),flush=True)
assert len({r["png_sha256"] for r in records})>5, "Too many identical viewpoints"
manifest={
 "model":"Ariadne_V142_Spherical_Diagnostic_NOT_ART_APPROVED.glb",
 "model_sha256":model_sha,
 "source":"V141 genuine MakeHuman CC0 plus procedural 3D engineering edits",
 "views":records,
 "unique_views":len(records),
 "independent_approved_references":0,
 "actual_react_cycles_executed":0,
 "minimum_react_cycles_needed_when_references_available":266*3,
 "art_target_passed_views":0,
 "geometry_reprojection_evidence":True,
 "full_art_completion":False,
 "status":"SPHERICAL_GEOMETRY_EVIDENCE_ONLY_ART_BLOCKED"
}
(OUT/"V142_CAMERA_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
(OUT/"V142_ART_GATE.json").write_text(json.dumps({
 "status":"ART_BLOCKED_REFERENCE_MISSING_AND_GEOMETRY_INCOMPLETE",
 "checked_266_fixed_cameras":True,
 "reference_registered_and_approved":False,
 "per_angle_95_percent_measured":False,
 "three_actual_react_cycles_per_angle":False,
 "pose_rig_joint_validated":False,
 "palm_orb_contact_validated":False,
 "garment_pattern_collision_validated":False,
 "face_and_hair_authority_validated":False,
 "formal_glb_release":False,
 "warning":"2D reprojection != independent 2D reference ReAct. Not a complete sculpture."
},indent=2),encoding="utf-8")
print("V142_SPHERE_RENDERED",len(records),"UNIQUE_IMAGES",len({r["png_sha256"] for r in records}),flush=True)
