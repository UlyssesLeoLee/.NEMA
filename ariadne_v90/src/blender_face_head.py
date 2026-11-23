#!/usr/bin/env python3
"""V90 real-Blender face-lock then head-angle transfer, strict no fake evidence.

Use:
 blender -b approved_face_rig.blend --python src/blender_face_head.py -- face_lock
 blender -b output/face_canonical_locked.blend --python src/blender_face_head.py -- head_turn

Required registered inputs: config/face_evidence_APPROVED.json,
config/head_pose_APPROVED.json (see EXAMPLE templates).
A V87/89 unrigged GLB does NOT satisfy these; no unverified body warping.
"""
from pathlib import Path
import sys, json, math, hashlib, traceback
import bpy
import numpy as np
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)


def req(path):
    p=ROOT/path
    if not p.is_file():raise RuntimeError('MANDATORY_APPROVED_INPUT_MISSING:'+str(path))
    return p


def save_json(name, data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def validate_face_evidence():
    p=req('config/face_evidence_APPROVED.json')
    m=json.loads(p.read_text('utf-8'))
    art=req('assets/V20_Original_Front_Art_Reference.png')
    if m.get('source_art_sha256')!=hashlib.sha256(art.read_bytes()).hexdigest():
        raise RuntimeError('SOURCE_2D_ART_SHA256_MISMATCH')
    if m.get('independent_art') is not True or m.get('registered_neutral_front') is not True:
        raise RuntimeError('FRONT_ART_NEUTRAL_CAMERA_REGISTRATION_NOT_VERIFIED')
    if m.get('expression_independently_approved') is not True:
        raise RuntimeError('FACIAL_EXPRESSION_2D_NOT_APPROVED')
    points=m.get('landmarks',[])
    if len(points)<24:raise RuntimeError('LESS_THAN_24_REAL_FACE_LANDMARKS')
    ids=[int(x['vertex_id']) for x in points]
    if len(ids)!=len(set(ids)):raise RuntimeError('DUPLICATE_FACE_VERTEX_BINDING')
    regions=set()
    for x in points:
        if x.get('confidence',0)<.5 or x.get('confidence',0)>1:
            raise RuntimeError('FACE_LANDMARK_CONFIDENCE_INVALID')
        if x.get('region') not in ('eye','brow','nose','lips','jaw','cheek','chin','ear'):
            raise RuntimeError('FACE_LANDMARK_SEMANTIC_INVALID')
        uv=x.get('target_uv_bottom_left')
        if not isinstance(uv,list) or len(uv)!=2 or not all(0<=v<=1 for v in uv):
            raise RuntimeError('INVALID_CAMERA_REGISTERED_UV')
        regions.add(x['region'])
    if not {'eye','brow','nose','lips','jaw'}.issubset(regions):
        raise RuntimeError('MISSING_LIKENESS_OR_EXPRESSION_REGION')
    if len(m.get('shape_key_names',[]))<5:
        raise RuntimeError('INSUFFICIENT_3D_FACE_MORPH_BASIS')
    return m


def evaluated_landmark_pixels(obj, vertex_ids, camera):
    dg=bpy.context.evaluated_depsgraph_get()
    ev=obj.evaluated_get(dg)
    mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
    try:
        if len(mesh.vertices)!=len(obj.data.vertices):
            raise RuntimeError('FACE_VERTEX_IDS_LOST_BY_TOPOLOGY_CHANGING_MODIFIER')
        out=[]
        for i in vertex_ids:
            co=obj.matrix_world@mesh.vertices[i].co
            p=world_to_camera_view(bpy.context.scene,camera,co)
            if p.z<=0:raise RuntimeError('FACE_LANDMARK_BEHIND_CAMERA')
            out.append((p.x,p.y))
        return np.array(out,float)
    finally:
        ev.to_mesh_clear()


def fit_front():
    m=validate_face_evidence()
    obj=bpy.data.objects.get(m['face_mesh_object'])
    if obj is None or obj.type!='MESH':raise RuntimeError('REGISTERED_FACE_MESH_MISSING')
    cam=bpy.data.objects.get(m['registered_front_camera'])
    if cam is None or cam.type!='CAMERA':raise RuntimeError('REGISTERED_FRONT_CAMERA_MISSING')
    if bpy.context.scene.camera!=cam:bpy.context.scene.camera=cam
    blocks=obj.data.shape_keys.key_blocks if obj.data.shape_keys else None
    keys=m['shape_key_names']
    identity_keys=m.get('identity_shape_key_names',[])
    expression_keys=m.get('expression_shape_key_names',[])
    if blocks is None or any(k not in blocks for k in keys):
        raise RuntimeError('REAL_ANATOMICAL_FACE_SHAPE_KEYS_NOT_AVAILABLE')
    if (len(identity_keys)<3 or len(expression_keys)<2 or
            set(identity_keys)&set(expression_keys) or set(keys)!=(set(identity_keys)|set(expression_keys))):
        raise RuntimeError('IDENTITY_AND_EXPRESSION_MORPH_SEPARATION_REQUIRED')
    if any(mod.type=='ARMATURE' for mod in obj.modifiers):
        if m.get('neutral_head_pose_approved') is not True:
            raise RuntimeError('NEUTRAL_HEAD_POSE_NOT_LOCKED')
    pts=m['landmarks'];vids=[int(p['vertex_id']) for p in pts]
    if min(vids)<0 or max(vids)>=len(obj.data.vertices):
        raise RuntimeError('FACE_LANDMARK_INVALID_MESH_VERTEX_ID')
    target=np.array([p['target_uv_bottom_left'] for p in pts],float)
    conf=np.array([float(p['confidence']) for p in pts],float)
    region=np.array([p['region'] for p in pts])
    original={k:float(blocks[k].value) for k in keys}
    all_phases=[]
    def solve_phase(stage, phase_keys, allowed_regions):
        current=np.array([blocks[k].value for k in phase_keys])
        filt=np.array([r in allowed_regions for r in region])
        if filt.sum()<10:
            raise RuntimeError('FACE_2D_REGION_ANNOTATION_INSUFFICIENT_'+stage)
        ww=np.where(filt,conf,0.)
        def setvec(p):
            for k,v in zip(phase_keys,p):blocks[k].value=float(v)
            bpy.context.view_layer.update()
        def project(p):
            setvec(p)
            return evaluated_landmark_pixels(obj,vids,cam)
        def loss(p):
            dif=project(p)-target
            return float((ww[:,None]*dif**2).sum()/ww.sum() +
                         1e-5*np.sum((p-current)**2))
        vec=current.copy(); start=loss(vec);trace=[]
        for it in range(1,31):
            src=project(vec);err=(target-src).reshape(-1)
            J=np.zeros((len(err),len(phase_keys)))
            for j,k in enumerate(phase_keys):
                pv=vec.copy();pv[j]=min(.9999,pv[j]+1e-3)
                if pv[j]==vec[j]:pv[j]=max(.0001,pv[j]-1e-3)
                J[:,j]=((project(pv)-src)/(pv[j]-vec[j])).reshape(-1)
            W=np.repeat(np.sqrt(ww),2)
            jw=J*W[:,None]
            step=np.linalg.solve(jw.T@jw+1e-4*np.eye(len(phase_keys)),jw.T@(err*W))
            step=np.clip(step,-.12,.12)
            old=loss(vec);accepted=False
            for shrink in (1.,.5,.25,.125):
                candidate=np.clip(vec+shrink*step,0,1)
                if loss(candidate)<old-1e-10:
                    vec=candidate;accepted=True;break
            trace.append({'round':it,'loss':float(loss(vec)),'accepted':accepted})
            if not accepted or old-loss(vec)<1e-9:break
        end=loss(vec);setvec(vec)
        if not end<start-1e-10:
            raise RuntimeError('NO_ACTUAL_3D_FACE_IMPROVEMENT_'+stage)
        all_phases.append({'stage':stage,'keys':phase_keys,'start_loss':start,
                           'end_loss':end,'trace':trace,'improved':end<start})
        return end
    # Explicit priority: restore identity before expression. Identity keys stay frozen in pass 2.
    solve_phase('F01_IDENTITY',identity_keys,{'eye','nose','jaw','cheek','chin'})
    locked_identity={k:blocks[k].value for k in identity_keys}
    solve_phase('F02_EXPRESSION',expression_keys,{'eye','brow','lips'})
    if any(abs(blocks[k].value-v)>1e-8 for k,v in locked_identity.items()):
        raise RuntimeError('IDENTITY_SHAPE_CHANGED_DURING_EXPRESSION_LOOP')
    final_weights={k:float(blocks[k].value) for k in keys}
    passed=m.get('human_review_2d_loop_approved') is True
    proof={'status':'FACE_LOCKED' if passed else 'FACE_LOOP_ART_REVIEW_REQUIRED',
           'source_art_sha256':m['source_art_sha256'],
           'phases':all_phases,'shape_key_weights':final_weights,
           'neutral_face_geometry_lock':passed,'source_independent_2d':True,
           'actual_blender_2d_optimization':True,
           'identity_before_expression_enforced':True}
    save_json('face2d_loop_execution.json',proof)
    if not passed:raise RuntimeError('FACE_2D_ART_APPROVAL_REQUIRED_AFTER_LOOP')
    bpy.context.scene.render.filepath=str(OUT/'face_canonical_actual_Blender.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'face_canonical_locked.blend'))


def head_turn():
    evidence=req('output/face2d_loop_execution.json')
    face=json.loads(evidence.read_text())
    if face.get('status')!='FACE_LOCKED':raise RuntimeError('CANONICAL_FACE_NOT_APPROVED')
    manifest=json.loads(req('config/head_pose_APPROVED.json').read_text())
    if manifest.get('derived_from_independent_24_art') is not True or manifest.get('neck_rotation_approved') is not True:
        raise RuntimeError('HEAD_POSE_ANGLE_NOT_INDEPENDENTLY_APPROVED')
    arm=bpy.data.objects.get(manifest['rig_object'])
    if arm is None or arm.type!='ARMATURE':raise RuntimeError('HEAD_NECK_RIG_NOT_PRESENT')
    bone=arm.pose.bones.get(manifest['neck_bone'])
    if bone is None:raise RuntimeError('NECK_BONE_NOT_PRESENT')
    if not manifest.get('hair_and_headwear_follow_head'):raise RuntimeError('HAIR_TIARA_TRANSFER_NOT_VERIFIED')
    degrees=manifest['neck_local_euler_deg']
    if len(degrees)!=3 or any(abs(v)>30 for v in degrees):raise RuntimeError('HEAD_ROTATION_OUT_OF_APPROVED_BOUNDS')
    # Bone rotation only; no image rotation, face mesh resculpt, or per-camera head cheating.
    m=validate_face_evidence()
    mesh=bpy.data.objects.get(m['face_mesh_object'])
    vids=[int(v['vertex_id']) for v in m['landmarks']]
    def world_landmarks():
        deps=bpy.context.evaluated_depsgraph_get()
        ev=mesh.evaluated_get(deps)
        mm=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
        try:
            if len(mm.vertices)!=len(mesh.data.vertices):
                raise RuntimeError('HEAD_ANGLE_TOPOLOGY_CORRESPONDENCE_LOST')
            return np.array([list(mesh.matrix_world@mm.vertices[i].co) for i in vids])
        finally:
            ev.to_mesh_clear()
    before_pts=world_landmarks()
    bone.rotation_mode='QUATERNION'
    from mathutils import Quaternion
    euler=Euler(tuple(math.radians(float(v)) for v in degrees),'XYZ')
    bone.rotation_quaternion=euler.to_quaternion()
    bpy.context.view_layer.update()
    after_pts=world_landmarks()
    pairs=[(i,j) for i in range(min(len(vids),24)) for j in range(i+1,min(len(vids),24))]
    if not pairs:raise RuntimeError('INSUFFICIENT_FACE_RIGIDITY_EVIDENCE')
    drift=max(abs(float(np.linalg.norm(after_pts[i]-after_pts[j]) - np.linalg.norm(before_pts[i]-before_pts[j]))) for i,j in pairs)
    # Reject neck skinning artifacts that alter the face itself. 0.75 mm is strict.
    if drift>0.00075:raise RuntimeError(f'FACE_RIGIDITY_DISTORTION_AFTER_NECK_TURN:{drift:.6f}')
    # Shape key values must remain invariant after head posing.
    keys=m['shape_key_names'];blocks=mesh.data.shape_keys.key_blocks
    for k,v in face['shape_key_weights'].items():
        if abs(blocks[k].value-v)>1e-7:raise RuntimeError('FACE_EXPRESSION_CHANGED_DURING_HEAD_TURN')
    save_json('head_angle_transfer.json',{'status':'HEAD_ANGLE_APPLIED_NOT_24VIEW_APPROVED',
              'angle_local_xyz_deg':degrees,'source':'head_pose_APPROVED.json',
              'face_shape_key_weights_preserved':True,
              'max_face_pair_distance_drift_m':drift,
              'real_joint_rotation_applied':True,
              'mandatory_followups':['verify facial pairwise 3D distance and normals',
                                     '24-angle render comparison and face expression approval']})
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'head_angle_applied_NOT_FINAL.blend'))


def main():
    if '--' not in sys.argv:raise RuntimeError('USAGE blender -b --python src/blender_face_head.py -- face_lock|head_turn')
    i=sys.argv.index('--')
    cmd=sys.argv[i+1] if i+1<len(sys.argv) else ''
    if cmd=='face_lock': fit_front()
    elif cmd=='head_turn':head_turn()
    else:raise RuntimeError('UNKNOWN_STAGE')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('STAGE_FAILED',str(e));traceback.print_exc();sys.exit(2)
