# V141 Adversarial Audit — REJECT / next corrective direction

Evidence: GitHub Actions run 45504799485 SUCCESS as engineering build, GLB + 10 actual Blender images, engineering audit reports 495 human body vertices modified.

## Root cause results
1. **Arm pose remains wrong.** Rotating a masked selection of 495 body vertices around an estimated shoulder is not a real anatomically rigged joint deformation. The orb is near shoulder/head but not supported on the palm. Remove that vertex heuristic from the formal route. Use the MakeHuman skeleton, validated skin weights, true wrist/forearm/hand joint animation and explicit ball/palm contact coordinates.
2. **Dress remains art-inaccurate.** Pattern panels improve separability over the previous extruded cylinder, but are not fitted, seamed, collision-checked surfaces built against the body. Verify shoulder seam, waist wrap and garment-to-garment contact using actual distances. Reject any model with disconnected open panel edges.
3. **Hair cap only partially repairs the issue.** The cap and curves are physical geometry, but scalp location and ear-framing were not fitted from the authoritative target, and front beauty/head sculpt remain deficient.
4. **Gold thread cannot pass spatial placement verification.** Need explicit fixed spline constraints, body-outside rule and no intersections.
5. **2D art authority is missing.** A newly generated 2D target must not be considered the user's approved high-resolution calibrated 266-camera truth. 10 render outputs != 266 ReAct cycles. No verified 95% per-view claim.

## Mandatory production sequence
P0 reference/camera lock -> P1 official anatomically rigged target pose, verified hands -> P2 3D tailored cut patterns, contact and fold sculpt -> P3 face and rooted hair, multiple closeups -> P4 material and gold line -> P5 all 266 views and per-angle ReAct with independently approved target -> P6 user art approval.

Outcome: ART_REJECT. Keep V141 as an engineering diagnostic candidate, NOT as a formal sculptural asset. No Vercel deployment.
