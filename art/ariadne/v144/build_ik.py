"""V143 real MakeHuman armature & source weights; joints control articulated pose.
V141 geometry is preserved only as an unapproved garment/hair engineering candidate.
"""
import bpy, math, json, hashlib, urllib.request, runpy
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v141/build_v141.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v144"
OUT.mkdir(parents=True,exist_ok=True)
REV="a8bc2d54ff0ac92e78ff71431b1023eda42bf482"
RIG_BASE=f"https://raw.githubusercontent.com/makehumancommunity/makehuman/{REV}/makehuman/data/rigs/"
def fetch(name):
 path=OUT/name
 urllib.request.urlretrieve(RIG_BASE+name,str(path))
 assert path.stat().st_size>10000
 return json.loads(path.read_text())
rig=fetch("default.mhskel")
weights=fetch("default_weights.mhw")
assert rig.get("license")=="CC0" and weights.get("license")=="CC0"
body=bpy.data.objects.get("Ariadne_CC0_Female_Anatomy_MASTER")
assert body is not None
old_mat=body.data.materials[0]
world=body.matrix_world.copy()
# Reconstruct original source vertices in exact MakeHuman face-index order,
# undoing previous V141 approximation, while retaining 3D costume meshes.
src=ROOT/"artifacts"/"ariadne_v139"
raw_vertices=[]
faces=[]
group=""
for ln in (src/"base.obj").open(errors="replace"):
 if ln.startswith("v "):
  raw_vertices.append(tuple(map(float,ln.split()[1:4])))
 elif ln.startswith("g "):
  group=ln.strip().split(maxsplit=1)[1]
 elif ln.startswith("f ") and group=="body":
  ids=[int(tok.split("/")[0])-1 for tok in ln.split()[1:]]
  faces.append(ids)
morph=[list(p) for p in raw_vertices]
for ln in (src/"female.target").open():
 t=ln.split()
 if len(t)!=4:continue
 try: idx=int(t[0]);vec=list(map(float,t[1:]))
 except ValueError:continue
 for i in range(3):morph[idx][i]+=vec[i]
used=sorted({x for face in faces for x in face})
idxmap={old:i for i,old in enumerate(used)}
assert len(used)==13380
mesh=bpy.data.meshes.new("V143_Official_CC0_Unmodified_Anatomy")
mesh.from_pydata([morph[i] for i in used],[],[[idxmap[x] for x in f] for f in faces])
mesh.update()
body.data=mesh
body.data.materials.append(old_mat)
for f in mesh.polygons:f.use_smooth=True
body["source"]="MakeHuman_CC0_Official_Exact_MeshAndWeights"
# Create official rig in world coordinates using stored joint source vertex IDs.
joint_centres={}
for name,ids in rig["joints"].items():
 valid=[idx for idx in ids if 0<=idx<len(morph)]
 if not valid:continue
 p=Vector((0,0,0))
 for idx in valid:p+=Vector(morph[idx])
 joint_centres[name]=world@(p/len(valid))
skeleton=bpy.data.armatures.new("MakeHuman_CC0_Skeleton")
arm=bpy.data.objects.new("V143_Official_Weighted_Skeleton",skeleton)
bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active=arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
created={}
# Build connected hierarchy from joint centroids.
for name,definition in rig["bones"].items():
 head=joint_centres.get(definition["head"])
 tail=joint_centres.get(definition["tail"])
 if head is None or tail is None:continue
 if (tail-head).length<.001:tail=head+Vector((0,0,.01))
 b=skeleton.edit_bones.new(name)
 b.head=head
 b.tail=tail
 created[name]=b
for name,definition in rig["bones"].items():
 if name not in created:continue
 parent=definition.get("parent")
 if parent in created and parent!=name:created[name].parent=created[parent]
bpy.ops.object.mode_set(mode="OBJECT")
arm.select_set(False)
assert len(created)>70, f"only {len(created)} armature bones"
# Apply exact source weight IDs to the face-filtered MakeHuman body.
assigned=0
for bone_name,pairs in weights["weights"].items():
 if bone_name not in created:continue
 group=body.vertex_groups.new(name=bone_name)
 for original_id,weight in pairs:
  current=idxmap.get(original_id)
  if current is None or weight<=0:continue
  group.add([current],float(weight),"REPLACE")
  assigned+=1
assert assigned>15000, f"not enough official weights {assigned}"
modifier=body.modifiers.new("Official_MH_Skinning","ARMATURE")
modifier.object=arm
body.parent=arm
body.matrix_parent_inverse=Matrix.Identity(4)
# For Blender weighting, body and armature transforms must share compatible
# world space: armature is at identity and rest bone coordinates world aligned.
# Retain body transform and source vertex coordinates as imported.
pose_names=["shoulder01.L","upperarm01.L","upperarm02.L","lowerarm01.L",
 "lowerarm02.L","wrist.L","shoulder01.R","upperarm01.R",
 "upperarm02.R","lowerarm01.R","lowerarm02.R","wrist.R"]
assert all(p in arm.pose.bones for p in pose_names)
# Art-directed arm gesture is applied through anatomically structured
# upper/lower arm pose channels, not vertex displacement.
# Do not claim target art agreement without separate calibrated reference.
for name in pose_names:
 arm.pose.bones[name].rotation_mode="XYZ"
# Locate which world side each arm is on based on actual shoulder coordinates.
xL=joint_centres[rig["bones"]["upperarm01.L"]["head"]].x
xR=joint_centres[rig["bones"]["upperarm01.R"]["head"]].x
ball_side="L" if xL< xR else "R"
rest_side="R" if ball_side=="L" else "L"
for side in (ball_side,rest_side):
 upper=arm.pose.bones["upperarm01."+side]
 upper2=arm.pose.bones["upperarm02."+side]
 lower=arm.pose.bones["lowerarm01."+side]
 lower2=arm.pose.bones["lowerarm02."+side]
 wrist=arm.pose.bones["wrist."+side]
 # Source arms spread laterally. Bend at shoulder and elbow.
 upper.rotation_euler=(math.radians(-15 if side==ball_side else 12),
                       math.radians(-52 if side==ball_side else 9),
                       math.radians(-4))
 upper2.rotation_euler=(0,math.radians(-16 if side==ball_side else 0),0)
 lower.rotation_euler=(0,math.radians(75 if side==ball_side else -12),math.radians(9))
 lower2.rotation_euler=(0,math.radians(12 if side==ball_side else 0),0)
 wrist.rotation_euler=(math.radians(10),math.radians(-12 if side==ball_side else 0),0)
# Finger joints: gentle natural flexion rather than rigid hand blocks.
for side in (ball_side,rest_side):
 for finger in range(1,6):
  for segment in range(1,4):
   key=f"finger{finger}-{segment}.{side}"
   if key in arm.pose.bones:
    pb=arm.pose.bones[key]
    pb.rotation_mode="XYZ"
    pb.rotation_euler.x=math.radians(12 if segment==1 else 9)
# V144: solve true pose-chain IK toward an elevated open-palm target.
# This replaces guessed Euler rotations as the decisive wrist placement.
for bone_name in ["upperarm01.","upperarm02.","lowerarm01.","lowerarm02.","wrist."]:
 pb=arm.pose.bones[bone_name+ball_side]
 pb.rotation_euler=(0,0,0)
target=bpy.data.objects.new("V144_Ball_Hand_IK_Target",None)
bpy.context.scene.collection.objects.link(target)
side_sign=-1 if ball_side=="L" else 1
# Actual joint geometry is authoritative; target is intentionally placed
# above and slightly in front of shoulder, rather than at arbitrary sphere spot.
shoulder_rest=joint_centres[rig["bones"]["upperarm01."+ball_side]["head"]]
target.location=(shoulder_rest.x+side_sign*.26,
                 shoulder_rest.y-.15,
                 shoulder_rest.z+.15)
wrist_ik=arm.pose.bones["wrist."+ball_side]
constraint=wrist_ik.constraints.new("IK")
constraint.target=target
constraint.chain_count=5
constraint.iterations=180
constraint.use_rotation=False
bpy.context.view_layer.update()
# Bake the evaluated IK onto actual pose channels and remove the temporary
# constraint, so glTF reimport contains the solution without external IK.
ik_target_coords_saved=tuple(target.location)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
bpy.context.scene.frame_set(1)
bpy.ops.nla.bake(frame_start=1,frame_end=1,step=1,
                 only_selected=True,visual_keying=True,
                 clear_constraints=True,use_current_action=True,
                 bake_types={"POSE"})
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()
actual_wrist=arm.matrix_world@arm.pose.bones["wrist."+ball_side].tail
ik_target_error=(actual_wrist-target.location).length
assert ik_target_error<.20, f"IK did not reach target: {ik_target_error}"
handbone=arm.pose.bones.get("wrist."+ball_side)
assert handbone
wrist_world=arm.matrix_world@handbone.tail
# Move gold ball exactly relative to the wrist articulation and flag that
# palm surface/individual fingers have not yet been independently proven.
balls=[o for o in bpy.data.objects if "Golden_Orb" in o.name and o.type=="MESH"]
assert balls
ball=balls[-1]
ball.location=wrist_world+Vector((0,.045,.065))
palm_dist=(ball.location-wrist_world).length
assert palm_dist<.13
# Existing one-piece thread should terminate near the updated orb;
# do not pretend these old control points physically track new palm.
for o in bpy.data.objects:
 if o.name.startswith("Single_Continuous_Gold_Thread") and o.type=="CURVE":
  points=o.data.splines[0].bezier_points
  points[-1].co=ball.location
  if len(points)>1: points[-2].co=ball.location+Vector((0,0,-.04))
# Snapshot armature and pose into real GLB, no scene-specific screenshot cheats.
scene=bpy.context.scene
outglb=OUT/"Ariadne_V144_CC0_IK_Pose_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(outglb),export_format="GLB",
    export_cameras=False,export_lights=False)
assert outglb.stat().st_size>200000
# Reimport in an empty scene, verifying actual encoded pose survives export.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(outglb))
imported=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert imported,"Exported GLB lost the actual armature"
assert len(imported[0].data.bones)>70
mesh_objs=[o for o in bpy.data.objects if o.type=="MESH"]
assert len(mesh_objs)>20
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=6
scene.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=640
scene.render.resolution_y=800
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=True
bpy.ops.object.light_add(type="AREA",location=(3,-3,4))
lamp=bpy.context.object;lamp.data.energy=800;lamp.data.size=4
bpy.ops.object.light_add(type="AREA",location=(-3,2,3))
lamp=bpy.context.object;lamp.data.energy=600;lamp.data.size=4
camera_data=bpy.data.cameras.new("V143_Art_Review_Camera")
camera=bpy.data.objects.new("V143_Camera",camera_data)
scene.collection.objects.link(camera);scene.camera=camera
camera_data.type="ORTHO";camera_data.ortho_scale=2.9
center=Vector((0,0,.85))
views=[(0,0),(45,0),(90,0),(135,0),(180,0),(225,0),(270,0),(315,0),(0,90),(0,-90)]
images=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 d=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
 camera.location=center+d*4.5
 camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V144_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 images.append({"az":az,"el":el,"png":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
report={
 "status":"REAL_CC0_RIGGED_ENGINEERING_CANDIDATE_ART_BLOCKED",
 "official_source_commit":REV,
 "actual_official_bone_count":len(created),
 "weighted_vertex_assignments":assigned,
 "original_cc0_body_vertices":len(mesh.vertices),
 "posed_ball_arm":ball_side,
 "ball_to_wrist_distance":palm_dist,
 "ik_target_error_m":ik_target_error,
 "hand_target_world":list(ik_target_coords_saved),
 "glb_sha256":hashlib.sha256(outglb.read_bytes()).hexdigest(),
 "glb":outglb.name,
 "real_blender_views":images,
 "target_art_similarity_verified":False,
 "correct_palmar_contact_verified":False,
 "garment_fitted_to_posed_mesh":False,
 "face_accuracy_verified":False,
 "266_view_react_executed":False
}
(OUT/"V144_AUDIT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("V144_IK_GLB_EXPORT",json.dumps({k:report[k] for k in ("actual_official_bone_count","weighted_vertex_assignments","ball_to_wrist_distance")}),flush=True)
