#!/usr/bin/env python3
"""A/B isolated simulation; this is NOT artistic V20 likeness evidence."""
import json
from pathlib import Path
import numpy as np
from face_2d_loop import fit_landmark_loop, project_ortho_xy, pose_after_face_locked

ROOT=Path(__file__).resolve().parents[1]

def build_toy():
    # Synthetic set of 40 face semantic landmarks, head local coords meters.
    rng=np.random.default_rng(901)
    n=40
    regions=np.array(['eye']*8+['brow']*8+['nose']*8+['lips']*8+['jaw']*8)
    x=np.linspace(-.075,.075,n)
    z=1.55+0.11*np.sin(np.linspace(0,3*np.pi,n))+rng.normal(0,.002,n)
    y=-.025-.02*np.cos(np.linspace(0,3*np.pi,n))
    verts=np.column_stack([x,y,z]); deltas=np.zeros((5,n,3))
    for j,r in enumerate(['eye','brow','nose','lips','jaw']):
        pick=(regions==r)
        deltas[j,pick,0] = (.008 if j%2==0 else -.006)*np.sign(x[pick]+.001)
        deltas[j,pick,2] = .009 * np.cos(np.linspace(-np.pi/2,np.pi/2,int(pick.sum())))
        deltas[j,pick,1] = .003
    weights=np.ones(n)
    return verts,deltas,regions.tolist(),weights

def run(write=True):
    verts,deltas,regions,weights=build_toy()
    true_p=np.array([.36,-.22,.29,-.31,.15])
    target=project_ortho_xy(verts+np.tensordot(true_p,deltas,axes=(0,0)),yaw_deg=0)
    # A: simultaneous face fitting in an arbitrarily tilted head coordinate frame.
    a=fit_landmark_loop(verts,deltas,target,weights,regions,yaw_deg=22.,allowed_yaw_for_face_loop=180,max_rounds=30)
    # B: recover the real 2D front facial proportions/expression before any head turn.
    b=fit_landmark_loop(verts,deltas,target,weights,regions,yaw_deg=0,max_rounds=30)
    approved_face=verts+np.tensordot(b.coeffs,deltas,axes=(0,0))
    pose=pose_after_face_locked(approved_face,22.)
    result={
      'scope':'SYNTHETIC_SOLVER_AB_NOT_REAL_V20_ART_QUALITY',
      'comparison':'A angled head simultaneous 2D face fit vs B neutral front first then rigid head transfer',
      'A_first_fit_loss':a.initial_loss,'A_final_fit_loss':a.final_loss,
      'B_first_fit_loss':b.initial_loss,'B_final_fit_loss':b.final_loss,
      'B_beats_A_on_toy_data':b.final_loss<a.final_loss,
      'B_fit_rounds':len(b.trace)-1,'A_fit_rounds':len(a.trace)-1,
      'B_head_transfer':pose,
      'face_shape_keys_are_real_on_actual_GLB':False,
      'validated_V20_2D_landmarks_available':False,
      'real_24_view_art_approval':False,
      'real_head_pose_blender_executed':False,
      'conclusion':'B is algorithmically separable and safer; real mesh fit and anatomical expression remain BLOCKED until registered facial morphs and independent 2D annotations exist',
      'B_history':b.trace
    }
    if write:
        dst=ROOT/'report/face2d_AB_numeric.json'
        dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
