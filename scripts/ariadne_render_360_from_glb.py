"""Render exactly 360 one-degree frames from independently reloaded GLB (not a sprite).
Blender Workbench is used for reliable CPU structural turntable.
"""
import bpy, math, pathlib, json, hashlib
from mathutils import Vector
root=pathlib.Path.cwd()/"ariadne_art_output"
p=root/"Ariadne_Sculptural_Art_Draft.glb"
assert p.exists(),str(p)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
result=bpy.ops.import_scene.gltf(filepath=str(p))
assert "FINISHED" in result
parts=[obj for obj in bpy.context.scene.objects if obj.type=="MESH"]
assert len(parts)>30
scene=bpy.context.scene
camdata=bpy.data.cameras.new("Frozen_360_Camera")
cam=bpy.data.objects.new("Frozen_360_Camera",camdata)
bpy.context.collection.objects.link(cam)
scene.camera=cam
camdata.type="ORTHO";camdata.ortho_scale=2.37
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=320;scene.render.resolution_y=440
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.6
scene.display.shading.curvature_valley_factor=1.6
scene.display.shading.show_shadows=True
# camera position must be frozen in radius, vertical center, ortho scale
out=root/"360_PNG"
out.mkdir(exist_ok=True)
for angle in range(360):
    a=math.radians(angle)
    cam.location=(-5*math.sin(a),-5*math.cos(a),1.0)
    cam.rotation_euler=(Vector((.045,0,.81))-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(out/f"{angle:03d}.png")
    bpy.ops.render.render(write_still=True)
assert len(list(out.glob("*.png")))==360
data={"glb_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
 "glb_parts":len(parts),"frames":360,"step_degrees":1,"camera_radius":5.0,
 "fixed_target":[.045,0,.81],"orthographic_scale":2.37,
 "source":"Independently reimported GLB",
 "renderer":"Blender Workbench 5.x CPU",
 "art_reference_score":"NOT_MEASURABLE",
 "status":"DIAGNOSTIC_UNAPPROVED"}
(root/"Turntable_360_Audit.json").write_text(json.dumps(data,indent=2))
print("ACTUAL_GLB_360_FRAMES_COMPLETE",len(parts))
