"""V139 genuine full-round anatomical base. Not a finished Ariadne likeness."""
import bpy, math, json, hashlib, urllib.request, os
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"artifacts"/"ariadne_v139"
OUT.mkdir(parents=True,exist_ok=True)
REV="a8bc2d54ff0ac92e78ff71431b1023eda42bf482"
BASE="https://raw.githubusercontent.com/makehumancommunity/makehuman/"+REV+"/makehuman/data/"
SOURCES={
 "base.obj": BASE+"3dobjs/base.obj",
 "female.target": BASE+"targets/macrodetails/caucasian-female-young.target",
}
source_hashes={}
for name,url in SOURCES.items():
 dst=OUT/name
 urllib.request.urlretrieve(url,str(dst))
 if dst.stat().st_size<10000: raise RuntimeError("unexpectedly small official asset "+name)
 source_hashes[name]=hashlib.sha256(dst.read_bytes()).hexdigest()
 print("OFFICIAL_CC0_ASSET",name,dst.stat().st_size,source_hashes[name],flush=True)

# Build Blender mesh directly from original vertex indexing so that official
# MakeHuman morph deltas cannot accidentally be applied to reordered vertices.
verts=[]; faces=[]; current_group=None; skipped_helper_faces=0
for ln in (OUT/"base.obj").open(errors="replace"):
 if ln.startswith("v "):
  t=ln.split();verts.append(tuple(map(float,t[1:4])))
 elif ln.startswith("g "):
  current_group=ln.strip().split(maxsplit=1)[1]
 elif ln.startswith("f "):
  if current_group!="body":
   skipped_helper_faces+=1
   continue
  fs=[]
  for tok in ln.split()[1:]:
   val=int(tok.split("/")[0]);fs.append(val-1 if val>0 else len(verts)+val)
  faces.append(fs)
if len(verts)<10000 or len(faces)<10000:
 raise RuntimeError("Incomplete official MakeHuman mesh")
shifted=0
for ln in (OUT/"female.target").open(errors="replace"):
 tokens=ln.split()
 if len(tokens)!=4 or tokens[0].startswith("#"):continue
 try:
  i=int(tokens[0]);dx,dy,dz=map(float,tokens[1:])
 except ValueError:continue
 if i<0 or i>=len(verts):raise RuntimeError("target index out of range")
 x,y,z=verts[i]
 verts[i]=(x+dx,y+dy,z+dz)
 shifted+=1
if shifted<1000:raise RuntimeError("female morphology did not apply")
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
used_indices=sorted({i for face in faces for i in face})
remap={old:new for new,old in enumerate(used_indices)}
body_verts=[verts[i] for i in used_indices]
body_faces=[[remap[i] for i in face] for face in faces]
mesh=bpy.data.meshes.new("MakeHuman_Official_CC0_MorphFemale_BodyOnly")
mesh.from_pydata(body_verts,[],body_faces);mesh.update()
print("Body faces",len(body_faces),"removed helper faces",skipped_helper_faces,flush=True)
body=bpy.data.objects.new("Ariadne_CC0_Female_Anatomy_MASTER",mesh)
bpy.context.collection.objects.link(body)
# Normalize to height 1.70m and orient longest dimension vertically.
ranges=[max(v[i] for v in verts)-min(v[i] for v in verts) for i in range(3)]
axis=max(range(3),key=lambda i:ranges[i])
if axis==1:
 body.rotation_euler[0]=math.pi/2
 body.rotation_euler[2]=math.pi
elif axis==0:body.rotation_euler[1]=-math.pi/2
bpy.context.view_layer.update()
bnd=[body.matrix_world @ Vector(p) for p in body.bound_box]
bottom=min(v.z for v in bnd);top=max(v.z for v in bnd)
height=top-bottom
if height<=0:raise RuntimeError("degenerate human mesh")
body.scale=(1.7/height,)*3
bpy.context.view_layer.update()
bnd=[body.matrix_world @ Vector(p) for p in body.bound_box]
bottom=min(v.z for v in bnd)
body.location.z-=bottom
body["source"]="official_makehuman_CC0_base"
body["morph"]="caucasian-female-young.target"
body["quality"]="ANATOMICAL_BASE_ONLY_NOT_TARGET_POSE"
mat=bpy.data.materials.new("Diagnostic_Plain_Clay")
mat.diffuse_color=(.74,.68,.62,1);body.data.materials.append(mat)
for p in mesh.polygons:p.use_smooth=True
# No fake procedural body, garment, hair, or image-mapped relief is added.
bpy.context.view_layer.objects.active=body;body.select_set(True)
model=OUT/"Ariadne_V139_CC0_Anatomical_Foundation_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(model),export_format="GLB",use_selection=True)
body.select_set(False)
if not model.exists() or model.stat().st_size<100000:
 raise RuntimeError("Failed to export GLB anatomical mesh")
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.device="CPU"
scene.cycles.samples=8;scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=560;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.film_transparent=True
if not scene.world:scene.world=bpy.data.worlds.new("Studio")
scene.world.color=(.25,.25,.25)
def lamp(location,energy,size):
 bpy.ops.object.light_add(type="AREA",location=location)
 l=bpy.context.object;l.data.energy=energy;l.data.size=size
 l.rotation_euler=(Vector((0,0,.85))-l.location).to_track_quat("-Z","Y").to_euler()
lamp((3,-4,5),650,4);lamp((-3,1,3),450,3)
camera=bpy.data.objects.new("camera",bpy.data.cameras.new("Ortho_Review"))
scene.collection.objects.link(camera);scene.camera=camera
camera.data.type="ORTHO";camera.data.ortho_scale=2.4
cam_angles=[(0,0),(45,0),(90,0),(135,0),(180,0),(225,0),(270,0),(315,0),(0,90),(0,-90)]
rendered=[]
for az,el in cam_angles:
 a=math.radians(az);e=math.radians(el);center=Vector((0,0,.85))
 direction=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 camera.location=center+direction*4
 camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 rendered.append({"az":az,"el":el,"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
report={"status":"ANATOMICAL_FOUNDATION_ONLY_ART_APPROVAL_BLOCKED","official_makehuman_commit":REV,"input_sha256":source_hashes,"vertex_count":len(body_verts),"polygon_count":len(body_faces),"excluded_helper_faces":skipped_helper_faces,"morph_modified_vertices":shifted,"model_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),"render_views":rendered,"full_round_anatomy":True,"target_pose_completed":False,"garment_completed":False,"hair_completed":False,"art_similarity_gt_95_verified":False,"imagegen_target_is_not_calibrated_3d_truth":True}
(OUT/"quality.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"result":"ANATOMICAL_CC0_GLB_EXPORTED","vertices":len(verts),"renders":len(rendered),"quality":report["status"]}),flush=True)
