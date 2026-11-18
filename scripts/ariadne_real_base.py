#!/usr/bin/env python3
"""Actual MakeHuman CC0 mesh import, female morph application, GLB export and 24-view diagnostic.
Run with blender -b -t 2 --python scripts/ariadne_real_base.py
Never represent this neutral anatomical master as the approved Ariadne sculpture.
"""
import bpy, math, os, json, hashlib, urllib.request, pathlib, tempfile
from mathutils import Vector
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE", pathlib.Path(__file__).resolve().parents[1]))
OUT=ROOT/"ariadne_real_artifacts"
OUT.mkdir(parents=True, exist_ok=True)
URL="https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
ASSETS={
    "base.obj": "3dobjs/base.obj",
    "female.target":"targets/macrodetails/caucasian-female-young.target",
}
def obtain(name,src):
    p=OUT/name
    if not p.exists():
        urllib.request.urlretrieve(URL+src,str(p))
    assert p.stat().st_size>100000, (name,p.stat().st_size)
    return p
files={k:obtain(k,v) for k,v in ASSETS.items()}
vertices=[]; faces=[]; group=None; all_faces=0
for line in files["base.obj"].open():
    if line.startswith("v "):
        x,y,z=map(float,line.split()[1:4])
        # Original MakeHuman: +Y up. Output: +Z up, -Y front.
        vertices.append([x/10.,-z/10.,y/10.])
    elif line.startswith("g "): group=line.strip()[2:]
    elif line.startswith("f "):
        all_faces+=1
        if group=="body":
            ids=[int(w.split("/")[0])-1 for w in line.split()[1:]]
            faces.append(ids)
assert len(vertices)==19158, len(vertices)
assert len(faces)==13378, len(faces)
morph_count=0
for line in files["female.target"].open():
    if not line or line[0]=="#": continue
    a=line.split()
    if len(a)==4:
        i=int(a[0]); dx,dy,dz=map(float,a[1:])
        # Female target original coordinates same as base OBJ
        vertices[i][0]+=dx/10.;vertices[i][1]-=dz/10.;vertices[i][2]+=dy/10.
        morph_count+=1
assert morph_count>10000,morph_count
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new("MakeHuman_CC0_13378_original_quads")
mesh.from_pydata(vertices,[],faces)
mesh.update()
human=bpy.data.objects.new("Female_Anatomy_CC0_Real_Base",mesh)
bpy.context.collection.objects.link(human)
# The unused rig/helper vertices remain in the imported positional array but are not rendered.
# Rebuild normals according to original topology (no silhouette extrusion).
for poly in mesh.polygons: poly.use_smooth=True
mat=bpy.data.materials.new("Diagnostic_Neutral_Stone_NOT_FINAL")
mat.diffuse_color=(0.73,0.72,0.69,1)
mat.use_nodes=True
bsdf=mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value=(0.73,0.72,0.69,1)
bsdf.inputs["Metallic"].default_value=0.0
bsdf.inputs["Roughness"].default_value=0.85
human.data.materials.append(mat)
# Offset feet to z=0 without changing anatomical proportions
zmin=min(v[2] for v in vertices[:13380])
human.location.z=-zmin
bpy.context.view_layer.objects.active=human
human.select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"MakeHuman_CC0_Female_Anatomy_Editable.blend"))
export_status=bpy.ops.export_scene.gltf(filepath=str(OUT/"MakeHuman_CC0_Female_Anatomy_DIAGNOSTIC.glb"),export_format="GLB",use_selection=True)
assert "FINISHED" in export_status, f"GLB export was not FINISHED: {export_status}"
assert (OUT/"MakeHuman_CC0_Female_Anatomy_DIAGNOSTIC.glb").stat().st_size>100000
# fixed camera, physically same mesh at all angles
world=bpy.context.scene.world
world.color=(0.65,0.65,0.65)
for ang,energy,sz in [(-35,650,3),(110,300,2.5)]:
    a=math.radians(ang)
    light=bpy.data.lights.new("Area"+str(ang),"AREA")
    light.energy=energy;light.shape="DISK";light.size=sz
    o=bpy.data.objects.new("Area"+str(ang),light)
    bpy.context.collection.objects.link(o)
    o.location=(3*math.sin(a),-3*math.cos(a),2.5)
    direction=Vector((0,0,0.95))-o.location
    o.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
camd=bpy.data.cameras.new("Locked_Orthographic_Camera")
camera=bpy.data.objects.new("Locked_Orthographic_Camera",camd)
bpy.context.collection.objects.link(camera)
camd.type="ORTHO";camd.ortho_scale=2.02
scene=bpy.context.scene;scene.camera=camera
scene.render.engine="CYCLES";scene.cycles.samples=12
scene.render.resolution_x=360;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.film_transparent=False
scene.view_settings.view_transform="Standard"
target=Vector((0,0,0.88))
for deg in range(0,360,15):
    a=math.radians(deg)
    camera.location=(-4*math.sin(a),-4*math.cos(a),0.88)
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(OUT/f"neutral_{deg:03d}.png")
    bpy.ops.render.render(write_still=True)
# Verify exported file by importing into a fresh scene
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(OUT/"MakeHuman_CC0_Female_Anatomy_DIAGNOSTIC.glb"))
reloaded=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert reloaded and sum(len(o.data.polygons) for o in reloaded)>=13378
report={"status":"DIAGNOSTIC_UNAPPROVED","pipeline":"actual MakeHuman mesh + female target + Blender GLB export",
"vertex_source_count":len(vertices),"body_quads_source_count":len(faces),
"female_target_deltas":morph_count,"source_hashes_sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()},
"exported_glb_bytes":(OUT/"MakeHuman_CC0_Female_Anatomy_DIAGNOSTIC.glb").stat().st_size,
"reimport_mesh_count":len(reloaded),"reimport_polygon_count":sum(len(o.data.polygons) for o in reloaded),
"art_reference_views":1,"art_similarity":"NOT_MEASURABLE",
"anatomy_approved":False,"sculpt_pose_approved":False,
"limitations":["This is a genuine neutral female anatomical starting mesh, not Ariadne's K pose.","No cloth or custom sculpt, hair or gold thread yet.","Reference only provides front view, independent 24-angle art fidelity cannot be scored.","UV/PBR production deferred until sculptural geometry is approved."]}
(OUT/"REAL_EXECUTION_AUDIT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print("REAL_GLTF_RELOAD_SUCCESS", json.dumps(report,ensure_ascii=False))
