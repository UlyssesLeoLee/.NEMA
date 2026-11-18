#!/usr/bin/env python3
"""Ariadne V16 neutral Rigify prefit diagnostic.

This is deliberately NOT the final K-pose rig. It proves that the real
MakeHuman female base can be loaded, attached to Blender Rigify, skinned,
exported to glTF, and independently re-imported. No pose or art gate is
approved by this diagnostic.
"""
from __future__ import annotations
import bpy, json, math, os, pathlib, hashlib, urllib.request, traceback
from mathutils import Vector

ROOT = pathlib.Path(os.environ.get("GITHUB_WORKSPACE", pathlib.Path(__file__).resolve().parents[1]))
OUT = ROOT / "ariadne_v16_rig_prefit"
OUT.mkdir(parents=True, exist_ok=True)
SRC = "https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
ASSETS = {
    "base.obj": "3dobjs/base.obj",
    "female.target": "targets/macrodetails/caucasian-female-young.target",
}

def obtain(name, rel):
    p = OUT / name
    if not p.exists():
        urllib.request.urlretrieve(SRC + rel, str(p))
    if p.stat().st_size < 100_000:
        raise RuntimeError(f"Source asset too small: {name} ({p.stat().st_size})")
    return p

def load_makehuman():
    files = {k: obtain(k, v) for k, v in ASSETS.items()}
    verts, faces, group = [], [], None
    for line in files["base.obj"].open(encoding="utf-8", errors="replace"):
        if line.startswith("v "):
            x, y, z = map(float, line.split()[1:4])
            verts.append([x / 10.0, -z / 10.0, y / 10.0])
        elif line.startswith("g "):
            group = line.strip()[2:]
        elif line.startswith("f ") and group == "body":
            faces.append(tuple(int(w.split("/")[0]) - 1 for w in line.split()[1:]))
    if len(verts) != 19158 or len(faces) != 13378:
        raise RuntimeError(f"Unexpected MakeHuman topology: {len(verts)} vertices / {len(faces)} body faces")
    deltas = 0
    for line in files["female.target"].open(encoding="utf-8", errors="replace"):
        if not line or line[0] == "#":
            continue
        a = line.split()
        if len(a) == 4:
            i = int(a[0])
            dx, dy, dz = map(float, a[1:])
            verts[i][0] += dx / 10.0
            verts[i][1] -= dz / 10.0
            verts[i][2] += dy / 10.0
            deltas += 1
    if deltas < 10000:
        raise RuntimeError(f"Female morph incomplete: {deltas} deltas")
    return verts, faces, files, deltas

def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def bounds_from_faces(verts, faces):
    ids = sorted({i for face in faces for i in face})
    pts = [verts[i] for i in ids]
    return (
        Vector((min(p[0] for p in pts), min(p[1] for p in pts), min(p[2] for p in pts))),
        Vector((max(p[0] for p in pts), max(p[1] for p in pts), max(p[2] for p in pts))),
    )

def enable_rigify():
    try:
        bpy.ops.preferences.addon_enable(module="rigify")
        import rigify  # noqa: F401
    except Exception as exc:
        raise RuntimeError("Rigify add-on is not installed/enabled in this Blender build") from exc
    candidates = [n for n in dir(bpy.ops.object) if "human_metarig_add" in n]
    if "armature_human_metarig_add" not in candidates:
        raise RuntimeError(f"Rigify human metarig operator unavailable: {candidates}")

def make_body():
    verts, faces, files, deltas = load_makehuman()
    used = {i for f in faces for i in f}
    zmin = min(verts[i][2] for i in used)
    for v in verts:
        v[2] -= zmin
    mesh = bpy.data.meshes.new("MakeHuman_CC0_Female_19158V_13378F")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    human = bpy.data.objects.new("Female_Anatomy_CC0_Neutral_Rig_Prefit", mesh)
    bpy.context.collection.objects.link(human)
    for poly in mesh.polygons:
        poly.use_smooth = True
    mat = bpy.data.materials.new("Neutral_Anatomy_Rigging_Diagnostic")
    mat.diffuse_color = (0.72, 0.70, 0.66, 1)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.72, 0.70, 0.66, 1)
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.82
    mesh.materials.append(mat)
    lo, hi = bounds_from_faces(verts, faces)
    return human, files, deltas, lo, hi, len(used)

def fit_metarig_to_body(human, lo, hi):
    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.object
    if not meta or meta.type != "ARMATURE":
        raise RuntimeError("Rigify did not create a human metarig")
    meta.name = "Ariadne_V16_Human_Metarig_Prefit"
    meta.data.name = "Ariadne_V16_Human_Metarig_Data"
    # Proportional prefit only: uniform scale preserves the metarig's authored
    # joint axes. Fine landmark-by-landmark fitting is deliberately deferred
    # until approved orthographic references are available.
    all_z = [b.head_local.z for b in meta.data.bones] + [b.tail_local.z for b in meta.data.bones]
    mmin, mmax = min(all_z), max(all_z)
    target_h = hi.z - lo.z
    source_h = mmax - mmin
    if source_h <= 0 or target_h <= 0:
        raise RuntimeError("Invalid body/metarig height")
    scale = target_h / source_h
    meta.scale = (scale, scale, scale)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    meta.location = ((lo.x + hi.x) * 0.5, (lo.y + hi.y) * 0.5, lo.z - mmin * scale)
    bpy.context.view_layer.update()
    # Record explicit limitation: this is a proportional fit, not a joint-fit.
    meta["fit_status"] = "PROPORTIONAL_PREFIT_ONLY"
    meta["fit_scale"] = scale
    meta["anatomical_landmark_fit"] = False
    meta["art_pose_approved"] = False
    return meta

def generate_rig(meta):
    before = {o.name for o in bpy.context.scene.objects}
    activate(meta)
    result = bpy.ops.pose.rigify_generate()
    if "FINISHED" not in result:
        raise RuntimeError(f"Rigify generation failed: {result}")
    rig = meta.data.rigify_target_rig if hasattr(meta.data, "rigify_target_rig") else None
    if not rig or rig.type != "ARMATURE":
        created = [o for o in bpy.context.scene.objects if o.type == "ARMATURE" and o.name not in before]
        if not created:
            raise RuntimeError("Rigify returned success but no generated rig object was found")
        rig = created[-1]
    rig.name = "Ariadne_V16_Rigify_Neutral_Prefit"
    rig.data.name = "Ariadne_V16_Rigify_Neutral_Prefit_Data"
    rig["fit_status"] = "PROPORTIONAL_PREFIT_ONLY"
    rig["pose_status"] = "NEUTRAL_ONLY"
    rig["production_release"] = False
    return rig

def bind_weights(human, rig):
    activate(rig)
    human.select_set(True)
    bpy.context.view_layer.objects.active = rig
    result = bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    if "FINISHED" not in result:
        raise RuntimeError(f"Automatic skin weighting failed: {result}")
    bpy.context.view_layer.update()
    arm_mods = [m for m in human.modifiers if m.type == "ARMATURE" and m.object == rig]
    if not arm_mods:
        raise RuntimeError("Skinning failed: no Armature modifier targets generated rig")
    if len(human.vertex_groups) < 20:
        raise RuntimeError(f"Insufficient generated vertex groups: {len(human.vertex_groups)}")
    # Blender's heat-weight solver can leave non-normalized totals on complex
    # imported meshes. Normalize the generated weights explicitly before QA.
    activate(human)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    bpy.context.view_layer.update()
    return arm_mods

def weight_audit(human):
    groups = {g.index: g.name for g in human.vertex_groups}
    weighted = 0
    sums = []
    missing = 0
    for v in human.data.vertices:
        total = 0.0
        for a in v.groups:
            if a.group in groups:
                total += a.weight
        if total > 1e-6:
            weighted += 1
            sums.append(total)
        else:
            missing += 1
    if missing:
        raise RuntimeError(f"{missing} mesh vertices have no skin weights")
    if not sums or min(sums) < 0.90 or max(sums) > 1.10:
        raise RuntimeError("Skin weights are not normalized within 0.90–1.10")
    return {
        "vertex_count": len(human.data.vertices),
        "weighted_vertex_count": weighted,
        "unweighted_vertex_count": missing,
        "vertex_group_count": len(human.vertex_groups),
        "weight_sum_min": min(sums),
        "weight_sum_max": max(sums),
    }

def rig_structure_audit(rig):
    bones = rig.data.bones
    missing = []
    short = []
    broken_chains = []
    finger_chains = {}
    digit_prefixes = ("thumb", "f_index", "f_middle", "f_ring", "f_pinky")
    finger_segment_count = 0
    for side in ("L", "R"):
        for digit in digit_prefixes:
            chain = [f"DEF-{digit}.{i:02d}.{side}" for i in (1, 2, 3)]
            finger_chains[f"{digit}.{side}"] = chain
            for idx, name in enumerate(chain):
                bone = bones.get(name)
                if bone is None:
                    missing.append(name)
                    continue
                finger_segment_count += 1
                if bone.length < 0.005:
                    short.append(name)
                expected_parent = f"DEF-{digit}.{idx:02d}.{side}" if idx > 0 else f"DEF-hand.{side}"
                if not bone.parent or bone.parent.name != expected_parent:
                    broken_chains.append({
                        "bone": name,
                        "expected_parent": expected_parent,
                        "actual_parent": bone.parent.name if bone.parent else None,
                    })

        arm_chain = [
            f"DEF-upper_arm.{side}",
            f"DEF-upper_arm.{side}.001",
            f"DEF-forearm.{side}",
            f"DEF-forearm.{side}.001",
            f"DEF-hand.{side}",
        ]
        for idx, name in enumerate(arm_chain):
            bone = bones.get(name)
            if bone is None:
                missing.append(name)
                continue
            if bone.length < 0.005:
                short.append(name)
            if idx > 0 and bone.parent and bone.parent.name != arm_chain[idx - 1]:
                broken_chains.append({
                    "bone": name,
                    "expected_parent": arm_chain[idx - 1],
                    "actual_parent": bone.parent.name,
                })

        leg_chain = [
            f"DEF-thigh.{side}",
            f"DEF-thigh.{side}.001",
            f"DEF-shin.{side}",
            f"DEF-shin.{side}.001",
            f"DEF-foot.{side}",
            f"DEF-toe.{side}",
        ]
        for idx, name in enumerate(leg_chain):
            bone = bones.get(name)
            if bone is None:
                missing.append(name)
                continue
            if bone.length < 0.005:
                short.append(name)
            if idx > 0 and bone.parent and bone.parent.name != leg_chain[idx - 1]:
                broken_chains.append({
                    "bone": name,
                    "expected_parent": leg_chain[idx - 1],
                    "actual_parent": bone.parent.name,
                })

    result = {
        "finger_chain_count": len(finger_chains),
        "finger_segment_count": finger_segment_count,
        "expected_finger_chain_count": 10,
        "expected_finger_segment_count": 30,
        "arm_chain_count": 2,
        "leg_chain_count": 2,
        "missing_bones": missing,
        "short_bones": short,
        "broken_chains": broken_chains,
        "finger_chains": finger_chains,
        "joint_limit_state": "PENDING_POSE_AND_APPROVED_THREE_VIEW_LANDMARK_FIT",
        "motion_constraint_state": "NOT_APPLIED_TO_NEUTRAL_PREFIT",
    }
    if missing or short or broken_chains or finger_segment_count != 30:
        raise RuntimeError("Rig anatomy structure audit failed: " + json.dumps(result, ensure_ascii=False))
    return result


def export_and_reload(human, rig):
    # The editable .blend retains the complete 706-bone Rigify control rig.
    # The runtime GLB receives only the actual deform skeleton so controls,
    # mechanism bones and custom widgets do not become hundreds of runtime joints.
    deform_bones = [b for b in rig.data.bones if b.use_deform]
    if len(deform_bones) < 100:
        raise RuntimeError(f"Unexpectedly small Rigify deform skeleton: {len(deform_bones)} bones")
    group_names = {g.name for g in human.vertex_groups}
    missing_groups = [b.name for b in deform_bones if b.name not in group_names]
    if missing_groups:
        raise RuntimeError(f"Deform bones lack matching skin groups: {missing_groups[:12]}")

    export_data = bpy.data.armatures.new("Ariadne_V16_DeformOnly_Skin_Data")
    export_rig = bpy.data.objects.new("Ariadne_V16_DeformOnly_Skin", export_data)
    bpy.context.collection.objects.link(export_rig)
    export_rig.matrix_world = rig.matrix_world.copy()
    export_data.pose_position = "REST"
    activate(export_rig)
    bpy.ops.object.mode_set(mode="EDIT")
    edit_map = {}
    for bone in deform_bones:
        eb = export_data.edit_bones.new(bone.name)
        # Copy the complete rest matrix; Bone exposes matrix_local, not roll.
        eb.matrix = bone.matrix_local.copy()
        eb.use_deform = True
        edit_map[bone.name] = eb
    for bone in deform_bones:
        parent = bone.parent
        while parent is not None and not parent.use_deform:
            parent = parent.parent
        eb = edit_map[bone.name]
        if parent is not None:
            eb.parent = edit_map[parent.name]
            eb.use_connect = bool(bone.use_connect and (eb.parent.tail - eb.head).length < 1e-5)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Preserve the visible mesh transform while switching its skin target.
    mesh_world = human.matrix_world.copy()
    for mod in list(human.modifiers):
        if mod.type == "ARMATURE":
            human.modifiers.remove(mod)
    human.parent = export_rig
    human.matrix_parent_inverse = export_rig.matrix_world.inverted()
    human.matrix_world = mesh_world
    skin = human.modifiers.new("Ariadne_V16_DeformOnly_Skin", "ARMATURE")
    skin.object = export_rig
    skin.use_vertex_groups = True
    skin.use_bone_envelopes = False

    glb = OUT / "Ariadne_V16_Neutral_Rigify_Prefit_DIAGNOSTIC.glb"
    bpy.ops.object.select_all(action="DESELECT")
    human.select_set(True)
    export_rig.select_set(True)
    bpy.context.view_layer.objects.active = export_rig
    status = bpy.ops.export_scene.gltf(
        filepath=str(glb), export_format="GLB", use_selection=True,
        export_skins=True, export_animations=False, export_apply=False,
    )
    if "FINISHED" not in status or not glb.exists() or glb.stat().st_size < 100_000:
        raise RuntimeError("Deform-only skinned diagnostic GLB export failed")
    source_hash = hashlib.sha256(glb.read_bytes()).hexdigest()

    # Independently inspect the GLB JSON before a fresh Blender import.
    import struct
    raw = glb.read_bytes()
    if raw[:4] != b"glTF":
        raise RuntimeError("Exported file is not a GLB container")
    json_length, json_type = struct.unpack_from("<I4s", raw, 12)
    if json_type != b"JSON":
        raise RuntimeError("GLB JSON chunk missing")
    gltf = json.loads(raw[20:20 + json_length])
    glb_mesh_count = len(gltf.get("meshes", []))
    glb_skin_count = len(gltf.get("skins", []))
    glb_primitive_count = sum(len(m.get("primitives", [])) for m in gltf.get("meshes", []))
    glb_joint_count = len(gltf.get("skins", [{}])[0].get("joints", [])) if glb_skin_count else 0
    if glb_mesh_count != 1 or glb_primitive_count != 1 or glb_skin_count != 1 or glb_joint_count != len(deform_bones):
        raise RuntimeError(
            f"Unexpected runtime GLB structure: meshes={glb_mesh_count}, skins={glb_skin_count}, "
            f"joints={glb_joint_count}, expected_deform_bones={len(deform_bones)}"
        )

    # Remove every object datablock, including hidden Rigify widget meshes,
    # so the independent reload audit cannot count stale scene objects.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    imp = bpy.ops.import_scene.gltf(filepath=str(glb))
    if "FINISHED" not in imp:
        raise RuntimeError("Independent GLB reload failed")
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.data and len(o.data.polygons) > 0]
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    skin_meshes = [o for o in meshes if any(m.type == "ARMATURE" for m in o.modifiers)]
    skin_mods = [m for o in skin_meshes for m in o.modifiers if m.type == "ARMATURE"]
    if len(skin_meshes) != 1 or len(arms) != 1 or len(skin_mods) != 1:
        raise RuntimeError(
            f"Reload structure mismatch: meshes={len(meshes)} names={[o.name for o in meshes]}, "
            f"skinned_meshes={len(skin_meshes)}, armatures={len(arms)}, skin_modifiers={len(skin_mods)}"
        )
    return {
        "glb": glb.name,
        "glb_bytes": glb.stat().st_size,
        "glb_sha256": source_hash,
        "glb_mesh_count": glb_mesh_count,
        "glb_primitive_count": glb_primitive_count,
        "glb_skin_count": glb_skin_count,
        "glb_joint_count": glb_joint_count,
        "deform_bone_count": len(deform_bones),
        "reloaded_mesh_count": len(meshes),
        "reloaded_mesh_names": [o.name for o in meshes],
        "reloaded_skinned_mesh_count": len(skin_meshes),
        "reloaded_armature_count": len(arms),
        "reloaded_skin_modifier_count": len(skin_mods),
    }

def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    enable_rigify()
    human, files, morph_deltas, lo, hi, used_vertices = make_body()
    meta = fit_metarig_to_body(human, lo, hi)
    rig = generate_rig(meta)
    rig_structure = rig_structure_audit(rig)
    arm_mods = bind_weights(human, rig)
    weights = weight_audit(human)
    meta_bone_count = len(meta.data.bones)
    rig_bone_count = len(rig.data.bones)
    # Save editable prefit before independent GLB reload clears the scene.
    blend = OUT / "Ariadne_V16_Neutral_Rigify_Prefit_DIAGNOSTIC.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    reload = export_and_reload(human, rig)
    report = {
        "status": "PASS_NEUTRAL_RIGIFY_PREFIT_DIAGNOSTIC_ONLY",
        "production_approved": False,
        "art_pose_approved": False,
        "three_view_gate": "BLOCKED_PENDING_APPROVED_FRONT_RIGHT_BACK",
        "body_source": "MakeHuman CC0 base.obj + caucasian-female-young.target",
        "source_hashes": {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in files.items()},
        "source_vertices": 19158,
        "source_body_faces": 13378,
        "used_body_vertices": used_vertices,
        "female_morph_delta_count": morph_deltas,
        "body_bounds_min": list(lo),
        "body_bounds_max": list(hi),
        "metarig_bone_count": meta_bone_count,
        "generated_rig_bone_count": rig_bone_count,
        "fit_method": "UNIFORM_HEIGHT_SCALE_AND_CENTER_ALIGNMENT",
        "fit_status": "PROPORTIONAL_PREFIT_ONLY",
        "joint_landmark_fit": False,
        "armature_modifier_count": len(arm_mods),
        "skin_weight_audit": weights,
        "rig_structure_audit": rig_structure,
        "editable_blend": blend.name,
        "reload_audit": reload,
        "limitations": [
            "No approved side/back orthographic references exist yet.",
            "Metarig has proportional prefit only; individual joints have not been fitted to 3-view anatomical landmarks.",
            "No Ariadne K pose, hand/orb contact, corrective sculpt, garment simulation, hair sculpt, or gold-thread collision validation.",
            "This diagnostic is not a final Ariadne model and must not unlock release.",
        ],
    }
    (OUT / "Rigify_Prefit_QA.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ARIADNE_V16_RIGIFY_PREFIT_AUDIT", json.dumps(report, ensure_ascii=False))
    print("RIGIFY_PREFIT_DIAGNOSTIC_COMPLETE")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
