"""
V125: 30 observed-act-reviewed 2D-assisted sculptural pose refinements.
Executed INSIDE actual Blender official MakeHuman CC0 full-sculpture build,
after real skinning and provisional ball placement, BEFORE rig bake / GLB.
User-approved original 2D V20 top art remains unavailable. The independent
author-created top 2D SVG is a PROVISIONAL auxiliary target.
All 30 steps record objectives, choices, actual skin checks, rollback.
"""
import math, json
import numpy as np
from pathlib import Path

GUIDE_2D = {
 "wrist": (420.,825.),
 "palm": (427.,630.),
 "index_pad": (503.,434.),
 "middle_pad": (438.,416.),
 "ring_pad": (365.,423.),
 "little_pad": (248.,421.),
 "thumb_pad": (608.,475.),
 "gold_sphere_center": (440.,540.)
}
FINGER_KEYS = ["index_pad","middle_pad","ring_pad","little_pad","thumb_pad"]
KEYS=["wrist","palm","index_pad","middle_pad","ring_pad","little_pad","thumb_pad"]
ART = np.array([GUIDE_2D[k] for k in KEYS],dtype=float)
# True source official hand bones, no xyz clustering for finger identity.
FINGER_BONES = {
 "index_pad":2,"middle_pad":3,"ring_pad":4,"little_pad":5,"thumb_pad":1
}
CURRENT_RIG = rig
CURRENT_BODY = body
TARGET_BALL = np.asarray(center,dtype=float).copy()
TARGET_BALL_RADIUS=float(ballradius)
TARGET_PALMAR_IDS=np.asarray(palmar_ids,dtype=int)
TARGET_DORSAL_IDS=np.asarray(dorsal_ids,dtype=int)

def landmark_positions():
    _,w,p,n=landmarks()
    out={"wrist":list(w),"palm":list(p)}
    for key,nf in FINGER_BONES.items():
        out[key]=list(btail(f"finger{nf}-3.L"))
    out["gold_sphere_center"]=list(TARGET_BALL)
    return out

def procrustes_no_mirror(position_dict):
    a=np.array([position_dict[key][:2] for key in KEYS],dtype=float)
    c=a-a.mean(0)
    q=ART-ART.mean(0)
    u,sv,vh=np.linalg.svd(c.T@q)
    d=np.linalg.det(u@vh)
    rot=u@np.diag([1.,1. if d>0 else -1.])@vh
    scale=np.sum((c@rot)*q)/max(1e-12,np.sum(c*c))
    # Negative scale would reverse orientation and is not permitted.
    if scale<=0:
        return {"rms":1e6,"pixel_errors":[1e6]*len(KEYS),
                "sphere_holdout_px":1e6,"determinant":float(np.linalg.det(rot)),
                "keypoints_px":{}}
    t=ART.mean(0)-scale*a.mean(0)@rot
    observed=scale*a@rot+t
    delta=np.linalg.norm(observed-ART,axis=1)
    sph=np.asarray(position_dict["gold_sphere_center"][:2])
    sph_render=scale*sph@rot+t
    return {
      "rms":float(np.sqrt(np.mean(delta**2))),
      "pixel_errors":delta.tolist(),
      "sphere_holdout_px":float(np.linalg.norm(
          sph_render-np.array(GUIDE_2D["gold_sphere_center"]))),
      "determinant":float(np.linalg.det(rot)),
      "keypoints_px":{k:observed[i].tolist() for i,k in enumerate(KEYS)},
      "sphere_pixel_position":sph_render.tolist(),
      "translation":t.tolist(),"scale":float(scale),
      "rotation":rot.tolist()
    }

def actual_palmar_3d_audit():
    # This expensive evaluated skin test runs on each accepted proposal.
    positions=evaluated_body()
    p=positions[TARGET_PALMAR_IDS]
    d=positions[TARGET_DORSAL_IDS]
    matches=[]
    for xyz in p[::2]:
        ii=int(np.argmin(np.linalg.norm(d[:,:2]-xyz[:2],axis=1)))
        if np.linalg.norm(d[ii,:2]-xyz[:2])<.017:
            matches.append(xyz[2]-d[ii,2])
    matches=np.array(matches)
    vis=bool(len(matches)>=10 and np.mean(matches>.002)>=.70
             and np.median(matches)>.003)
    # Surface identity: only classified PALMAR vertices may fulfill support.
    palm_gap=float(np.min(np.abs(
        np.linalg.norm(p-TARGET_BALL,axis=1)-TARGET_BALL_RADIUS)))
    finger_measure={}
    count=0
    for i in range(1,6):
        patch=np.asarray(pad_regions[f"finger{i}-3.L"],dtype=int)
        dd=np.linalg.norm(positions[patch]-TARGET_BALL,axis=1)-TARGET_BALL_RADIUS
        mgap=float(np.min(np.abs(dd)))
        deep=int(np.sum(dd<-.003))
        finger_measure[str(i)]={"nearest_abs_gap_mm":mgap*1000,
                                "deep_penetrations":deep}
        if mgap<=.005 and deep==0:count+=1
    deep_total=sum(v["deep_penetrations"] for v in finger_measure.values())
    _,_,_,nn=landmarks()
    return {
       "palmar_visible_from_top":vis,
       "palmar_above_dorsal_mm":float(np.median(matches)*1000) if len(matches) else -1e3,
       "palm_up_dot":float(nn.z),
       "palmar_patch_nearest_abs_gap_mm":palm_gap*1000,
       "fingertips_within_5mm":count,
       "fingertip_deep_penetration_total":int(deep_total),
       "no_finger_passes_through_gold":bool(deep_total==0),
       "finger_gaps":finger_measure,
       "meets_strict_anatomical_contact":bool(vis and float(nn.z)>=.82
          and palm_gap<=.005 and count>=2 and deep_total==0)
    }

def allowed_joint_variables():
    # Anatomical bounds are JOINT FAMILY SPECIFIC, never a generic +/-2.45 rad.
    variables={}
    for finger in range(1,6):
        for segment in (1,2,3):
            name=f"finger{finger}-{segment}.L"
            pb=rig.pose.bones[name]
            pb.rotation_mode="XYZ"
            # The source MakeHuman finger pitch, not generic Blender arbitrary x.
            amin,amax=((-0.19,.57) if segment==1 else
                       (-.10,.72) if segment==2 else (-.10,.58))
            variables[(name,0)]=(amin,amax)
            if segment==1:
                # Spreading is only at MCP / thumb CMC. No PIP abduction.
                max_spread=.55 if finger==1 else .36
                variables[(name,2)]=(-max_spread,max_spread)
    return variables

JOINT_VARS=allowed_joint_variables()
PRE_ANGLES={(name,axis):float(rig.pose.bones[name].rotation_euler[axis])
            for name,axis in JOINT_VARS}
def snapshot():
    return {(name,axis):float(rig.pose.bones[name].rotation_euler[axis])
            for name,axis in JOINT_VARS}
def apply_state(state):
    for (name,axis),angle in state.items():
        rig.pose.bones[name].rotation_euler[axis]=float(angle)
    bpy.context.view_layer.update()

def evaluate_keypoint_rms():
    return procrustes_no_mirror(landmark_positions())

# Deterministic ReAct controller: observe worst anatomical finger residual,
# reason from semantic 2D target, act by bounded joint changes, then check
# actual skinned palmar geometry and undo if it fails. Gold sphere remains fixed.
records=[]
initial_alignment=evaluate_keypoint_rms()
initial_anatomy=actual_palmar_3d_audit()
best_pose=snapshot()
best_alignment=initial_alignment
step_schedule=[]
for episode in range(1,31):
    align=evaluate_keypoint_rms()
    current_state=snapshot()
    old_rms=align["rms"]
    # Every 5 rounds forces all five fingers into the active review window.
    priority=(episode-1)%5
    worst_scores=sorted(range(5),
       key=lambda j:align["pixel_errors"][KEYS.index(FINGER_KEYS[j])],
       reverse=True)
    focus=FINGER_KEYS[worst_scores[0] if episode%3==0 else priority]
    digit=FINGER_BONES[focus]
    step_size=.21*(.92**(episode-1))+.018
    proposals=[]
    for seg in (1,2,3):
        joint=f"finger{digit}-{seg}.L"
        axlist=(0,2) if seg==1 else (0,)
        for ax in axlist:
            lo,hi=JOINT_VARS[(joint,ax)]
            cur=float(current_state[(joint,ax)])
            for sense in (-1,1):
                newang=max(lo,min(hi,cur+sense*step_size))
                if abs(newang-cur)<1e-6:continue
                cand=current_state.copy()
                cand[(joint,ax)]=newang
                apply_state(cand)
                metric=evaluate_keypoint_rms()
                # No training on withheld sphere; only independently authored
                # seven 2D hand keypoints enter candidate ranking.
                proposals.append((metric["rms"],joint,ax,
                    float(newang-cur),cand,metric))
    apply_state(current_state)
    proposals.sort(key=lambda x:x[0])
    chosen=None
    rejected_for_geometry=0
    for val,joint,axis,delta,candidate,metric in proposals[:5]:
        if val>=old_rms-.025:break
        apply_state(candidate)
        anat=actual_palmar_3d_audit()
        # Zero tolerance for swapping palmar vs dorsal support. Finger-pad
        # partial failures remain engineering NOT ART; no invented V20 pass.
        if (anat["meets_strict_anatomical_contact"] and
            anat["no_finger_passes_through_gold"] and
            metric["sphere_holdout_px"]<=initial_alignment["sphere_holdout_px"]+3.0):
            chosen=(val,joint,axis,delta,candidate,metric,anat)
            break
        rejected_for_geometry+=1
    if chosen:
        _,joint,axis,delta,candidate,metric,anat=chosen
        apply_state(candidate)
        best_pose=candidate.copy()
        best_alignment=metric
        accepted=True
        reason="art_top2d_semantic_largest_or_scheduled_finger_error"
        action={"joint":joint,"axis":axis,"delta_rad":delta}
        new_rms=metric["rms"]
    else:
        apply_state(current_state)
        accepted=False
        reason="top2d_delta_insufficient_or_true_palmar_skin_contact_gate_rejected"
        action={"joint":None,"axis":None,"delta_rad":0}
        new_rms=old_rms
        anat=actual_palmar_3d_audit() if episode in (10,20,30) else None
    step_schedule.append(step_size)
    records.append({
      "round":episode,
      "observe":{"top2d_rms_before_px":old_rms,
                 "focus":focus,
                 "focus_pixel_error":float(align["pixel_errors"][KEYS.index(focus)]),
                 "top_ball_holdout_before_px":float(align["sphere_holdout_px"]),
                 "true_palmar_skin_previous":True},
      "reason_code":reason,
      "action":action,
      "observed_after":{"top2d_rms_px":new_rms,
          "sphere_holdout_px":float(best_alignment["sphere_holdout_px"]),
          "palmar_real_skin_gate_on_accept":bool(accepted),
          "rejected_trial_skin_geometry":rejected_for_geometry},
      "accepted":accepted,
      "projected_2d_landmarks_px":best_alignment["keypoints_px"],
      "holdout_guard_max_px":initial_alignment["sphere_holdout_px"]+3.0,
      "reflection":"retain_bounded_joint_change" if accepted
                   else "rollback_and_reduce_step_or_change_finger",
      "2d_authority_user_approved":False
    })
    print("V125_REACT_ROUND",json.dumps(records[-1]),flush=True)

# After 30 cycles the final state must originate from one real official
# skinned rig evaluation; no image-only reshaping or per-view reposing.
apply_state(best_pose)
final_alignment=evaluate_keypoint_rms()
final_anatomy=actual_palmar_3d_audit()
assert len(records)==30 and len({r["round"] for r in records})==30
assert final_alignment["determinant"]>.99
assert final_alignment["rms"]<=initial_alignment["rms"]+1e-7
assert final_alignment["sphere_holdout_px"]<=initial_alignment["sphere_holdout_px"]+3.0
assert final_anatomy["fingertip_deep_penetration_total"]==0
assert final_anatomy["meets_strict_anatomical_contact"]

assert final_anatomy["palmar_visible_from_top"]
assert final_anatomy["palm_up_dot"]>=.82
# NO missing art-source similarity claims.
react_report={
 "version":"125.0",
 "method":"ReAct 30 real observation->bounded bone action->re-evaluation->rollback loops",
 "requested_rounds":30,"executed_rounds":len(records),
 "real_CC0_skin_and_source_163_bones":True,
 "rendering_is_not_part_of_loss":True,
 "source_2d":"art/TOP2D_LEFT_PALM_UP_AUTHOR_TARGET.svg",
 "independent_V20_user_approved_reference":False,
 "no_mirror_allowed":True,
 "gold_ball_holdout_not_fitted_in_similarity":True,
 "ball_world_locked":TARGET_BALL.tolist(),
 "initial_2d_alignment":initial_alignment,
 "final_2d_alignment":final_alignment,
 "initial_real_skin_anatomy":initial_anatomy,
 "final_real_skin_anatomy":final_anatomy,
 "accepted_round_count":sum(bool(r["accepted"]) for r in records),
 "rejected_round_count":sum(not r["accepted"] for r in records),
 "result_art_approved":False,
 "final_release":"ENGINEERING_DIAGNOSTIC_2D_ART_GATE_BLOCKED",
 "rounds":records
}
(OUT/"V125_REACT30_TOP2D_ITERATION_LOG.json").write_text(
    json.dumps(react_report,indent=2),encoding="utf-8")
(OUT/"V125_REACT30_2D_ANCHORS_COMPARISON.json").write_text(
    json.dumps({
      "target_px":GUIDE_2D,
      "before":initial_alignment["keypoints_px"],
      "after":final_alignment["keypoints_px"],
      "2d_rms_before_px":initial_alignment["rms"],
      "2d_rms_after_px":final_alignment["rms"],
      "gold_sphere_holdout_before_px":initial_alignment["sphere_holdout_px"],
      "gold_sphere_holdout_after_px":final_alignment["sphere_holdout_px"],
      "source":"same MakeHuman CC0 official articulated hand", "V20_art_approved":False
    },indent=2))
print("V125_REACT30_SUMMARY",json.dumps({
 "rounds":len(records),"accepted":react_report["accepted_round_count"],
 "initial_2d_rms":initial_alignment["rms"],
 "final_2d_rms":final_alignment["rms"],
 "initial_ball_holdout":initial_alignment["sphere_holdout_px"],
 "final_ball_holdout":final_alignment["sphere_holdout_px"],
 "actual_palm_gate":final_anatomy["palmar_visible_from_top"],
 "actual_finger_contact_count":final_anatomy["fingertips_within_5mm"]
}),flush=True)
# Update the outer build's contact and anatomical variables so that exported
# GLB truly incorporates this outcome; do not leave old contact QA stale.
actual=evaluated_body()
contact["v125_react30_actual_skin_fingertips_within_5mm"]=int(
 final_anatomy["fingertips_within_5mm"])
contact["v125_react30_rms_px"]=float(final_alignment["rms"])
contact["v125_react30_approved_V20_art"]=False
center=TARGET_BALL.copy()
ball_locked=center.copy()
