#!/usr/bin/env python3
"""V90 face-first iterative 2D landmark solver.

This numerical core acts on existing, source-verified 3D face shape-key deltas.
It never creates anatomy or labels a synthetic test as V20 art reconstruction.
Inputs target_uv must be independently annotated, camera-registered artwork.
Requires numpy. Run ab_synthetic.py for isolated algorithmic A/B testing.
"""
from dataclasses import dataclass
from typing import Sequence
import numpy as np

REGIONS = frozenset({'eye','brow','nose','lips','jaw','cheek','chin','ear','other'})


def rotate_yaw(vertices: np.ndarray, yaw_deg: float) -> np.ndarray:
    """Rigid head turn about Z, for a Z-up head local coordinate system."""
    t=np.deg2rad(float(yaw_deg))
    c,s=np.cos(t),np.sin(t)
    r=np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
    return np.asarray(vertices)@r.T


def project_ortho_xy(vertices: np.ndarray, yaw_deg: float=0.0) -> np.ndarray:
    """Synthetic test camera only: (x,z) orthographic, not V20 camera calibration."""
    vertices=rotate_yaw(vertices,yaw_deg)
    return vertices[:,[0,2]]


def robust_huber(x: np.ndarray, delta: float) -> np.ndarray:
    a=np.abs(x)
    return np.where(a<=delta,0.5*x*x,delta*(a-0.5*delta))


@dataclass
class LoopResult:
    coeffs: np.ndarray
    initial_loss: float
    final_loss: float
    trace: list
    converged: bool
    evidence_scope: str


def _check(neutral, deltas, target, weights, regions, bounds):
    neutral=np.asarray(neutral,float);deltas=np.asarray(deltas,float);target=np.asarray(target,float)
    weights=np.asarray(weights,float)
    if neutral.ndim!=2 or neutral.shape[1]!=3 or len(neutral)<12:
        raise ValueError('REAL_REGISTERED_FACE_LANDMARKS_AT_LEAST_12_REQUIRED')
    if deltas.ndim!=3 or deltas.shape[1:]!=neutral.shape or deltas.shape[0]<2:
        raise ValueError('INDEPENDENT_ANATOMICAL_MORPH_BASIS_REQUIRED')
    if target.shape!=(len(neutral),2) or not np.all(np.isfinite(target)):
        raise ValueError('TARGET_2D_REGISTRATION_INVALID')
    if weights.shape!=(len(neutral),) or np.any(weights<0) or weights.sum()<1 or not np.all(np.isfinite(weights)):
        raise ValueError('INVALID_FACE_CONFIDENCE_WEIGHTS')
    if len(regions)!=len(neutral) or not set(regions)<=REGIONS:
        raise ValueError('UNREGISTERED_FACIAL_SEMANTIC_REGION')
    if not {'eye','brow','nose','lips','jaw'} <= set(r for r,w in zip(regions,weights) if w>0):
        raise ValueError('FIVE_CRITICAL_FACE_REGIONS_NOT_ANNOTATED')
    if not np.isfinite(deltas).all() or not np.isfinite(neutral).all():
        raise ValueError('INVALID_3D_FACE_PRIOR')
    if bounds<=0 or bounds>1.0:raise ValueError('OUT_OF_RANGE_EDIT_BOUNDS')
    return neutral,deltas,target,weights


def fit_landmark_loop(neutral, deltas, target, weights, regions:Sequence[str],
                      *, yaw_deg:float=0.0, max_rounds:int=25,
                      max_step:float=.17, bound:float=.75,
                      damping:float=1e-7, huber_delta:float=.05,
                      convergence_epsilon:float=1e-8,
                      allowed_yaw_for_face_loop:float=0.1) -> LoopResult:
    """A trust-region Gauss-Newton loop over valid source shape keys.

    The `allowed_yaw_for_face_loop` safeguard can be relaxed ONLY in the
    experimental A condition, never in a production face-canonical pass.
    """
    neutral,deltas,target,weights=_check(neutral,deltas,target,weights,regions,bound)
    if max_rounds<1 or max_rounds>100:raise ValueError('INVALID_ROUND_COUNT')
    if abs(yaw_deg)>allowed_yaw_for_face_loop:
        raise ValueError('FACE_2D_CANONICAL_NOT_NEUTRAL_BEFORE_FIT')
    k=len(deltas)
    values=np.zeros(k)
    region_weights=np.array([2.2 if r in ('eye','lips','nose','brow') else 1.0 for r in regions])
    effective=weights*region_weights
    def shape(p):return neutral + np.tensordot(p,deltas,axes=(0,0))
    def pred(p):return project_ortho_xy(shape(p),yaw_deg)
    def loss(p):
        dif=pred(p)-target
        data=float(np.sum(robust_huber(dif,huber_delta)*effective[:,None])/effective.sum())
        regularization=float(damping*np.dot(p,p))
        return data+regularization
    baseline=loss(values)
    trace=[{'round':0,'loss':baseline,'accepted':True,'coeffs':values.tolist()}]
    w=np.repeat(np.sqrt(effective),2)
    converged=False
    for i in range(1,max_rounds+1):
        p0=pred(values)
        err=(target-p0).reshape(-1)
        J=np.zeros((len(err),k),float)
        eps=1e-4
        for j in range(k):
            v=values.copy();v[j]+=eps
            J[:,j]=((pred(v)-p0)/eps).reshape(-1)
        # Classic damped least-squares trial step, clipped to a conservative sculpt budget.
        Aw=J*w[:,None];bw=err*w
        mat=Aw.T@Aw + (damping+1e-6)*np.eye(k)
        step=np.linalg.solve(mat,Aw.T@bw-damping*values)
        step=np.clip(step,-max_step,max_step)
        old_loss=loss(values)
        accepted=False
        for shrink in (1.,.5,.25,.125,.0625):
            candidate=np.clip(values+step*shrink,-bound,bound)
            new_loss=loss(candidate)
            if new_loss < old_loss-1e-13:
                values=candidate
                accepted=True
                break
        trace.append({'round':i,'loss':float(loss(values)),'accepted':accepted,
                      'coeffs':[round(float(v),8) for v in values]})
        if not accepted or (old_loss-loss(values))<convergence_epsilon:
            converged=True
            break
    return LoopResult(values,baseline,loss(values),trace,converged,'NUMERIC_GEOMETRY_TEST_ONLY_NOT_V20_ART')


def pose_after_face_locked(face_local_points:np.ndarray, angle_deg:float)->dict:
    """Rigid transform invariant used to prevent expression changes during head pose."""
    v=np.asarray(face_local_points,float)
    if v.ndim!=2 or v.shape[1]!=3 or len(v)<12: raise ValueError('REGISTERED_FACE_VERTICES_REQUIRED')
    moved=rotate_yaw(v,angle_deg)
    n=len(v)
    # Compare fixed facial-pair distances, not camera-space distances.
    pairs=[(i,j) for i in range(min(n,24)) for j in range(i+1,min(n,24))]
    before=np.array([np.linalg.norm(v[i]-v[j]) for i,j in pairs])
    after=np.array([np.linalg.norm(moved[i]-moved[j]) for i,j in pairs])
    err=float(np.max(np.abs(before-after)))
    return {'max_pairwise_distance_delta_m':err,'pose_deg':angle_deg,
            'face_geometry_unchanged':err<1e-10,
            'note':'Rigid math unit test only; actual Blender neck skin deformation must be independently audited'}
