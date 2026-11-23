#!/usr/bin/env python3
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
base=yaml.safe_load((ROOT/'baseline/V89_MASTER.yaml').read_text(encoding='utf8'))
p=base['project'];p['name']='NEMA_Ariadne_V90_Face2D_Loop_FrontLock_Then_NeckPose_FULL_Master';p['version']='90.0';p['baseline']={'source_version':'89.0','file':'baseline/V89_MASTER.yaml'}
p['objective']=(
    '在 V89 现有三项收敛任务之上，仅扩展面部和头部的必要执行顺序。'
    '先从独立 V20 原画校准正面长相与眼鼻口等局部表情，'
    '反复 2D 渲染/差异定位/形态修正/回滚，正面锁定后再将头通过颈部真实骨骼转向目标角度。'
    '服装大褶、发型、人体来源、金球金线不重新设计；随后全 24 角验收。'
)
p['output_contract']=[
 'V20_original_art_face_crop_NOT_APPROVED_REFERENCE.png',
 'F00_independent_face_landmark_annotation_and_camera_registration.json',
 'F01_F02_2D_front_facial_identity_expression_iteration_logs.json',
 'face_canonical_actual_Blender.png',
 'face_canonical_locked.blend',
 'face_geometry_expression_lock.json',
 'head_angle_applied_NOT_FINAL.blend',
 'neck_joint_head_angle_transfer_and_face_preservation.json',
 '24_view_face_expression_and_pose_regression.json'
] + p['output_contract']

scope=base['scope']
scope['in_scope']=['canonical_front_face_2D_iterative_likeness_reconstruction',
                    'front_expression_lock_then_neck_joint_head_angle_transfer',
                    'head_angle_24_view_regression'] + scope['in_scope']
scope['out_of_scope']=[x for x in scope['out_of_scope'] if x!='full_head_hair_redesign'] + ['full_hair_costume_redesign','per_view_head_rotation_cheating','face_replacement_by_single_texture','standalone_frontal_billboard_face']
scope['exception']=(scope.get('exception','')+ ' 可以在有证据和实际拓扑绑定的前提下修雕原有脸部网格；'
                         '不允许重置为默认 AI 人脸、重做发型或让头饰脱离头骨。')
new_rules=[
 'independent_V20_art_face_and_expression_evidence_before_face_sculpt',
 'V20_original_face_slightly_oblique_not_automatically_neutral_front',
 'require_camera_and_head_neutralization_registration_before_front_loop',
 'do_not_confuse_2D_generated_guide_with_independent_ground_truth',
 'face_identity_first_expression_second_after_identity_lock',
 '2D_loop_must_have_actual_render_measure_sculpt_rerender_and_rollback',
 'no_2D_face_texture_as_substitute_for_facial_sculpt_geometry',
 'face_sculpt_only_using_anatomical_morph_basis_or_verified_sculpt_delta',
 'face_2D_loop_needs_semantic_eyes_brows_nose_lips_jaw_visibility',
 'frontal_face_and_expression_approved_before_any_head_yaw_pitch_roll',
 'head_angle_via_true_neck_joint_after_facial_shape_lock',
 'head_turn_must_not_change_face_shape_key_weights_or_expression',
 'hair_tiara_veil_neck_and_face_must_follow_same_head_transform',
 'only_one_head_quaternion_for_all_24_renders_never_per_view_repose',
 'after_head_pose_check_3D_landmark_rigidity_no_collar_or_neck_tearing',
 'do_not_claim_95_percent_face_similarity_without_registered_real_2D_and_3D_evidence',
 'block_face_and_head_pose_if_missing_real_rig_or_facial_shape_keys'
]
base['hard_constraints']+=new_rules
ref=base['reference_assets']
ref['face_original_front_art']={
 'file':'assets/V20_Original_Front_Art_Reference.png',
 'raw_image_is_not_guaranteed_exact_canonical_neutral':True,
 'face_crop':'assets/V20_original_head_reference_crop.png',
 'crop_purpose':'evidence_visualization_only_not_a_new_user_approved_reference',
 'source_sha256_manifest':'assets/face_reference_provenance.json',
 'observed_visual_style':'idealized Greek marble female, subtle composed expression, gently open eyelids, neutral lips, sculpted nose/cheek/jaw',
 'source_2D_provenance':'prior user-authorized V20 original art',
 'forbidden':'AI-generated or 3D-rendered face used as independent target',
 'approval':'PENDING_CAMERA_REGISTRATION_AND_FACE_LANDMARK_ANNOTATION'
}
ref['facial_2D_semantic_annotations']={
 'status':'MISSING_NOT_ALLOWED_TO_INFER_FROM_FILENAME',
 'required_attributes':['semantic_region','source_image_uv','registered_neutral_front_uv','confidence','occlusion','paired_3D_vertex_id'],
 'required_regions':['left_eye','right_eye','eyebrows','nose_bridge','nose_tip','lips','mouth_corners','jawline','chin','cheekbones'],
 'minimum_points':24,
 'independent_2d_human_approval':True,
 'must_match_exact_source_sha256':True,
 'do_not_autofill_unknown_points':True
}

base['face_2d_loop_contract']={
 'core_principle':'FACE_IDENTITY_IN_2D_FIRST_THEN_EXPRESSION_THEN_HEAD_ANGLE',
 'two_separate_phases':{
  'L1_identity_geometry':{
   'target':'frontal facial bone structure and timeless likeness',
   'regions':['eye_spacing','eye_shape','nose_bridge_and_tip','cheekbone_projection','jawline','chin','facial_proportion'],
   'allowed_edits':['verified_anatomical_shape_keys','face_vertex_sculpt_deltas_registered_to_3D_IDs'],
   'disallowed':['camera_pose_to_hide_face_errors','2D_plane_with_face_texture','mirror_away_genuine_asymmetry'],
   'lock_when':['original_art_landmarks_registered','actual_frontal_Blender_render_checked','identity_shape_approved']
  },
  'L2_expression_geometry':{
   'target':'subtle original V20 composed expression; no invented smile or gaze change',
   'regions':['upper_and_lower_eyelids','brow_arch_left_right','lip_crease','mouth_corner_left_right','nasolabial_and_chin_tension','gaze_direction'],
   'allowed_edits':['approved_expression_shape_keys','localized_sculpt_delta_matching_independent_2d'],
   'disallowed':['over_exaggerated_smile','eyes_closed_when_reference_eyes_open','texture_only_lip_crease'],
   'lock_when':['expression_2d_art_approved','microexpression_visible_in_geometry','actual_same_camera_face_render_checked']
  }
 },
 'loop':{
  'max_iterations_each_phase':30,
  'must_run_in_real_Blender_on_real_3D_face':True,
  'process':['render_actual_neutral_front_same_camera','register_2D_art_to_render_geometry','measure_per_region_silhouette_and_landmarks','choose_worst_semantic_region','edit_3D_anatomical_basis_with_bounded_delta','rerender_same_camera','regression_check_3D_face_volume_and_other_angles','rollback_if_any_critical_region_degrades'],
  'objective':'weighted_robust_per_region_pixel_landmark_loss_plus_geometry_prior_plus_expression_prior',
  'normalization':'use_same_camera_intrinsics_extrinsics_and_registration_for_every_iteration',
  'early_stop_only_when':['region_metrics_plateau_with_art_minima_satisfied','human_identity_and_expression_signoff'],
  'if_no_improvement':'ROLLBACK_AND_LOG_NEXT_REGION_OR_BLOCK',
  'never_treat_max_iteration_count_as_success':True,
  'max_shape_key_step_per_iteration':0.12,
  'max_face_shape_coeff_in_unit_interval':1.0,
  'retain_approved_asymmetry':True,
  'do_not_use_mean_face_loss_to_hide_failed_eye_or_mouth':True
 },
 'art_quality_gate':{
  'front_identity_expressions_separately_approved':True,
  'reprojection_error_percentile_95_max_px':'MUST_BE_SET_FROM_CALIBRATED_SOURCE',
  'independent_v20_face_2d_source':True,
  'actual_face_model_render':True,
  'nose_lips_eyelids_true_geometry':True,
  'front_face_mesh_locked_before_head_turn':True,
  'status':'BLOCKED_PENDING_REAL_FACE_SCULPT_AND_HUMAN_APPROVAL'
 }
}
base['neck_pose_transfer_contract']={
 'after':['F00','F01','F02','P01_body_pose_without_head_angle'],
 'do_not_reopen_identity_shape_keys_after_head_pose':True,
 'rig_requirements':['true_neck_joint_and_head_joint','verified_head_and_face_skin_weights','headwear_hair_veil_follow_verified_transform','valid_neck_base_and_collar_overlap'],
 'if_no_bone_rig':'BLOCK_NOT_PROCEDURAL_WARP',
 'angles':['yaw','pitch','roll'],
 'angle_source':'24 independent V20 angles, actual camera registration and head vector evidence',
 'initial_angle_range_deg':{'yaw':[-25,25],'pitch':[-15,15],'roll':[-10,10]},
 'optimize_one_shared_quaternion_for_all_24_views':True,
 'head_angle_cannot_be_changed_between_camera_views':True,
 'checks':['facial_internal_3D_landmark_distances_preserved','nose_mouth_expression_constant','hair_circlet_follow_head','neck_below_jaw_no_tearing','eyes_nose_lips_2D_projection_consistent_in_24_views'],
 'must_reject':['per_frame_face_projection_2d_sticker','one_view_only_yaw_fix','hair_or_tiara_not_following','expression_changing_after_pose'],
 'report':['head_pose_joint_rotation.json','face_shape_lock_before_after.json','24_view_face_angle_regression.json']
}
base['execution_contract']['rig_route']['deformation_requirements']+=['head_neck_bones_and_face_shape_key_binding_are_real', 'face_identity_locked_before_head_angle_motion']
base['execution_contract']['quality']['face_likeness_and_expression_24views_required']=True
base['execution_contract']['release']['face_front_approved_before_head_rotation']=False
base['execution_contract']['release']['real_face_blender_loop_executed_in_this_revision']=False
base['execution_contract']['release']['head_rotation_done_in_this_revision']=False
base['execution_contract']['release']['head_pose_art_verified']=False

pipeline=base['pipeline']
face_steps=[
 {'id':'F00','name':'INDEPENDENT_V20_FACE_CANONICALIZATION_AND_2D_MARKUPS','depends_on':['P00'],
  'actions':['use_original_V20_pixels_and_sha256_do_not_generate_new_authoritative_face','register_original_head_yaw_and_camera_to_approved_neutral_front','annotate_eyes_brow_nose_lips_cheeks_chin_jaw_with_persistent_IDs','record_occlusion_confidence_nonuniform_expression_asymmetry','human_review_original_image_registered_face_axes'],
  'outputs':['F00_front_art_provenance.json','F00_face_landmark_map_2D3D.json','F00_neutral_front_camera.json'],
  'gate':['original_art_sha256_matches','real_camera_registration_approved','all_critical_semantic_face_regions_annotated','no_generated_2D_as_source']},
 {'id':'F01','name':'FRONTAL_LIKENESS_2D_LOOP_REAL_3D_FACIAL_SCULPT','depends_on':['F00'],
  'actions':['restore_eye_spacing_nose_bridge_zygomatic_jaw_chin_from_independent_art','render_neutral_frontal_face_from_same_anatomical_mesh','measure_registered_2D_projection_per_semantic_region','bounded_sculpt_against_real_3D_morph_basis_and_vertex_IDs','repeat_2D_difference_feedback_and_reject_regressions','lock_identity_geometry_when_artist_approves'],
  'outputs':['F01_frontal_face_2D_loop_actual_renders','F01_2D_identity_loss_trace.json','F01_facial_identity_shape_locked.blend'],
  'gate':['real_anatomical_face_morph_or_verified_sculpt_basis_exists','identity_2D_loop_produces_actual_3D_geometry_changes','identity_shape_passes_artist_front_gate']},
 {'id':'F02','name':'EXPRESSION_2D_LOOP_WITH_FACE_LOCK','depends_on':['F01'],
  'actions':['capture_original_V20_calm_expression_not_generic_default','measure_left_right_eyelids_brows_lip_tension_mouth_corners_and_gaze','apply_independent_verified_expression_morphs_without_disturbing_identity','render_and_compare_same_front_camera_after_each_update','reject_over_smile_eyelid_collapse_and_random_asymmetry','approve_and_lock_expression_and_face_shape_keys'],
  'outputs':['F02_expression_2D_loop_actual_renders','F02_region_expression_loss_trace.json','face_canonical_locked.blend','face_geometry_expression_lock.json'],
  'gate':['expression_sources_independent','expression_geometry_not_texture_only','identity_geometry_preserved','front_face_and_expression_approved']},
]
# Set P01 dependent on approved face and rig, but body pose MUST not change head geometry or angle.
for x in pipeline:
    if x['id']=='P01':
        x['depends_on']=['F02']
        x['name']='GLOBAL_K_BODY_POSE_HEAD_ANGLE_HELD_CANONICAL'
        x['method'].append('keep_face_local_shape_and_expression_locked_until_F03')
        x['gate'].append('canonical_face_shape_not_changed_by_body_pose')
    if x['id']=='P02':x['depends_on']=['F04']
    if x['id']=='P04':
        x['method'].append('recompute_all_24_face_identity_expression_and_head_angle_projections_from_locked_one_mesh')
        x['gate'].append('face_identity_and_expression_verified_after_head_pose_on_all_views')

head_steps=[
 {'id':'F03','name':'NECK_JOINT_HEAD_ANGLE_TRANSFER_AFTER_FRONTAL_FACE_LOCK','depends_on':['F02','P01'],
  'actions':['load_frozen_canonical_face_shape_and_expression','estimate_neck_rotation_from_independent_24_art_and_3D_head_vector','rotate_true_neck_head_joint_about_anatomically_correct_center','propagate_same_joint_to_hair_circlet_veil_attached_to_head','check_stable_face_local_3D_pairs_and_shape_key_weights','do_not_warp_head_pixels_in_2D_or_resculpt_face'],
  'outputs':['head_angle_applied_NOT_FINAL.blend','neck_joint_head_angle_transfer_and_face_preservation.json'],
  'gate':['actual_valid_neck_joint_deformation','front_face_3D_shape_invariant','one_head_quaternion_only','hair_headwear_follow_head_and_neck_no_tearing']},
 {'id':'F04','name':'FACE_AND_EXPRESSION_24VIEW_REGRESSION_AFTER_HEAD_ANGLE','depends_on':['F03'],
  'actions':['render_face_crop_from_each_of_24_locked_cameras','align_24_independent_art_face_regions_to_same_physical_model','measure_features_occlusion_gaze_eyelids_jaw_face_silhouette_per_view','rollback_head_angle_if_front_likeness_or_other_view_degrades','freeze_head_pose_only_when_all_visible_semantic_regions_pass'],
  'outputs':['face_head_24view_same_mesh_render_sheet.png','24_view_face_angle_regression.json','head_face_angle_locked.blend'],
  'gate':['face_identity_and_expression_stable_across_available_angles','no_camera_specific_face_rotation','all_24_registered_art_evidence_or_explicit_BLOCKED','no_quality_claim_if_gates_missing']},
]
ids={x['id'] for x in pipeline}
if ids!={'P00','P01','P02','P03','P04','P05'}:
    raise RuntimeError('UNEXPECTED_BASELINE_PIPELINE_CHANGE')
new_pipeline=[pipeline[0],*face_steps,pipeline[1],*head_steps,*pipeline[2:]]
base['pipeline']=new_pipeline
base['ab_experiment']['V90_head_face_ab_extension']={
 'A':'face_2D_fit_while_head_is_yawed_and_edit_expression_implicitly',
 'B':'canonical_registered_front_face_identity_then_expression_lock_then_one_shared_neck_rotation',
 'same_2D_reference_and_semantic_points':True,
 'measured_numeric_test':'report/face2d_AB_numeric.json',
 'synthetic_numeric_test_is_not_real_v20_art':True,
 'head_pose_geometry_invariance_verified_only_in_synthetic_test':True,
 'no_real_world_art_winner_before_actual_blender_renders':True
}
base['ab_result_interpretation']['V90_face_added']={
 'method_selected':'B_FACE_IDENTITY_EXPRESSIONS_2D_LOOP_THEN_NECK_ROTATION',
 'isolated_numeric_ab_status':'SYNTHETIC_TEST_ONLY',
 'actual_v20_blender_face_loop_status':'BLOCKED_MISSING_FACE_LANDMARKS_MORPHS_RIG',
 'actual_head_angle_status':'NOT_EXECUTED',
 'final_art_approval':'NOT_APPROVED'
}
file=ROOT/'NEMA_Ariadne_V90_Face2D_Loop_HeadAngle_Single_FULL_Master.yaml'
file.write_text(yaml.safe_dump(base,allow_unicode=True,sort_keys=False,width=110),encoding='utf8')
print('FULL YAML',file,'stages', [x['id'] for x in base['pipeline']],'bytes',file.stat().st_size)
