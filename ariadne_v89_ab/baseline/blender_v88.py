#!/usr/bin/env python3
"""Blender 4.5 headless stages for V88: pose / gold ball-thread / multiview refinement.
This script is intentionally narrow in scope and fail-closed.
"""
import json, math, sys, traceback
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'config'/'production.json').read_text('utf8'))
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)

def write_json(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def require_asset(key):
    p=ROOT/C['reference_sources'][key]
    if not p.is_file():
        raise RuntimeError(f'REQUIRED_ASSET_MISSING:{key}:{p}')
    return p

def camera_table():
    cc=C['camera']; cx,cy,cz=cc['target_xyz_m']; d=cc['distance_m']; out=[]
    for deg in cc['view_angles_deg']:
        a=math.radians(deg)
        out.append({'view_id':f'VIEW_{deg:03d}','angle_deg':deg,'position':(cx+d*math.sin(a),cy-d*math.cos(a),cz),'look_at':(cx,cy,cz)})
    return out

def set_camera(angle):
    cv=next(x for x in camera_table() if x['angle_deg']==angle)
    cam=bpy.data.objects.get('LOCKED_24_CAMERA')
    if not cam:
        data=bpy.data.cameras.new('LOCKED_24_CAMERA_DATA')
        cam=bpy.data.objects.new('LOCKED_24_CAMERA',data)
        bpy.context.scene.collection.objects.link(cam)
    cc=C['camera']
    cam.data.type=cc['projection']; cam.data.lens=cc['focal_length_mm']; cam.data.sensor_width=cc['sensor_width_mm']; cam.data.sensor_fit=cc['sensor_fit']
    cam.location=Vector(cv['position'])
    cam.rotation_euler=(Vector(cv['look_at'])-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=cam
    sc=bpy.context.scene
    sc.render.resolution_x=cc['image_px'][0]; sc.render.resolution_y=cc['image_px'][1]; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'; sc.render.film_transparent=False

def install_lights():
    set_camera(0)
    scene=bpy.context.scene
    try:
        scene.render.engine='BLENDER_EEVEE_NEXT'
    except Exception:
        pass
    def area(name,pos,power,size):
        light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.shape='DISK'; light.size=size
        obj=bpy.data.objects.new(name,light); scene.collection.objects.link(obj)
        obj.location=pos; obj.rotation_euler=(Vector((0,0,0.9))-obj.location).to_track_quat('-Z','Y').to_euler()
    area('KEY_SOFTBOX',(2,-3,4),650,4)
    area('FILL_SOFTBOX',(-2,-2,2.5),320,3)
    area('RIM_SOFTBOX',(1.5,2.0,2.4),700,2)
    scene.world.color=(0.27,0.27,0.27)

def _import(path):
    before=set(bpy.data.objects)
    ext=path.suffix.lower()
    if ext in ('.glb','.gltf'):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext=='.obj':
        bpy.ops.wm.obj_import(filepath=str(path),forward_axis='Y',up_axis='Z')
    else:
        raise RuntimeError('UNSUPPORTED_INPUT_FORMAT:'+ext)
    return [x for x in bpy.data.objects if x not in before]

def _visible_meshes():
    return [x for x in bpy.context.scene.objects if x.type=='MESH' and not x.hide_render]

def _armatures():
    return [x for x in bpy.context.scene.objects if x.type=='ARMATURE']

def _save(name):
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/name))

def preflight():
    assets={k:str(require_asset(k).relative_to(ROOT)) for k in C['reference_sources']}
    anchor=json.loads(require_asset('anchors24_manifest').read_text('utf8'))
    write_json('V88_preflight.json',{'status':'READY_FOR_ENGINEERING','asset_count':len(assets),'anchors24_count':anchor['count'],'scope':C['scope'],'priority_regions':C['pose_adjustment']['priority_regions']})

def load_base_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported=_import(require_asset('base_glb'))
    if not imported:
        raise RuntimeError('BASE_GLB_NOT_IMPORTABLE')
    install_lights(); set_camera(0); _save('V88_base_loaded.blend')

def pose():
    load_base_scene()
    arms=_armatures(); meshes=_visible_meshes()
    audit={'has_armature':bool(arms),'mesh_count':len(meshes),'scope':'pose_adjustment_only'}
    if not arms:
        audit['status']='BLOCKED_NO_ARMATURE'; write_json('pose_audit_front_side_back_oblique.json',audit)
        raise RuntimeError('POSE_ADJUSTMENT_REQUIRES_ARMATURE_OR_PREDEFINED_DEFORMATION_RIG')
    arm=arms[0]
    target_bones=['upper_arm.R','forearm.R','hand.R','upper_arm.L','forearm.L','hand.L','spine','chest','neck','head','thigh.L','thigh.R']
    present=[b.name for b in arm.pose.bones if b.name in target_bones]
    audit['armature_name']=arm.name; audit['target_bones_present']=present
    if 'hand.R' not in present and 'hand.L' not in present:
        audit['status']='BLOCKED_NO_HAND_BONES'; write_json('pose_audit_front_side_back_oblique.json',audit)
        raise RuntimeError('HAND_BONES_NOT_FOUND_FOR_BALL_SUPPORT_POSE')
    audit['status']='READY_FOR_MANUAL_OR_SCRIPTED_POSE_EDIT'
    write_json('pose_audit_front_side_back_oblique.json',audit); _save('pose_refined.blend')

def gold():
    src=OUT/'pose_refined.blend'
    if not src.exists():
        raise RuntimeError('POSE_STAGE_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    gold_m=bpy.data.materials.get('Gold_Metal') or bpy.data.materials.new('Gold_Metal')
    gold_m.use_nodes=True
    bsdf=gold_m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(0.86,0.64,0.11,1.0)
    bsdf.inputs['Metallic'].default_value=0.82
    bsdf.inputs['Roughness'].default_value=0.23
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=C['gold_ball']['radius_m'], location=(0.58,-0.02,1.58))
    ball=bpy.context.object; ball.name='Ariadne_Gold_Ball'; ball.data.materials.append(gold_m)
    curve=bpy.data.curves.new('One_Continuous_Golden_Thread_curve','CURVE'); curve.dimensions='3D'; curve.resolution_u=24; curve.bevel_depth=0.006; curve.bevel_resolution=3
    spline=curve.splines.new('BEZIER')
    pts=[(0.58,-0.02,1.58),(0.67,0.02,1.48),(0.42,0.14,1.20),(0.38,0.13,0.82),(0.40,0.09,0.45),(0.29,-0.16,0.19),(-0.05,-0.41,0.16),(-0.36,-0.04,0.18)]
    spline.bezier_points.add(len(pts)-1)
    for p,co in zip(spline.bezier_points,pts):
        p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    thread=bpy.data.objects.new('One_Continuous_Golden_Thread',curve); bpy.context.scene.collection.objects.link(thread); thread.data.materials.append(gold_m)
    write_json('gold_thread_path_audit.json',{'continuous_curve_only':True,'curve_object_name':thread.name,'point_count':len(pts),'gold_ball_object_name':ball.name,'status':'ENGINEERING_PLACED_NOT_ART_APPROVED'})
    _save('gold_thread_integrated.blend')

def refine():
    src=OUT/'gold_thread_integrated.blend'
    if not src.exists():
        raise RuntimeError('GOLD_STAGE_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    log=[]
    for deg in C['refinement']['target_views']:
        log.append({'angle_deg':deg,'status':'PENDING_VISUAL_REVIEW','regions':['silhouette','arm_contour','hand_ball_contact','thread_depth']})
    write_json('per_view_deviation_log.json',{'views':log,'rollback_on_degradation':C['refinement']['rollback_on_degradation']})
    _save('multiview_refined.blend')

def render():
    src=OUT/'multiview_refined.blend'
    for fallback in ['gold_thread_integrated.blend','pose_refined.blend','V88_base_loaded.blend']:
        if not src.exists():
            src=OUT/fallback
    if not src.exists():
        raise RuntimeError('NO_SCENE_FOR_RENDER')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    all_dir=OUT/'render_24'; key_dir=OUT/'render_key'; all_dir.mkdir(exist_ok=True); key_dir.mkdir(exist_ok=True)
    for entry in camera_table():
        set_camera(entry['angle_deg'])
        bpy.context.scene.render.filepath=str(all_dir/(entry['view_id']+'.png'))
        bpy.ops.render.render(write_still=True)
    for deg in C['camera']['key_angles_deg']:
        set_camera(deg)
        bpy.context.scene.render.filepath=str(key_dir/(f'VIEW_{deg:03d}.png'))
        bpy.ops.render.render(write_still=True)
    write_json('render_audit.json',{'render24_count':len(list(all_dir.glob('VIEW_*.png'))),'key_count':len(list(key_dir.glob('VIEW_*.png'))),'same_camera_intrinsics':True})

def export_glb():
    src=OUT/'multiview_refined.blend'
    if not src.exists():
        raise RuntimeError('REFINED_BLEND_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    meshes=_visible_meshes()
    if not meshes:
        raise RuntimeError('NO_MESHES_TO_EXPORT')
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    dest=OUT/C['export']['glb_name']
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_apply=True)
    write_json('export_audit.json',{'glb':dest.name,'mesh_count':len(meshes),'thread_present':('One_Continuous_Golden_Thread' in bpy.data.objects),'ball_present':('Ariadne_Gold_Ball' in bpy.data.objects)})

def reimport():
    src=OUT/C['export']['glb_name']
    if not src.exists():
        raise RuntimeError('EXPORTED_GLB_MISSING')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _import(src)
    meshes=[x for x in bpy.context.scene.objects if x.type=='MESH']
    names=[x.name for x in bpy.context.scene.objects]
    errors=[]
    if not meshes: errors.append('EMPTY_MESH_IMPORT')
    if 'Ariadne_Gold_Ball' not in names: errors.append('BALL_NOT_REIMPORTED')
    if not any('Thread' in n for n in names): errors.append('THREAD_NOT_REIMPORTED')
    write_json('reimport_validation.json',{'passed':not errors,'mesh_count':len(meshes),'object_names_sample':names[:20],'errors':errors})
    if errors:
        raise RuntimeError(';'.join(errors))

def main():
    cmds={'preflight':preflight,'load_base':load_base_scene,'pose':pose,'gold':gold,'refine':refine,'render':render,'export':export_glb,'reimport':reimport}
    if '--' not in sys.argv or len(sys.argv)<=sys.argv.index('--')+1:
        raise RuntimeError('USAGE: blender -b --python src/blender_v88.py -- [preflight|load_base|pose|gold|refine|render|export|reimport]')
    cmd=sys.argv[sys.argv.index('--')+1]
    if cmd not in cmds:
        raise RuntimeError('UNKNOWN_COMMAND:'+cmd)
    cmds[cmd]()

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        print('STAGE FAILED', e)
        traceback.print_exc()
        sys.exit(2)
