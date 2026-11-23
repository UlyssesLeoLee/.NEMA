#!/usr/bin/env python3
"""Run reproducible geometry subset of V89 A/B on GitHub, with real V87 GLB.
Only geometry and pose capability, NOT artistic 24-view A/B.
"""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ab_benchmark import load_glb, ball_trial, sha256
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report';OUT.mkdir(exist_ok=True)
path,gltf,scene,body,zup=load_glb()
sha=sha256(path)
expected='4e9eb8ca64891ed63aae2a7a32297bf60f9b757f9c1873a7d67480827d11c948'
if sha!=expected:raise RuntimeError('V87_BASE_MESH_HASH_MISMATCH '+sha)
assert not gltf.get('skins')
ball=ball_trial(zup)
assert ball['A_gap_to_hand_candidate_m']>.30
assert abs(ball['B_gap_to_hand_candidate_m'])<.01
result={'status':'PASS_ENGINEERING_GEOMETRY_ONLY', 'source_sha256':sha,
        'unrigged':True,'body_vertices':len(zup),'A_gap_m':ball['A_gap_to_hand_candidate_m'],
        'B_gap_m':ball['B_gap_to_hand_candidate_m'],
        '24view_art_approved':False,'palm_and_finger_contact_approved':False,
        'real_blender_pose_executed':False,'final_glb_created':False}
(OUT/'GitHub_AB_Geometry_Proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
