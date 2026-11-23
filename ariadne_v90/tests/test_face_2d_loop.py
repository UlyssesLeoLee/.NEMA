import json,math,sys, hashlib
from pathlib import Path
import numpy as np
import pytest
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from face_2d_loop import fit_landmark_loop,pose_after_face_locked, rotate_yaw
from ab_synthetic import run,build_toy
from preflight import audit


def test_full_master_preserves_v89_contracts_and_three_focus():
    y=yaml.safe_load((ROOT/'NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml').read_text('utf8'))
    assert y['project']['version']=='90.0'
    assert y['project']['baseline']['source_version']=='89.0'
    assert {'P00','P01','P02','P03','P04','P05','F00','F01','F02','F03','F04'}=={e['id'] for e in y['pipeline']}
    assert y['execution_contract']['quality']['all_24_individually_required']
    assert y['execution_contract']['quality']['per_view_threshold_operator']=='>'
    assert 'full_garment_redesign' in y['scope']['out_of_scope']
    assert y['neck_pose_transfer_contract']['optimize_one_shared_quaternion_for_all_24_views']
    assert y['face_2d_loop_contract']['two_separate_phases']['L1_identity_geometry']['target']


def test_order_must_be_face_identity_then_expression_then_body_then_neck_pose_then_gold():
    y=yaml.safe_load((ROOT/'NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml').read_text('utf8'))
    ids=[e['id'] for e in y['pipeline']]
    assert ids==['P00','F00','F01','F02','P01','F03','F04','P02','P03','P04','P05']
    assert y['pipeline'][7]['depends_on']==['F04']


def test_v20_actual_source_hash_and_unapproved_crop():
    prov=json.loads((ROOT/'assets/face_reference_provenance.json').read_text('utf8'))
    assert hashlib.sha256((ROOT/'assets/V20_Original_Front_Art_Reference.png').read_bytes()).hexdigest()==prov['source_sha256']
    assert prov['crop_is_independent_art']
    assert not prov['has_registered_canonical_camera']
    assert not prov['expression_approval']


def test_real_gltf_preflight_detects_missing_rig_morphs_and_registration():
    rep=audit()
    assert rep['status']=='BLOCKED'
    assert rep['source_model_skins']==0
    assert rep['source_model_morph_targets']==0
    assert 'NO_REAL_NECK_HEAD_RIG_IN_V87_GLB' in rep['blockers']
    assert 'REGISTERED_CANONICAL_FACE_2D_ANNOTATION_MISSING' in rep['blockers']
    assert rep['actual_frontal_face_loop_executed'] is False


def test_numeric_ab_loop_has_real_accepted_updates_and_face_first_wins():
    r=run(write=False)
    assert r['B_beats_A_on_toy_data']
    assert 1 < r['B_fit_rounds']<=30
    assert r['B_final_fit_loss'] < r['B_first_fit_loss']*.05
    assert r['B_head_transfer']['face_geometry_unchanged']
    assert r['real_24_view_art_approval'] is False


def test_frontal_loop_rejects_head_yaw_in_production():
    v,d,regions,w=build_toy()
    target=v[:,[0,2]]
    with pytest.raises(ValueError,match='NEUTRAL'):
        fit_landmark_loop(v,d,target,w,regions,yaw_deg=20)


def test_frontal_loop_requires_actual_face_morph_basis():
    v,d,regions,w=build_toy()
    with pytest.raises(ValueError,match='MORPH_BASIS'):
        fit_landmark_loop(v,np.zeros((1,*v.shape)),v[:,[0,2]],w,regions)


def test_face_loop_requires_eye_brow_nose_lips_jaw_semantics():
    v,d,regions,w=build_toy()
    regions=['eye']*len(regions)
    with pytest.raises(ValueError,match='FIVE_CRITICAL'):
        fit_landmark_loop(v,d,v[:,[0,2]],w,regions)


def test_rejects_invalid_pixels_and_missing_landmarks():
    v,d,regions,w=build_toy()
    bad=np.full((len(v),2),float('nan'))
    with pytest.raises(ValueError,match='INVALID'):
        fit_landmark_loop(v,d,bad,w,regions)
    with pytest.raises(ValueError,match='REAL_REGISTERED'):
        fit_landmark_loop(v[:2],d[:,:2],bad[:2],w[:2],regions[:2])


def test_head_rotation_rigidity_random_angles():
    v,_,_,_=build_toy()
    for angle in (-30,-15,0,12,25,180,345):
        check=pose_after_face_locked(v,angle)
        assert check['face_geometry_unchanged']
        assert check['max_pairwise_distance_delta_m']<1e-12


def test_yaw_is_a_single_transform_not_mirror_or_stretch():
    v,_,_,_=build_toy()
    turned=rotate_yaw(v,20)
    assert not np.allclose(v,turned)
    d0=np.linalg.norm(v[0]-v[20]);d1=np.linalg.norm(turned[0]-turned[20])
    assert d1==pytest.approx(d0,abs=1e-12)


def test_art_release_remains_blocked_and_no_rig_fabrication():
    y=yaml.safe_load((ROOT/'NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml').read_text('utf8'))
    assert y['ab_result_interpretation']['V90_face_added']['final_art_approval']=='NOT_APPROVED'
    assert y['execution_contract']['rig_route']['unrigged_without_validated_binding']=='BLOCK_POSE'
    assert y['neck_pose_transfer_contract']['if_no_bone_rig']=='BLOCK_NOT_PROCEDURAL_WARP'


def test_blender_script_compiles_and_checks_shape_pose():
    import py_compile
    py_compile.compile(str(ROOT/'src/blender_face_head.py'),doraise=True)
    source=(ROOT/'src/blender_face_head.py').read_text('utf8')
    for condition in ['SOURCE_2D_ART_SHA256_MISMATCH','REAL_ANATOMICAL_FACE_SHAPE_KEYS_NOT_AVAILABLE','FACE_EXPRESSION_CHANGED_DURING_HEAD_TURN','FACE_RIGIDITY_DISTORTION_AFTER_NECK_TURN','NECK_BONE_NOT_PRESENT']:
        assert condition in source


def test_no_fake_approval_templates():
    a=json.loads((ROOT/'config/face_evidence_APPROVED.EXAMPLE.json').read_text('utf8'))
    b=json.loads((ROOT/'config/head_pose_APPROVED.EXAMPLE.json').read_text('utf8'))
    assert a['registered_neutral_front'] is False
    assert a['expression_independently_approved'] is False
    assert not a['landmarks']
    assert b['neck_rotation_approved'] is False
    assert b['neck_local_euler_deg']==[None,None,None]


def test_v20_24_real_reference_frames_have_matching_hashes():
    a=json.loads((ROOT/'assets/anchor_manifest24.json').read_text())
    assert a['count']==24 and len(a['anchors'])==24
    assert [p['angle_deg'] for p in a['anchors']]==list(range(0,360,15))
    for record in a['anchors']:
        p=ROOT/record['file']
        assert p.is_file()
        assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']
