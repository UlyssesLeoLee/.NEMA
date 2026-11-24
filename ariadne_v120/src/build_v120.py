#!/usr/bin/env python3
"""V120: real MakeHuman body, saved Rigify source, joint-driven engineering candidate.
Art gate is always BLOCKED without independent V20 references.
No capsule body, vertex pulling, replacement mesh, or fake contact.
"""
import bpy, os, pathlib, json, math, hashlib, struct, traceback
from mathutils import Vector
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE",pathlib.Path(__file__).resolve().parents[2]))
OUT=ROOT/"ariadne_v120"/"output"; OUT.mkdir(parents=True,exist_ok=True)
def fail(msg): raise RuntimeError(msg)
def main():
    blends=list((ROOT/"ariadne_v120"/"input").rglob("Ariadne_V16_Neutral_Rigify_Prefit_DIAGNOSTIC.blend"))
    if len(blends)!=1: fail("V16_REAL_RIGIFY_BLEND_MISSING_OR_AMBIGUOUS")
    bpy.ops.wm.open_mainfile(filepath=str(blends[0]))
    armatures=[o for o in bpy.data.objects if o.type=="ARMATURE"]
    rigs=[o for o in armatures if "Rigify_Neutral_Prefit" in o.name and "Metarig" not in o.name]
    humans=[o for o in bpy.data.objects if o.type=="MESH" and "Female_Anatomy_CC0_Neutral_Rig_Prefit" in o.name]
    if len(rigs)!=1 or len(humans)!=1: fail("AUTHORITATIVE_RIG_OR_BODY_MISSING")
    rig=rigs[0]; human=humans[0]
    if len(human.data.vertices)!=19158: fail("OFFICIAL_MAKEHUMAN_VERTEX_COUNT_MISMATCH")
    if len(human.data.polygons)!=13378: fail("OFFICIAL_MAKEHUMAN_BODY_FACE_COUNT_MISMATCH")
    if len(rig.data.bones)<500 or not any(m.type=="ARMATURE" and m.object==rig for m in human.modifiers):
        fail("REAL_RIGIFY_SKIN_INTEGRITY_FAIL")
    # Prove physics-dependent pose is on actual skeleton, not a baked vertex edit.
    ctrl_names=["upper_arm_fk.L","forearm_fk.L","hand_fk.L",
                "upper_arm_fk.R","forearm_fk.R","hand_fk.R"]
    missing=[n for n in ctrl_names if n not in rig.pose.bones]
    if missing: fail("FK_CONTROLS_UNAVAILABLE: "+repr(missing))
    for side in ("L","R"):
        par=rig.pose.bones.get("upper_arm_parent."+side)
        if par is None or "IK_FK" not in par:
            fail("RIGIFY_FK_SWITCH_NOT_AUDITED_"+side)
        par["IK_FK"]=0.0
    bpy.context.view_layer.update()
    def evaluated():
        deps=bpy.context.evaluated_depsgraph_get()
        ev=human.evaluated_get(deps); me=ev.to_mesh()
        verts=[ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
        return verts
    before=evaluated()
    # SMALL exploratory FK pose, deliberately not claiming artistic correctness.
    pose_deg={"upper_arm_fk.L":(0,0,18),
              "forearm_fk.L":(0,0,30),
              "hand_fk.L":(0,-7,0),
              "upper_arm_fk.R":(0,0,-7),
              "forearm_fk.R":(0,0,12),
              "hand_fk.R":(0,5,0)}
    for name,angles in pose_deg.items():
        pb=rig.pose.bones[name];pb.rotation_mode="XYZ"
        pb.rotation_euler=tuple(math.radians(q) for q in angles)
    bpy.context.view_layer.update()
    after=evaluated()
    disps=[(a-b).length for a,b in zip(after,before)]
    max_move=max(disps); moved=sum(1 for d in disps if d>0.0005)
    if max_move<0.005 or moved<100: fail("POSE_DID_NOT_DEFORM_REAL_BODY")
    # Preserve full control rig and live modifiers for continued constrained IK.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"V120_RealRig_Posed_Editable_NOT_ART.blend"))
    # Export deform-only skeleton with copied real pose matrices and original weights.
    deform=[b for b in rig.data.bones if b.use_deform]
    if len(deform)<100: fail("DEFORM_CHAIN_TOO_SMALL")
    data=bpy.data.armatures.new("V120_DeformOnly_Data")
    export=bpy.data.objects.new("V120_Live_GLTF_Skin",data)
    bpy.context.collection.objects.link(export);export.matrix_world=rig.matrix_world.copy()
    bpy.ops.object.select_all(action="DESELECT");export.select_set(True)
    bpy.context.view_layer.objects.active=export
    bpy.ops.object.mode_set(mode="EDIT")
    emap={}
    for b in deform:
        eb=data.edit_bones.new(b.name);eb.matrix=b.matrix_local.copy()
        eb.use_deform=True;emap[b.name]=eb
    for b in deform:
        p=b.parent
        while p and not p.use_deform:p=p.parent
        if p:emap[b.name].parent=emap[p.name]
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in deform:
        source=rig.pose.bones.get(b.name)
        if source: export.pose.bones[b.name].matrix=source.matrix.copy()
    bpy.context.view_layer.update()
    # Exchange armature modifier WITHOUT applying deformation or changing anatomy topology.
    original_world=human.matrix_world.copy()
    for mod in list(human.modifiers):
        if mod.type=="ARMATURE":human.modifiers.remove(mod)
    human.parent=export;human.matrix_parent_inverse=export.matrix_world.inverted()
    human.matrix_world=original_world
    mod=human.modifiers.new("V120_RealSkeletonSkin","ARMATURE");mod.object=export
    mod.use_vertex_groups=True;mod.use_bone_envelopes=False
    glb=OUT/"V120_MakeHuman_LiveSkinnedPose_ENGINEERING_NOT_ART.glb"
    bpy.ops.object.select_all(action="DESELECT")
    human.select_set(True);export.select_set(True)
    bpy.context.view_layer.objects.active=export
    result=bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
        use_selection=True,export_skins=True,export_animations=False,export_apply=False)
    if "FINISHED" not in result or glb.stat().st_size<100000:fail("GLB_EXPORT_FAILED")
    raw=glb.read_bytes()
    if raw[:4]!=b"glTF":fail("GLB_MAGIC_INVALID")
    n,typ=struct.unpack_from("<I4s",raw,12)
    if typ!=b"JSON":fail("GLB_JSON_INVALID")
    gltf=json.loads(raw[20:20+n])
    if len(gltf.get("skins",[]))!=1:fail("GLB_LIVE_SKIN_MISSING")
    joints=len(gltf["skins"][0]["joints"])
    if joints!=len(deform):fail("GLB_JOINT_COUNT_MISMATCH")
    # Separate re-import to prevent false positive from current scene.
    exported_body_vertex_count=len(human.data.vertices)
    exported_body_face_count=len(human.data.polygons)
    for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    loaded=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    if not loaded or not any(m.type=="ARMATURE" for o in loaded for m in o.modifiers):
        fail("FRESH_GLB_RELOAD_SKIN_FAILED")
    scene=bpy.context.scene
    camera=bpy.data.objects.new("Audit_Orthographic",bpy.data.cameras.new("AuditCamera"))
    bpy.context.collection.objects.link(camera);camera.data.type="ORTHO"
    camera.data.ortho_scale=2.1;scene.camera=camera
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
    scene.render.resolution_x=288;scene.render.resolution_y=384
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG"
    target=Vector((0,0,0.82))
    cam={}
    for deg in range(0,360,15):
        t=math.radians(deg)
        camera.location=(3.4*math.sin(t),-3.4*math.cos(t),0.82)
        camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(OUT/("v120_%03d.png"%deg))
        bpy.ops.render.render(write_still=True)
        cam[str(deg)]={"location":list(camera.location),"ortho_scale":camera.data.ortho_scale}
    qa={"status":"ENGINEERING_POSED_NOT_ART_APPROVED",
        "source":"V16 MakeHuman CC0 original female 19158 vertices + Blender Rigify control rig",
        "raw_art_original_24_present":False,"art_similarity_measured":False,
        "art_approval":False,"k_pose_art_matched":False,
        "support_hand_ball_contact_approved":False,"garment_art_solved":False,
        "live_gltf_skin_count":1,"live_gltf_joint_count":joints,
        "body_vertices":exported_body_vertex_count,"body_faces":exported_body_face_count,
        "pose_max_vertex_motion_m":max_move,"pose_vertices_moved_gt_0p5mm":moved,
        "glb_bytes":glb.stat().st_size,
        "glb_sha256":hashlib.sha256(raw).hexdigest(),
        "images_from_reloaded_glb":24,"camera_yaw_manifest":cam,
        "pose_controls_degrees":pose_deg,
        "gates":{"P05_anatomical_source":"PASS","P05_joint_local_movement":"PASS",
                 "P05_live_skin_export":"PASS","P02_V20_24_anchors":"BLOCKED",
                 "P06_palm_orb_art":"BLOCKED","P07_garment":"BLOCKED",
                 "P16_24x95_percent_art":"BLOCKED"}}
    (OUT/"V120_AUDIT.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
    print("V120_REAL_CLOUD_POSE_AUDIT",json.dumps({k:v for k,v in qa.items() if k!="camera_yaw_manifest"}))
if __name__=="__main__":
    try: main()
    except Exception:
        traceback.print_exc()
        raise
