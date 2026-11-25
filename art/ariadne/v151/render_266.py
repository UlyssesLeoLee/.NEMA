"""Render all 266 unique spherical positions from exactly one reimported actual V149 GLB.
DIAGNOSTIC ONLY. Never count renders as 2D->3D->2D ReAct cycles.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"artifacts"/"ariadne_v151"
OUT.mkdir(parents=True,exist_ok=True)
glb=ROOT/"artifacts"/"ariadne_v149"/"Ariadne_V149_Corrected_Face_Hair_Engineering_NOT_ART_APPROVED.glb"
assert glb.is_file(),str(glb)
glbsha=hashlib.sha256(glb.read_bytes()).hexdigest()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
scene=bpy.context.scene
assert len([o for o in bpy.data.objects if o.type=="ARMATURE"])==1
# An actual GLB rendering: no per-camera pose or mesh edits.
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
minz=min((o.matrix_world@Vector(c)).z for o in meshes for c in o.bound_box)
maxz=max((o.matrix_world@Vector(c)).z for o in meshes for c in o.bound_box)
minx=min((o.matrix_world@Vector(c)).x for o in meshes for c in o.bound_box)
maxx=max((o.matrix_world@Vector(c)).x for o in meshes for c in o.bound_box)
miny=min((o.matrix_world@Vector(c)).y for o in meshes for c in o.bound_box)
maxy=max((o.matrix_world@Vector(c)).y for o in meshes for c in o.bound_box)
target=Vector(((minx+maxx)/2,(miny+maxy)/2,(minz+maxz)/2))
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.render.resolution_x=280
scene.render.resolution_y=370
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.world.color=(.12,.12,.12)
cam_data=bpy.data.cameras.new("V151_Canonical_SphereCamera")
cam=bpy.data.objects.new("V151_Canonical_SphereCamera",cam_data)
scene.collection.objects.link(cam)
scene.camera=cam
cam_data.type="ORTHO"
cam_data.ortho_scale=max((maxz-minz)*1.15,2.65)
views=[(az,el) for el in range(-75,76,15) for az in range(0,360,15)]
views+=[(0,90),(0,-90)]
assert len(views)==266 and len(set(views))==266
registered={(0,0),(45,0),(90,0),(180,0),(270,0),(315,0),(0,90),(0,-90)}
records=[]
for idx,(az,el) in enumerate(views):
    a=math.radians(az);e=math.radians(el)
    unit=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
    cam.location=target+unit*4.8
    # At exact poles, stable camera up is chosen consistently to avoid inversion.
    if abs(el)==90:
        up=Vector((0,1 if el==90 else -1,0))
        normal=(target-cam.location).normalized()
        right=normal.cross(up).normalized()
        newup=right.cross(normal).normalized()
        from mathutils import Matrix
        rot=Matrix(((right.x,newup.x,-normal.x),
                    (right.y,newup.y,-normal.y),
                    (right.z,newup.z,-normal.z))).to_4x4()
        cam.rotation_euler=rot.to_euler()
    else:
        cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    name=f"V151_AZ{az:03d}_EL{el:+04d}.png"
    f=OUT/name
    scene.render.filepath=str(f)
    bpy.ops.render.render(write_still=True)
    records.append({"view_id":f"AZ{az:03d}_EL{el:+04d}",
        "az":az,"el":el,"image":name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
        "registered_art_available":(az,el) in registered,
        "pixel_calibrated_art_reference":False,
        "actual_2d_redraws_this_camera":0,
        "actual_3d_revisions_this_camera":0,
        "real_2d_3d_2d_react_cycles_this_camera":0})
    if idx%40==0:print("V151_SPHERE_RENDERED",idx+1,flush=True)
report={
 "status":"REAL_266_GLB_CAMERA_DIAGNOSTICS_ART_BLOCKED",
 "input_reimported_glb_sha256":glbsha,
 "actual_unique_spherical_renders":266,
 "independent_user_art_view_candidates":len(registered),
 "approved_pixel_calibrated_view_count":0,
 "required_art_react_cycles_per_view":30,
 "required_total_art_react_cycles":7980,
 "actual_art_react_cycles":0,
 "render_changes_do_not_count_as_art_react":True,
 "model_center":list(target),
 "camera_ortho_scale":cam_data.ortho_scale,
 "records":records
}
(OUT/"V151_SPHERE_AUDIT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("V151_RENDER_DONE",json.dumps({k:report[k] for k in
 ("actual_unique_spherical_renders","actual_art_react_cycles","status")}),flush=True)
