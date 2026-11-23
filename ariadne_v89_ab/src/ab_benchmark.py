#!/usr/bin/env python3
"""Repeatable, evidence-labeled A/B audit of Ariadne V88 vs V89 design gates.

Run from any working directory: python src/ab_benchmark.py
A = immutable V88 baseline; B = proposed V89 safety/geometry workflow.
Tests a real V87 GLB and 24 independent historical art frames. This is NOT
24-angle artistic evaluation nor a new posed Blender GLB.
"""
from __future__ import annotations
import csv
import hashlib
import json
import struct
import math
import pathlib
from collections import Counter
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REF = ROOT / 'references'
REP = ROOT / 'report'
REP.mkdir(exist_ok=True)
BASE = yaml.safe_load((ROOT/'baseline'/'V88_0_MASTER.yaml').read_text(encoding='utf8'))
BETTER = yaml.safe_load((ROOT/'NEMA_Ariadne_V89_AB_Optimized_Master.yaml').read_text(encoding='utf8'))
A_SOURCE = (ROOT/'baseline'/'blender_v88.py').read_text(encoding='utf8')


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_glb():
    path = REF/'Ariadne_V87_DesignFirst_Engineering_NOT_ART.glb'
    data=path.read_bytes()
    assert data[:4]==b'glTF' and struct.unpack_from('<I',data,4)[0]==2
    assert struct.unpack_from('<I',data,8)[0]==len(data)
    n=struct.unpack_from('<I',data,12)[0]
    assert data[16:20]==b'JSON'
    gltf=json.loads(data[20:20+n])
    scene=trimesh.load(path,force='scene',process=False)
    body=next((geo for name,geo in scene.geometry.items() if 'MakeHuman' in name),None)
    if body is None: raise RuntimeError('MakeHuman body mesh not found; refuse proxy substitution')
    xyz=body.vertices
    # glTF Y-up -> Blender-style Z-up. Verified against bounds in provenance.
    zup=np.column_stack((xyz[:,0],-xyz[:,2],xyz[:,1]))
    return path,gltf,scene,body,zup


def asset_integrity():
    old=json.loads((REF/'anchor_manifest.json').read_text(encoding='utf8'))
    files=sorted((REF/'anchors24').glob('art_*.png'))
    actual={p.name:sha256(p) for p in files}
    records=old.get('anchors',[])
    mismatches=[]
    for a in records:
        filename=pathlib.Path(a['file']).name
        if actual.get(filename)!=a['sha256']:
            mismatches.append(filename)
    assert old.get('count')==24 and len(records)==24 and len(files)==24
    assert [int(p.stem.split('_')[1]) for p in files]==list(range(0,360,15))
    return {'found':len(files),'manifest_records':len(records),'distinct_sha256':len(set(actual.values())),
            'mismatches':mismatches,'all_hashes_match':not mismatches,
            'front_art_sha256':sha256(REF/'V20_Original_Front_Art_Reference.png'),
            'turnaround_sha256':sha256(REF/'V20_24Art_Turnaround.png')}


def closest_to_group(zup, center, mask):
    pts=zup[mask]
    if len(pts)==0: raise RuntimeError('Empty hand-region heuristic')
    return float(np.linalg.norm(pts-center,axis=1).min())


def ball_trial(zup):
    # NOT a palm landmark: right arm/wrist candidate based on spatial bounds only.
    hand=(zup[:,0] > .40)&(zup[:,2] > .90)&(zup[:,2] < 1.15)
    bodytree=cKDTree(zup)
    coords=zup[hand]
    assert len(coords)>50
    radius=0.095
    a=np.array((.58,-.02,1.58),dtype=float)  # literal V88 position in actual script
    a_gap=closest_to_group(zup,a,hand)-radius
    # Explore two independent parameters: attachment point + outward offset.
    # The trial only establishes *geometric surface proximity*, not palm direction.
    reps=coords[(coords[:,0]>.48)&(coords[:,2]>.95)&(coords[:,2]<1.07)]
    reps=reps[::max(1,len(reps)//180)]
    directions=np.array([(1,0,0),(.97,0,.24),(.85,-.16,.50),(.88,.15,.45),(.75,0,.66)],dtype=float)
    directions=directions/np.linalg.norm(directions,axis=1)[:,None]
    winners=[]
    for p in reps:
        for d in directions:
            for delta in (.0,.003,.006):
                q=p+d*(radius+delta)
                near,_=bodytree.query(q)
                gap=float(near-radius)
                # Surface proxy screening only. Reject center likely inside another body vertex cloud.
                if -.002 <= gap <= .018:
                    desired_z=(q[2]-np.median(coords[:,2]))
                    score=abs(gap-.004)+.002*max(0.0,-desired_z)
                    winners.append((score,q,gap))
    if not winners:raise RuntimeError('No candidate meeting coarse contact tolerance')
    winners.sort(key=lambda x:x[0])
    _,b,allbodygap=winners[0]
    b_hand_gap=closest_to_group(zup,b,hand)-radius
    return {'metric':'nearest hand-candidate vertex distance minus sphere radius (m)',
            'radius_m':radius,'hand_candidate_vertex_count':int(hand.sum()),
            'A_fixed_center_zup_m':[.58,-.02,1.58],
            'A_gap_to_hand_candidate_m':round(a_gap,6),
            'B_candidate_center_zup_m':[round(float(v),6) for v in b],
            'B_gap_to_hand_candidate_m':round(b_hand_gap,6),
            'B_gap_to_all_body_vertices_m':round(allbodygap,6),
            'B_proxy_contact_10mm':abs(b_hand_gap)<=.010,
            'B_palm_anatomy_pass':None,
            'B_joint_pose_pass':None,
            'limitations':['No semantic palm/finger vertex mapping',
                           'No posed/rigged body mesh',
                           'Vertex proximity is NOT exact mesh-triangle clearance',
                           'No 0/45/90 camera contact proof']}


def row(case, type_, A, B, finding, evidence, state):
    return {'id':case,'kind':type_,'A_v88':A,'B_v89':B,
            'finding':finding,'source':evidence,'test_state':state}


def run():
    path,gltf,scene,body,zup=load_glb()
    if 'POSE_ADJUSTMENT_REQUIRES_ARMATURE_OR_PREDEFINED_DEFORMATION_RIG' not in A_SOURCE:
        raise AssertionError('Baseline A script has changed, AB control invalid')
    if "for o in meshes:" not in A_SOURCE or "o.select_set(True)" not in A_SOURCE:
        raise AssertionError('Baseline export selection changed, AB control invalid')
    if BETTER['project']['baseline']['source_version']!='88.0':
        raise AssertionError('B baseline provenance does not match 88.0')
    if len(BETTER['pipeline'])<5:raise AssertionError('B pipeline truncated')
    art=asset_integrity(); ball=ball_trial(zup)
    if not art['all_hashes_match']: raise AssertionError('Recovered art no longer matches provenance')
    if not (ball['A_gap_to_hand_candidate_m']>.10 and ball['B_proxy_contact_10mm']):
        raise AssertionError('Expected A->B near-contact improvement not reproduced')
    no_rig=(len(gltf.get('skins',[]))==0)
    if not no_rig:raise AssertionError('Real baseline now has rig; rerun AB design')
    A_gates=set(BASE['hard_constraints'])
    B_gates=set(BETTER['hard_constraints'])
    required={
      'no_false_rig_assumption', 'do_not_fake_armature_from_mesh_name',
      'gold_ball_contact_after_pose_not_fixed_world_coordinates',
      'palm_finger_wrist_anatomy_required',
      'convert_gold_thread_curve_to_mesh_before_glb_export',
      'verify_reimported_glb_contains_one_continuous_thread_and_gold_ball',
      'every_angle_strictly_above_0_95_after_art_camera_registration',
      'source_2d_art_must_be_independent_of_3d_render',
      'fail_closed_if_any_art_gate_unverified',
      'preserve_pre_sculpted_garment_folds',
      'no_out_of_scope_garment_hair_rebuild'
    }
    assert required<=B_gates, 'Missing mandatory B hard gates: '+str(sorted(required-B_gates))
    contract=BETTER['execution_contract']
    assert contract['rig_route']['unrigged_mesh']=='P00_BIND_VALIDATED_ARMATURE_OR_EXPLICIT_POSE_DEFORMER'
    assert contract['rig_route']['unrigged_without_validated_binding']=='BLOCK_POSE'
    assert contract['glb_export']['curve_mesh_conversion_required'] is True
    assert contract['quality']['per_view_threshold_operator']=='>'
    assert contract['quality']['per_view_threshold']==0.95
    assert contract['quality']['view_count']==24
    assert contract['quality']['all_24_individually_required'] is True
    assert contract['release']['art_approved_on_AB_trial'] is False

    rows=[
      row('AB01','observed','NO_SKIN','NO_SKIN -> RIG_BIND_REQUIRED',
          'V88 pose() cannot execute on actual source; B explicitly routes to validated binding rather than claiming an edited pose',
          'glTF JSON skins count', 'PASS_ENGINEERING'),
      row('AB02','observed',round(ball['A_gap_to_hand_candidate_m'],6),round(ball['B_gap_to_hand_candidate_m'],6),
          'Ball surface-proximity candidate moves from floating to near-contact, but palm support remains unverified',
          'V87 GLB MakeHuman vertices; scipy cKDTree', 'PASS_PROXY_ONLY'),
      row('AB03','observed','MESH_ONLY_SELECT', 'CURVE_TO_MESH_AND_ROUNDTRIP_REQUIRED',
          'V88 selects only MESH objects during GLB export: thread remains CURVE and is omitted by selection; B prevents this',
          'V88 source: export_glb and gold', 'PASS_CODE_AUDIT'),
      row('AB04','observed','24_LABELS_NO_HASH_ASSERT','24_ANCHORS_SHA256_VERIFIED',
          'Actual independent 2D anchor bytes verified against historical manifest',
          'anchor_manifest.json and 24 PNG files', 'PASS_ASSET_INTEGRITY'),
      row('AB05','observed','24_PENDINGS_NO_LOSS','24_STRICT_PER_VIEW_LOSS_REQUIRED',
          'B does not count pending views as measured; requires camera-registered independent art',
          'V88 refine() vs V89 YAML execution_contract', 'PASS_POLICY_NOT_VISUAL'),
      row('AB06','observed','FIXED_3D_COORDINATES','GEOMETRY_DERIVED_AFTER_POSE',
          'B forbids committing unposed ball coordinates as final contact',
          'V88 gold() hardcoded sphere center vs V89 YAML', 'PASS_POLICY'),
      row('AB07','not_executed','NOT_RUN','NOT_RUN',
          'No Blender pose correction or actual B GLB has been rendered in this A/B trial',
          'No new output/GLB and no verified rig', 'BLOCKED_NOT_EXECUTED'),
      row('AB08','not_executed','NOT_MEASURED','NOT_MEASURED',
          '24 angles each >95% artistic similarity not proven for A or B; no comparative art superiority claimed',
          'Independent art and actual camera registration missing', 'BLOCKED_ART_QA'),
      row('AB09','not_executed','NOT_MEASURED','NOT_MEASURED',
          'No signed palm/finger/contact landmarks; surface proximity cannot pass anatomical support test',
          '256 registered landmarks not supplied for this model', 'BLOCKED_ANATOMY'),
      row('AB10','policy','UNSPECIFIED','NO_SCOPE_EXPANSION',
          'B preserves garment and hair geometry unless explicitly affected by validated pose binding',
          'V89 hard_rules and scope_lock', 'PASS_POLICY'),
    ]
    summary={
      'experiment':'V88 A vs V89 B real-source engineering A/B',
      'scope':'YAML optimization with real input geometry measurements and executable policy gates, NOT a sculpture A/B render',
      'baseline_source_sha256':sha256(ROOT/'baseline/V88_0_MASTER.yaml'),
      'baseline_script_sha256':sha256(ROOT/'baseline/blender_v88.py'),
      'input_glb_sha256':sha256(path),
      'input_glb_bytes':path.stat().st_size,
      'input_glb_meshes':len(scene.geometry),
      'body_vertices':len(zup),'body_faces':len(body.faces),
      'gltf_skins':len(gltf.get('skins',[])),'gltf_animations':len(gltf.get('animations',[])),
      'source_axis':'glTF Y-up; explicitly transformed X,-Z,Y to Blender Z-up for geometry test',
      'anchor_evidence':art,
      'ball_surface_proxy':ball,
      'cases':rows,
      'engineering_ab_conclusion':'B recommended for safer, executable future model pipeline and coarse ball-placement initialization',
      'artistic_quality_conclusion':'NO_WINNER_MEASURED. Both A and B unverified; B prototype proximity cannot pass anatomical and 24-view art gates.',
      'new_GLb_produced':False,
      'blender_pose_executed':False,
      'release_status':'BLOCKED_ART_AND_RIG',
    }
    (REP/'AB_Results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with (REP/'AB_Cases.csv').open('w',encoding='utf8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=['id','kind','A_v88','B_v89','finding','source','test_state'])
        writer.writeheader();writer.writerows(rows)
    return summary


if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
