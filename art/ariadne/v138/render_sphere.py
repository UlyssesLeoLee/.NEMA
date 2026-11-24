import bpy, math, json, hashlib, os, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"artifacts"/"ariadne_v138"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/"website"/"assets"/"ariadne-relief-3d.glb"
assert SOURCE.exists(), f"missing source: {SOURCE}"
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert meshes, "source GLB has no meshes"
corners=[]
for obj in meshes:
 for v in obj.bound_box: corners.append(obj.matrix_world @ Vector(v))
low=Vector([min(v[i] for v in corners) for i in range(3)])
high=Vector([max(v[i] for v in corners) for i in range(3)])
center=(low+high)/2
radius=max((high-low).length*1.35,1)
scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=512;scene.render.resolution_y=512
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=True
scene.world.color=(.14,.14,.14)
def lamp(name,position,power,size):
 bpy.ops.object.light_add(type="AREA",location=position)
 obj=bpy.context.object;obj.name=name;obj.data.energy=power;obj.data.shape="DISK";obj.data.size=size
 direction=center-obj.location;obj.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
lamp("Key",(center.x+radius,center.y-radius,center.z+radius),950,radius)
lamp("Fill",(center.x-radius,center.y-radius/2,center.z+radius/2),650,radius)
cam=bpy.data.cameras.new("V138_Orthographic");camera=bpy.data.objects.new("V138_Camera",cam)
scene.collection.objects.link(camera);scene.camera=camera
cam.type="ORTHO";cam.ortho_scale=max((high-low).length*1.2,.1)
views=[]
for el in range(-75,76,15):
 for az in range(0,360,15):views.append((az,el))
views.extend([(0,90),(0,-90)])
assert len(views)==266
records=[]
for i,(az,el) in enumerate(views):
 a=math.radians(az);e=math.radians(el)
 position=center+Vector((radius*math.sin(a)*math.cos(e),-radius*math.cos(a)*math.cos(e),radius*math.sin(e)))
 camera.location=position
 camera.rotation_euler=(center-position).to_track_quat("-Z","Y").to_euler()
 file=OUT/f"view_{i:03d}_az{az:03d}_el{el:+04d}.png"
 scene.render.filepath=str(file)
 bpy.ops.render.render(write_still=True)
 records.append({"id":i,"azimuth":az,"elevation":el,"image":file.name,"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"matrix_world":[list(row) for row in camera.matrix_world]})
 (OUT/"camera_manifest.json").write_text(json.dumps({"source_sha256":sha,"source_type":"2D_DEPTH_RELIEF_NOT_FULL_SCULPTURE","views":records},indent=2),encoding="utf-8")
report={"source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha,"views_rendered":len(records),"geometry_mesh_objects":len(meshes),"art_similarity_95pct_verified":False,"body_cc0_verified":False,"status":"ENGINEERING_RENDER_ONLY_ART_BLOCKED","reason":"Relief reference is not a full round sculpture; independent 266 approved reference views and CC0 body are missing."}
(OUT/"quality_gate.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report))
