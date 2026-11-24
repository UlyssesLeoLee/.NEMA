# Ariadne V130 — Actual 390-round 2D-assisted ReAct engineering execution

**Build source:** Actual V129 exported official MakeHuman CC0 model (163 original source bones, baked GLB). `d4399072e0573fed60bd6ab2dc7ed2a8ef42a5230decbc28958443aa165fd04a`.

**Final actual GLB SHA256:** `e0a5a487a7446e74210506aee0d26c8cad740647c1f76f80a0bd9a3f0b42ada5`.

**Execution location:** local sandbox, *not a GitHub Actions V130 run*. GitHub Actions previously produced V129; V130 was actually edited, re-exported, reimported and externally rendered locally. Source and 390-round logs are in the downloadable user package.

## Evidence
- 12 governed components x 30 ReAct loops = 360, plus 30 joint reconciliation = **390 executed**.
- **141 accepted** geometry proposals, 249 rejected/rolled back; 390 genuine front/top 2D correspondence PNGs, 13 JSON round logs.
- 136 existing V129 objects with measured vertex changes (>50 μm). The skin remains the original source, so vertex deformation **does not count as a new anatomical joint or rig solve**.
- A separate post-loop sculpt added **53 genuine hair, braid, chignon and laurel meshes**, yielding **226 mesh objects** (all 173 original object names survive with the same vertex and triangle counts).
- A separate collision resolution fixed **43 purple cloth-to-chiton front occlusion sample violations** (0 remain) with 0 new flipped cloth faces.
- Independent anti-inversion guard rolled back offending veil / base changes; final original-173 normal-orientation reversal count **0**. These guard repairs are not counted among accepted ReAct actions.
- Final **26 model-diagnostic views** (24x15° horizontal plus vertical top and bottom), from exactly the final GLB SHA.
- Combined original approved art is a single page with a hero and tiny views. It is **not 26 independent, calibrated high-resolution art targets**, so pixel-perfect or per-view >95% restoration CANNOT be claimed.

## Open art blockers
The model remains an engineering candidate. Sculpted beauty of face, complete palmar-vs-dorsal and finger-pad contact in original art, flowing Greek royal Chiton/Himation, side braids and original K-golden-ratio are not art-approved. Independent full-resolution 26-view art, semantic correspondence and visual approval are still required.

**Source-of-truth V130 YAML:** `NEMA_Ariadne_V130_SINGLE_FULL_MASTER.yaml` in the downloadable package (preserves original V129 and older sections); the short governance YAML in this repository is a companion, **not** the full master.
