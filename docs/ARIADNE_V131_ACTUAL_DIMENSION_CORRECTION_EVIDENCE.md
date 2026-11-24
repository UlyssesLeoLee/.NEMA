# Ariadne V131 — Body-anchored hair and garment scaling: actual geometry correction

**Current model status: engineering candidate, NOT artist-approved.**

V130's 390 2D ReAct updates did not include a mandatory actual-body dimension loss. Component hair, fabric and veil could improve two-dimensional projections but leave 3D absolute scale seriously wrong. V131 remedies this specific failure using anatomical measurements of the **real official MakeHuman CC0 13,380-vertex skinned body**.

## Real data and before / after

| GLB ratio | V130 source | V131 actual |
|---|---:|---:|
| Head hair cap width / skull width | 1.8301x | 1.2719x |
| White Chiton hem width / lower leg breadth | 1.8909x | 1.5504x |
| Rear veil width / shoulder width | 1.4140x | 1.1519x |
| Purple main mantle X width | 0.5034m | 0.4398m |
| Pedestal max width | 0.8581m | 0.7251m |

Measurements are computed from glTF **Y-up**, with body-only skull samples constrained to Y=1.455..1.525m and |X| <=0.145m to exclude the raised left arm. **Do not mix Blender Z-up with glTF Y-up**. Multiple height-dependent XZ taper factors are applied to garments/ornaments/veil rather than scaling the whole statue.

Source GLB SHA-256: `e0a5a487a7446e74210506aee0d26c8cad740647c1f76f80a0bd9a3f0b42ada5`.

Actual V131 GLB SHA-256: `40b1ec31028027bfa3a5af6281293d3c4c628f0d0bb7c0f0a6030756e6591bfd`.

**Quantitative audit:** 214 out of 226 scene mesh nodes have changed geometry. 13,380 source body vertices, exact ball mesh, outer gold thread and all old topology are unchanged. 0 sampled flipped triangles, clean full GLB reload. 26 identical-camera model diagnostic renders (24 azimuths + polar top/bottom) were generated from that exact exported V131 GLB.

**Build location:** Executed locally in the container and packaged with the source and complete V131 YAML. **No V131 GitHub Actions run** is claimed because the V130 source GLB exists as a local, not GitHub-hosted workflow artifact. The GitHub branch contains companion governance; user archive contains the exact runnable source and actual V131 GLB.

## Remaining hard blockers

- Even after ratios are more plausible, actual head/crown hair artistry, crown alignment, white/purple sculptural sewn cloth patterns, fitted fabric collision and human beauty are still below the user-approved concept.
- Lower-body/shoulder torso sizing ratios are engineering anchors, not independent 26-image art supervision.
- Strict original 24 angles >95%, certified real palmar orb support from art, and genuine signed-distance garment/body collision are not claimed as passed.

Full source: `src/fit_real_anatomical_proportions.py`, `src/render_v131_exact26.py`, `qa/V131_ANATOMICAL_PROPORTIONS_AUDIT.json`, in the linked V131 ZIP.
