#!/usr/bin/env python3
"""Blender 4.5 headless stages for V86.0 design-first garment pipeline.

Commands are fail-closed. Garment simulation is secondary-only and may not define
primary silhouette or major fold paths.
"""
import json
import math
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gates import check_design

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT/'config'/'production.json').read_text('utf8'))
OUT = ROOT/'output'; OUT.mkdir(exist_ok=True)


def require_asset(name):
    p=ROOT/C['reference_sources'][name]
    if not p.is_file(): raise RuntimeError(f'REQUIRED_ASSET_MISSING: {name}: {p}')
    return p


def write_json(filename,d):
    (OUT/filename).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', 'utf8')


def camera_table():
    from math import sin,cos,radians
    c=C['camera']; cx,cy,cz=c['target_xyz_m']; dist=c['distance_m']; out=[]
    for deg in c['view_angles_deg']:
        theta=radians(deg)
        out.append({'view_id':f'VIEW_{deg:03d}','angle_deg':deg,
                    'position':(cx+dist*sin(theta),cy-dist*cos(theta),cz),
                    'look_at':(cx,cy,cz)})
    return out


def set_camera(ang):
    cv=next(a for a in camera_table() if a['angle_deg']==ang)
    obj=bpy.data.objects.get('LOCKED_24_CAMERA')
    if not obj:
        data=bpy.data.cameras.new('LOCKED_24_CAMERA_DATA')
        obj=bpy.data.objects.new('LOCKED_24_CAMERA',data)
        bpy.context.scene.collection.objects.link(obj)
    cc=C['camera'];obj.data.type=cc['projection'];obj.data.lens=cc['focal_length_mm'];obj.data.sensor_width=cc['sensor_width_mm'];obj.data.sensor_fit=cc['sensor_fit']
    obj.location=cv['position']; direction=Vector(cv['look_at'])-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=obj
    scene=bpy.context.scene
    scene.render.resolution_x=cc['image_px'][0];scene.render.resolution_y=cc['image_px'][1]
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True


def import_mesh(path):
    before=set(bpy.data.objects)
    ext=path.suffix.lower()
    if ext=='.obj':bpy.ops.wm.obj_import(filepath=str(path),forward_axis='Y',up_axis='Z')
    elif ext in ['.glb','.gltf']:bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path))
    else:raise RuntimeError('UNSUPPORTED_GEOMETRY_FORMAT: '+ext)
    return [x for x in bpy.data.objects if x not in before and x.type=='MESH']


def connected_components(mesh):
    n=len(mesh.vertices); par=list(range(n))
    def get(a):
        while par[a]!=a:
            par[a]=par[par[a]];a=par[a]
        return a
    for edge in mesh.edges:
        a,b=edge.vertices;ra,rb=get(a),get(b)
        if ra!=rb:par[rb]=ra
    return len({get(a) for a in range(n)})


def obj_world_bounds(objects):
    pts=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    return (min(p.z for p in pts),max(p.z for p in pts))


def set_material(obj,name,color):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0)
    if obj.type=='MESH':obj.data.materials.clear();obj.data.materials.append(m)


def install_camera_lights():
    set_camera(0)
    scene=bpy.context.scene
    try:scene.render.engine=C['render']['engine']
    except Exception:scene.render.engine='BLENDER_EEVEE_NEXT'
    def area(name, pos, power, size):
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size
        obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj)
        obj.location=pos;obj.rotation_euler=(Vector([0,0,0.8])-obj.location).to_track_quat('-Z','Y').to_euler()
    area('KEY_SOFTBOX', (2,-3,4),500,4)
    area('FILL_SOFTBOX', (-2,-2,2.5),270,3)
    area('RIM_SOFTBOX', (1.5,2.0,2.4),600,2)
    scene.world.color=(0.27,0.27,0.27)


def graybox():
    raw=require_asset('cc0_body')
    provenance=require_asset('cc0_body_provenance')
    prov=json.loads(provenance.read_text('utf8'))
    if prov.get('license')!='CC0-1.0' or not prov.get('female_morph_target_applied'):
        raise RuntimeError('CC0_LICENSE_OR_ANATOMICAL_PRIOR_UNVERIFIED')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objects=import_mesh(raw)
    if not objects:raise RuntimeError('HUMAN_MESH_NOT_IMPORTABLE')
    for i,obj in enumerate(objects):
        obj.name=f'Human_CC0_{i:02d}'
        set_material(obj,'Ariadne_stone_gray',(0.58,0.58,0.58))
        mod=obj.modifiers.new('Collision','COLLISION')
        mod.settings.thickness_outer=0.009
    bpy.context.view_layer.update()
    low,high=obj_world_bounds(objects)
    if high-low<0.01: raise RuntimeError('INVALID_BODY_BOUNDING_BOX')
    sf=C['model_height_m']/(high-low)
    for obj in bpy.context.scene.objects:
        if obj.type=='ARMATURE':obj.scale*=sf
        elif obj.type=='MESH' and not obj.parent:obj.scale*=sf
    bpy.context.view_layer.update()
    low,_=obj_world_bounds(objects)
    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH','ARMATURE'} and not obj.parent:obj.location.z-=low
    bpy.context.view_layer.update()
    install_camera_lights()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'clean_graybox_scene.blend'))
    write_json('graybox_mesh_audit.json',{'imported_body_count':len(objects),'mesh_vertices':sum(len(x.data.vertices) for x in objects),
              'body_height_target_m':C['model_height_m'],'body_source':str(raw.relative_to(ROOT)),
              'rig_present':bool([x for x in bpy.data.objects if x.type=='ARMATURE']),
              'pose_approved':False,'art_ready':False})
    print('S00 graybox saved; NO art/pose approval claimed')


def _load_design_manifest():
    path = require_asset('garment_design_manifest')
    data = json.loads(path.read_text('utf8'))
    required_keys = ['design_principle','primary_regions_authored','no_free_drop_base','required_vertex_groups']
    missing=[k for k in required_keys if k not in data]
    if missing:
        raise RuntimeError('GARMENT_DESIGN_MANIFEST_INVALID: missing '+','.join(missing))
    if data['design_principle'] != 'designed_drapery_not_free_hanging_cloth':
        raise RuntimeError('GARMENT_DESIGN_PRINCIPLE_MISMATCH')
    if data['no_free_drop_base'] is not True:
        raise RuntimeError('GARMENT_PATTERN_NOT_DECLARED_DESIGN_FIRST')
    authored=set(data['primary_regions_authored'])
    required=set(C['garment_design']['required_primary_regions'])
    if not required.issubset(authored):
        raise RuntimeError('PRIMARY_GARMENT_REGIONS_NOT_AUTHORED')
    return data


def _validate_garment_object(cloth, manifest):
    count=connected_components(cloth.data)
    if count!=1:
        raise RuntimeError(f'CLOTH_NOT_CONNECTED: components={count}')
    vgs={vg.name for vg in cloth.vertex_groups}
    missing=[name for name in C['simulation']['required_vertex_groups'] if name not in vgs]
    if missing:
        raise RuntimeError('MISSING_REQUIRED_VERTEX_GROUPS: '+','.join(missing))
    if 'tube' in cloth.name.lower() or 'cylinder' in cloth.name.lower():
        raise RuntimeError('FORBIDDEN_FREE_DROP_BASE_NAME_DETECTED')
    if manifest.get('base_shape_hint') in {'tube','cylinder','sheet'}:
        raise RuntimeError('FORBIDDEN_BASE_SHAPE_DECLARED')
    # A declaration alone is not sculpted geometry. Require revision-stamped
    # Blender-native 3D mesh evidence, before the solver touches anything.
    if len(cloth.data.vertices) < 500 or len(cloth.data.polygons) < 400:
        raise RuntimeError('NOT_A_SUBSTANTIVE_SCULPTED_GARMENT_MESH')
    if cloth.get('primary_fold_sculpt_locked') is not True:
        raise RuntimeError('PRIMARY_FOLD_SCULPT_NOT_LOCKED_IN_BLENDER_ASSET')
    if cloth.get('design_revision') != manifest['pattern_revision']:
        raise RuntimeError('DESIGN_REVISION_MISMATCH_BETWEEN_MANIFEST_AND_MESH')
    # Every required semantic group must contain real geometry, not just a name.
    for group_name in C['simulation']['required_vertex_groups']:
        idx=cloth.vertex_groups[group_name].index
        hits=0
        for v in cloth.data.vertices:
            for g in v.groups:
                if g.group==idx and g.weight>0:
                    hits+=1; break
        if hits==0:
            raise RuntimeError(f'EMPTY_VERTEX_GROUP: {group_name}')
    # secondary sim zone must not be the whole garment; otherwise solver still defines everything
    idx=cloth.vertex_groups['SECONDARY_SIM_ZONE'].index
    in_zone=sum(1 for v in cloth.data.vertices for g in v.groups if g.group==idx and g.weight>0)
    if in_zone / len(cloth.data.vertices) > 0.75:
        raise RuntimeError('SECONDARY_SIM_ZONE_TOO_BROAD')
    if in_zone / len(cloth.data.vertices) < 0.01:
        raise RuntimeError('SECONDARY_SIM_ZONE_TOO_SMALL')
    # Blender cloth 'vertex_group_structural_stiffness' is NOT a fixed-position
    # constraint. The actual PIN group must cover all protected main-fold and
    # outer silhouette vertices at nearly full pin weight.
    protected_names = ('PRIMARY_OUTLINE_LOCK', 'PRIMARY_FOLD_LOCK',
                       'WAIST_GATHER', 'SHOULDER_DRAPE', 'CHEST_U_DRAPE',
                       'BACK_VEIL_ANCHOR')
    protected = set()
    for name in protected_names:
        protected.update(_group_indices(cloth, name))
    pin_id = cloth.vertex_groups['PIN'].index
    zone_id = cloth.vertex_groups['SECONDARY_SIM_ZONE'].index
    free_secondaries = 0
    for v in cloth.data.vertices:
        wg = {g.group:g.weight for g in v.groups}
        pin_weight = wg.get(pin_id,0.0)
        if v.index in protected and pin_weight < .98:
            raise RuntimeError(f'PRIMARY_DESIGN_VERTEX_NOT_ACTUALLY_PINNED:{v.index}')
        if wg.get(zone_id,0.0) > .1 and pin_weight < .5:
            free_secondaries += 1
    if free_secondaries < max(10,len(cloth.data.vertices)//100):
        raise RuntimeError('NO_FREE_SECONDARY_CLOTH_VERTICES')


def _snapshot_positions(obj):
    return [obj.matrix_world @ v.co.copy() for v in obj.data.vertices]


def _mean_displacement(before, after, indices):
    if not indices: return 0.0
    return sum((after[i]-before[i]).length for i in indices)/len(indices)


def _group_indices(obj, group_name):
    idx=obj.vertex_groups[group_name].index
    out=[]
    for v in obj.data.vertices:
        for g in v.groups:
            if g.group==idx and g.weight>0:
                out.append(v.index);break
    return out


def simulate():
    src=OUT/'clean_graybox_scene.blend'
    if not src.exists(): raise RuntimeError('S00_GRAYBOX_REQUIRED')
    gate = check_design()
    if gate['status'] != 'PASS':
        raise RuntimeError('DESIGN_INPUT_GATE_BLOCKED:'+';'.join(gate['reasons']))
    manifest=_load_design_manifest()
    pattern=require_asset('garment_pattern')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    if pattern.suffix.lower()!='.blend':
        raise RuntimeError('GARMENT_PATTERN_MUST_BE_BLEND_TO_PRESERVE_PIN_VERTEX_GROUP')
    with bpy.data.libraries.load(str(pattern), link=False) as (data_from,data_to):
        targets=[name for name in data_from.objects if name==manifest.get('garment_object_name','Garment_DesignFirst')]
        if len(targets)!=1:
            raise RuntimeError('DESIGN_FIRST_GARMENT_OBJECT_NOT_FOUND_IN_BLEND')
        data_to.objects=targets
    garments=[obj for obj in data_to.objects if obj and obj.type=='MESH']
    for garment in garments:bpy.context.scene.collection.objects.link(garment)
    if len(garments)!=1:raise RuntimeError('GARMENT_MUST_BE_SINGLE_CONNECTED_MESH_OBJECT')
    cloth=garments[0];cloth.name='Garment_DesignFirst'
    _validate_garment_object(cloth, manifest)
    body=[x for x in bpy.data.objects if x.name.startswith('Human_CC0_')]
    if not body:raise RuntimeError('PHYSICAL_BODY_COLLIDER_NOT_FOUND')
    pre_positions=_snapshot_positions(cloth)
    protected_outline=_group_indices(cloth,'PRIMARY_OUTLINE_LOCK')
    protected_folds=_group_indices(cloth,'PRIMARY_FOLD_LOCK')
    # Pin primary structure. Only secondary sim zone is allowed to relax substantially.
    m=cloth.modifiers.new('Controlled_Secondary_Cloth_Solver','CLOTH')
    m.settings.quality=C['simulation']['quality']
    m.settings.vertex_group_mass='PIN'
    m.settings.pin_stiffness = 45.0
    # The actual spatial lock is PIN; the separate structural/fold groups are
    # selection evidence and are evaluated geometrically after the simulation.
    m.collision_settings.use_collision=True
    m.collision_settings.distance_min=C['simulation']['collision_distance_m']
    m.collision_settings.use_self_collision=C['simulation']['self_collision']
    m.point_cache.frame_start=1;m.point_cache.frame_end=C['simulation']['frames'];m.point_cache.use_disk_cache=True
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=C['simulation']['frames']
    scene.frame_set(1)
    set_material(cloth,'Ariadne_garment_stone',(0.78,0.76,0.72))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cloth_simulation_working.blend'))
    bpy.ops.ptcache.bake_all(bake=True)
    scene.frame_set(C['simulation']['frames']);bpy.context.view_layer.update()
    baked=bool(m.point_cache.is_baked)
    evaluated=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
    new_mesh=bpy.data.meshes.new_from_object(evaluated)
    final=bpy.data.objects.new('Garment_Simulated_Verified',new_mesh)
    final.matrix_world=cloth.matrix_world.copy()
    bpy.context.scene.collection.objects.link(final)
    set_material(final,'Ariadne_garment_stone',(0.78,0.76,0.72))
    cloth.hide_render=True;cloth.hide_set(True)
    post_positions=_snapshot_positions(final)
    outline_drift=_mean_displacement(pre_positions, post_positions, protected_outline)
    fold_drift=_mean_displacement(pre_positions, post_positions, protected_folds)
    outline_max=max(((post_positions[i]-pre_positions[i]).length for i in protected_outline), default=0.)
    fold_max=max(((post_positions[i]-pre_positions[i]).length for i in protected_folds), default=0.)
    issues=[]
    if not baked:issues.append('CACHE_NOT_BAKED')
    if connected_components(new_mesh)!=1: issues.append('SOLVED_MESH_DISCONNECTED')
    if outline_drift > C['simulation']['max_primary_shape_drift_m']:
        issues.append(f'PRIMARY_OUTLINE_DRIFT_TOO_HIGH:{outline_drift:.6f}')
    if fold_drift > C['simulation']['max_primary_fold_drift_m']:
        issues.append(f'PRIMARY_FOLD_DRIFT_TOO_HIGH:{fold_drift:.6f}')
    if outline_max > C['simulation']['max_primary_shape_drift_m']:
        issues.append(f'PRIMARY_OUTLINE_LOCAL_DRIFT_TOO_HIGH:{outline_max:.6f}')
    if fold_max > C['simulation']['max_primary_fold_drift_m']:
        issues.append(f'PRIMARY_FOLD_LOCAL_DRIFT_TOO_HIGH:{fold_max:.6f}')
    write_json('protected_shape_drift.json',{
        'outline_mean_drift_m':outline_drift,
        'fold_mean_drift_m':fold_drift,
        'outline_max_drift_m':outline_max,
        'fold_max_drift_m':fold_max,
        'outline_limit_m':C['simulation']['max_primary_shape_drift_m'],
        'fold_limit_m':C['simulation']['max_primary_fold_drift_m'],
        'secondary_only_role':True,
        'status':'PASS' if not issues else 'FAIL'
    })
    write_json('cloth_solver_audit.json',{'real_bpy_modifier':True,'cache_baked':baked,
               'solver':'Blender built-in Cloth SECONDARY ONLY','blender_version':bpy.app.version_string,
               'topology_connected':connected_components(new_mesh)==1,
               'source_vertex_count':len(cloth.data.vertices),'solved_vertex_count':len(new_mesh.vertices),
               'self_collision_enabled':m.collision_settings.use_self_collision,
               'evaluated_at_frame':scene.frame_current,
               'outline_mean_drift_m':outline_drift,'fold_mean_drift_m':fold_drift,
               'issues':issues,'approval':'PHYSICS_TEST_ONLY_ART_NOT_APPROVED'})
    if issues:raise RuntimeError('; '.join(issues))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cloth_solved.blend'))
    for obj in bpy.context.selected_objects:obj.select_set(False)
    for obj in body+[final]:obj.select_set(True)
    bpy.context.view_layer.objects.active=final
    bpy.ops.export_scene.gltf(filepath=str(OUT/'V86_Controlled_Cloth_Engineering_Proof_Not_Art.glb'),export_format='GLB',use_selection=True)
    print('G04 controlled cloth solver engineering proof saved')


def render():
    src=OUT/'cloth_solved.blend'
    if not src.exists():raise RuntimeError('G04_DESIGN_FIRST_CLOTH_RESULT_REQUIRED')
    bpy.ops.wm.open_mainfile(filepath=str(src))
    # Engineering evidence only; this must never pretend to be reference art.
    bpy.context.scene.render.engine='BLENDER_WORKBENCH'
    target=OUT/'render_24';target.mkdir(parents=True,exist_ok=True)
    for entry in camera_table():
        set_camera(entry['angle_deg'])
        bpy.context.scene.render.filepath=str(target/(entry['view_id']+'.png'))
        bpy.ops.render.render(write_still=True)
        print('RENDERED',entry['view_id'])
    write_json('render_24_audit.json',{'count':len(list(target.glob('VIEW_*.png'))),
                                     'camera_table_source':'config/production.json',
                                     'same_intrinsics_for_all_views':True,'same_distance_for_all_views':True,
                                     'independent_art_available':(ROOT/C['reference_sources']['front_art']).is_file() and (ROOT/C['reference_sources']['turnaround']).is_file()})


def export_candidate():
    source=OUT/'art_sculpted_24views.blend'
    if not source.is_file():raise RuntimeError('ART_SCULPTED_SCENE_NOT_PROVIDED')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    objs=[x for x in bpy.data.objects if x.type=='MESH' and not x.hide_render]
    if not objs:raise RuntimeError('NO_FINISHED_MESHES')
    for x in bpy.context.selected_objects:x.select_set(False)
    for x in objs:x.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    dest=OUT/'Ariadne_Final_DesignFirst_Candidate.glb'
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_apply=True)
    print('Exported CANDIDATE (NOT CERTIFIED):',dest)


def reimport():
    src=OUT/'V86_Controlled_Cloth_Engineering_Proof_Not_Art.glb'
    if not src.exists():raise RuntimeError('ENGINEERING_GLB_MISSING')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(src))
    meshes=[x for x in bpy.context.scene.objects if x.type=='MESH']
    bad=[]
    if not meshes:bad.append('EMPTY_MESH_IMPORT')
    if any(len(x.data.polygons)==0 for x in meshes):bad.append('EMPTY_POLYGON_OBJECT')
    missing=[x.name for x in bpy.data.images if x.source=='FILE' and x.filepath and not x.packed_file and not Path(bpy.path.abspath(x.filepath)).is_file()]
    if missing:bad.append('MISSING_TEXTURE_IMAGES: '+','.join(missing))
    write_json('glb_reimport_audit.json',{'passed':not bad,'mesh_count':len(meshes),'polygon_count':sum(len(x.data.polygons) for x in meshes),
                                         'texture_missing':missing,'errors':bad,'blender_version':bpy.app.version_string})
    if bad:raise RuntimeError('; '.join(bad))


def main():
    if '--' not in sys.argv or len(sys.argv)<=sys.argv.index('--')+1:raise RuntimeError('USAGE: blender -b --python src/blender_build.py -- [graybox|simulate|render|export|reimport]')
    command=sys.argv[sys.argv.index('--')+1]
    actions={'graybox':graybox,'simulate':simulate,'render':render,'export':export_candidate,'reimport':reimport}
    if command not in actions:raise RuntimeError('UNKNOWN_COMMAND '+command)
    actions[command]()

if __name__=='__main__':
    try:main()
    except Exception as ex:
        print('STAGE FAILED:',ex)
        traceback.print_exc()
        sys.exit(2)
