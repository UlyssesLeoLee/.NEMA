# V150 actual render art audit — REJECT and return to last engineering candidate

GitHub Actions run 45527183375 successfully built, exported, reimported the real GLB, verified 17 Blender views and no vertices in a conservative facial exclusion ROI. This is **NOT an artistic pass**.

## Visual adversarial findings from face closeups
1. Conforming the cap to skinned skull triangles avoids the old detached posterior bowl in some views.
2. At 0°, 30°, 60°, 90° and 330° multiple hair strands rise vertically into spiky, rigid pillars above the head. This is a new **severe artistic failure** and violates the approved beautiful hairstyle.
3. The face is uncovered in central zones, but forehead/temple hairline and postauricular continuity remain unapproved.
4. The head looks bald in side views; long braid attachment is not a continuous sculptural mass.
5. V147 white / purple couture remains visually incorrect, orb is unheld, and no certified independent reference registration exists.

## Root cause of new issue
Converting broad hair guide arcs to snapped nearest vertex / BVH points across a topological or geometric boundary caused successive control points to collapse or jump between scalp sectors. Bezier interpolation then created high-curvature vertical extrusions. A mask which merely reports zero hair-face collisions is **necessary but wildly insufficient** for successful grooming.

**Do NOT fix this by further arbitrary procedural tubes or local hidden patch meshes.** Art first: paint hair in approved five-view target SVG, define root triangles and barycentric weights on scalp, use continuous scalp geodesics and curvature/strand tangent regularization; art review before committing the next GLB. Explicitly guard tangent direction, segment length, root-to-tip monotonicity, scalp clearance, hair coverage without bald side and facial visibility simultaneously.

## Stop / rollback
- V150 is a diagnostic **REJECTED** model, not finished art.
- V149 is retained as the previous engineering baseline with the central face not hair-obscured; V149 itself is **NOT ART APPROVED** because of floating posterior shell.
- Per V148 no more than three severe quality failures without architecture change: reset hair representation to anatomical scalp-bound **sculpted continuous broad locks** from authored 2D cross-view target paths. Do not iterate unchanged path again.
- True 266×30 independent art ReAct cycles completed: 0 / 7980.
