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

def export_and_reload(human, rig):
    glb = OUT / "Ariadne_V16_Neutral_Rigify_Prefit_DIAGNOSTIC.glb"
    activate(rig)
    human.select_set(True)
    status = bpy.ops.export_scene.gltf(
        filepath=str(glb), export_format="GLB", use_selection=True,
        export_skins=True, export_animations=False, export_apply=False,
    )
    if "FINISHED" not in status or not glb.exists() or glb.stat().st_size < 100_000:
        raise RuntimeError("Skinned diagnostic GLB export failed")
    source_hash = hashlib.sha256(glb.read_bytes()).hexdigest()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    imp = bpy.ops.import_scene.gltf(filepath=str(glb))
    if "FINISHED" not in imp:
        raise RuntimeError("Independent GLB reload failed")
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if not meshes or not arms:
        raise RuntimeError(f"Reload lost skinned mesh/armature: meshes={len(meshes)} arms={len(arms)}")
    skin_mods = [m for o in meshes for m in o.modifiers if m.type == "ARMATURE"]
    if not skin_mods:
        raise RuntimeError("Reloaded GLB contains no armature skin modifier")
    return {
        "glb": glb.name,
        "glb_bytes": glb.stat().st_size,
        "glb_sha256": source_hash,
        "reloaded_mesh_count": len(meshes),
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
