# Ariadne V120 — GitHub Real Rig Pose Audit (2026-11-24)

## Verified execution
- GitHub Actions: https://github.com/UlyssesLeoLee/.NEMA/actions/runs/45309917671
- Result: SUCCESS, engineering-only (NOT ART APPROVED).
- Prior V16 Blender/Rigify neutral source from Actions run 44399369733.
- Runner ubuntu-latest, Blender 5.0.1. Earlier attempt using Blender 4.0.2 could not read the Blender 5 source file.
- In headless mode the original FK controls did not produce visible deformation. The fail-closed test caught it. The successful implementation extracts real deform bones from existing Rigify and poses those bones using the real skinned female MakeHuman anatomical mesh.
- Original MakeHuman default.mhskel and default_weights.mhw were independently downloaded in V104 run 45160529755. V120 uses historical Rigify automatic skinning weights, NOT a certified remapping of the official .mhw weights.

## Numerical measurements
- Original MakeHuman vertex count: 19158.
- Body quad face count: 13378.
- glTF skins: 1.
- Exported live skin joints: 160.
- Evaluated body vertices moved by >0.5mm: 5336.
- Maximum motion: 0.6720044605981729 m (far too large to assume anatomically ideal).
- GLB file size: 788364 bytes.
- GLB SHA256: e52798b56693c3fc0288342fa6bf484ac59baa3d5cd1295570d639093f4d1132.
- Exported GLB: V120_MakeHuman_LiveSkinnedPose_ENGINEERING_NOT_ART.glb.
- Editable project: V120_RealRig_Posed_Editable_NOT_ART.blend.
- Twenty-four fixed camera PNGs from the actual reimported engineering GLB. These are NOT V20 art anchors.
- Artifact stored in successful GitHub run 45309917671.

## Stage decisions
| Stage | State | Evidence |
|---|---|---|
| P00 CC0 source | Historical PASS | V16 and V104 verified GitHub sources |
| P01 real anatomical body and live rig | ENGINEERING PASS | 19158 vertices, live GLB skin, 160 joints |
| P02 24 independently approved V20 art images + 256 landmark observations | BLOCKED | not in GitHub reference manifest |
| P05 joint-local deformation and glTF reload | ENGINEERING PASS | 5336 displaced vertices, 24 fresh views |
| P05 artistic anatomy and correct K pose | NOT APPROVED | body motion magnitude must be reviewed |
| P06 palm-up gold ball multi-contact | BLOCKED | artistic targets, anatomy and contact not validated |
| P07 garment with true cloth after pose lock | BLOCKED | depends on P06 |
| P09 normal/ray/3DGS comparison | NOT EXECUTED ON V20 | only V118 synthetic evidence |
| P16 full sculpture >95% for every one of 24 original views | BLOCKED | no independent art score |

## Proven workflow now established
GitHub Actions artifact -> Blender 5.0.1 -> authentic MakeHuman female base and Rigify skin -> real deform bone FK pose -> evaluate source mesh displacement -> glTF with live skin -> clean reimport -> 24-view engineering audit -> hard-gate art release.
