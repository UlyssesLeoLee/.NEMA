#!/usr/bin/env python3
"""Read-only source & readiness preflight. PENDING is a valid outcome, never a pass."""
import json,hashlib,struct
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/V20_Original_Front_Art_Reference.png'

def gltf_json(p):
    blob=p.read_bytes()
    if blob[:4]!=b'glTF' or len(blob)<24:
        raise ValueError('INVALID_REAL_GLB')
    n=struct.unpack_from('<I',blob,12)[0]
    if blob[16:20]!=b'JSON':raise ValueError('GLTF_JSON_MISSING')
    return json.loads(blob[20:20+n])

def audit():
    master=yaml.safe_load((ROOT/'NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml').read_text('utf8'))
    a=json.loads((ROOT/'assets/face_reference_provenance.json').read_text('utf8'))
    actual_sha=hashlib.sha256(ART.read_bytes()).hexdigest()
    if a['source_sha256']!=actual_sha:
        raise ValueError('V20_SOURCE_SHA_MISMATCH')
    source=ROOT/'baseline/V89_source_V87_1.glb'
    model=gltf_json(source) if source.is_file() else None
    meshes=[] if model is None else model.get('meshes',[])
    targets=sum(len(p.get('targets',[])) for m in meshes for p in m.get('primitives',[]))
    skins=0 if model is None else len(model.get('skins',[]))
    real_face_evidence=(ROOT/'config/face_evidence_APPROVED.json').is_file()
    real_head_pose=(ROOT/'config/head_pose_APPROVED.json').is_file()
    blockers=[]
    if not real_face_evidence: blockers.append('REGISTERED_CANONICAL_FACE_2D_ANNOTATION_MISSING')
    if targets==0:blockers.append('NO_FACE_3D_MORPH_TARGETS_IN_V87_GLB')
    if skins==0:blockers.append('NO_REAL_NECK_HEAD_RIG_IN_V87_GLB')
    if not real_head_pose:blockers.append('HEAD_ANGLE_24VIEW_ART_APPROVAL_MISSING')
    if model is None:blockers.append('V87_GLB_NOT_AVAILABLE_FOR_SOURCE_CAPABILITY_AUDIT')
    report={
        'project_version':master['project']['version'],'art_source_sha256':actual_sha,
        'source_V20_art_verified':True,'source_model_present':model is not None,
        'source_model_skins':skins,'source_model_morph_targets':targets,
        'independent_art_is_neutral_front_automatically':False,
        'actual_frontal_face_loop_executed':False,'actual_head_angle_changed':False,
        'art_likeness_approved':False,'status':'BLOCKED' if blockers else 'READINESS_UNDER_REVIEW',
        'blockers':blockers,
        'note':'No placeholders are treated as art/geometry proof'
    }
    (ROOT/'report/V90_preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
if __name__=='__main__':
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
