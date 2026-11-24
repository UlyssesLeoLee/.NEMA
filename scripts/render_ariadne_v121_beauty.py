#!/usr/bin/env python3
"""Physically lit beauty renders of V121 real GH GLB. Geometry is unchanged."""
import bpy,math,pathlib,json,hashlib,os
from mathutils import Vector
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE",pathlib.Path(__file__).resolve().parents[1]))
OUT=ROOT/"ariadne_v121_beauty";OUT.mkdir(exist_ok=True)
inp=ROOT/"ariadne_v121_beauty_input"/"Ariadne_V121_Complete_Princess_Model_CANDIDATE_NOT_ART_APPROVED.glb"
assert inp.exists(),str(inp)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(inp))
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
assert len(meshes)>=30
# Do not alter sculpture vertices, camera-dependent geometry or pose.
src_counts={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in meshes}
for mat in bpy.data.materials:
    mat.use_nodes=True
    p=mat.node_tree.nodes.get("Principled BSDF")
    if not p:continue
    n=mat.name.lower()
    if "gold" in n or "diadem" in n:
        p.inputs["Base Color"].default_value=(0.66,0.33,0.055,1)
        p.inputs["Metallic"].default_value=.83
        p.inputs["Roughness"].default_value=.29
    elif "hair" in n:
        p.inputs["Base Color"].default_value=(.70,.64,.54,1)
        p.inputs["Metallic"].default_value=0
        p.inputs["Roughness"].default_value=.54
    elif "pedestal" in n or "base" in n:
        p.inputs["Base Color"].default_value=(.49,.46,.44,1)
        p.inputs["Roughness"].default_value=.62
    elif "linen" in n or "cloth" in n:
        p.inputs["Base Color"].default_value=(.82,.73,.58,1)
        p.inputs["Roughness"].default_value=.68
    else:
        p.inputs["Base Color"].default_value=(.81,.76,.68,1)
        p.inputs["Roughness"].default_value=.58
    if "gold" not in n:
        noise=mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value=135
        noise.inputs["Detail"].default_value=2.2
        bump=mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value=.07
        bump.inputs["Distance"].default_value=.0017
        mat.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"],p.inputs["Normal"])
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=12
scene.cycles.use_denoising=True
scene.render.resolution_x=480;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
world=bpy.data.worlds.new("Ariadne_Museum_Dark_Blue")
scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.027,.034,.061,1)
bg.inputs["Strength"].default_value=.35
def light(name,loc,energy,color,size):
 data=bpy.data.lights.new(name,"AREA");data.energy=energy;data.shape="DISK";data.size=size;data.color=color
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
 o.location=loc;o.rotation_euler=(Vector((0,0,.88))-o.location).to_track_quat("-Z","Y").to_euler()
light("Sculpture_Key_Light",(-2.5,-3.8,4.2),850,(1,.85,.66),3.4)
light("Sculpture_Fill_Light",(3.0,-1.4,2.0),400,(.68,.79,1),3.2)
light("Sculpture_Rim_Light",(1.5,2.9,3.4),950,(1,.92,.81),2.0)
cam=bpy.data.objects.new("Museum_Locked_Camera",bpy.data.cameras.new("Ariadne_Camera"))
bpy.context.collection.objects.link(cam)
cam.data.type="ORTHO";cam.data.ortho_scale=2.02
scene.camera=cam
target=Vector((0,0,.78))
views=[0,90,180,270]
for deg in views:
 a=math.radians(deg)
 cam.location=(3.8*math.sin(a),-3.8*math.cos(a),1.1)
 cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 scene.render.filepath=str(OUT/f"V121_REAL_GLB_MUSEUM_{deg:03d}.png")
 bpy.ops.render.render(write_still=True)
 print("RENDERED_REAL_GLB_BEAUTY",deg,flush=True)
for o in meshes:
 assert (len(o.data.vertices),len(o.data.polygons))==src_counts[o.name]
report={"status":"PHYSICALLY_LIT_REAL_GLB_NOT_ART_APPROVED",
 "input_glb_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
 "unmodified_geometry_object_count":len(meshes),"views":views,
 "render_engine":"Blender Cycles 12 samples",
 "render_only_procedural_surface_bump_not_baked_into_GLB":True,
 "original_V20_24_art_accuracy_not_measured":True}
(OUT/"BEAUTY_RENDER_QA.json").write_text(json.dumps(report,indent=2))
print("BEAUTY_REAL_GLB_AUDIT",json.dumps(report),flush=True)
