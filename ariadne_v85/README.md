# Ariadne V85 — GitHub Blender model/render execution

This is an **engineering geometry and cloth render**, not a V20 art-matched final GLB.

- Workflow: `.github/workflows/ariadne_v85_blender.yml`, on branch `ariadne_v85_github_blender`.
- Source: official MakeHuman community CC0 base OBJ + CC0 young-female macro target; verify **Git blob SHA1**, **CC0 headers**, SHA256 and topology before creating actual body mesh.
- Model: MakeHuman human mesh (no primitive proxy body), preliminary anatomical whole-mesh arm pose, connected chiton surface plus an independent real himation garment layer.
- Solver: actual Blender CLOTH, collision/self-collision on, 42 frames; deformed polygons are frozen into GLB; displacement logged.
- Render: 24 locked 15-degree views, six key screenshots, contact sheets produced from actual Blender PNGs.
- Outputs: `Ariadne_V85_Engineering_NOT_ART.glb`, `Ariadne_V85_CC0_Cloth_Engineering.blend`, `cloth_solver_proof.json`, `BUILD_AUDIT.json`, all view PNGs.

## Strict limitations

The user-authored V20 independent front reference, 24-angle turnaround, approved 256-point landmark correspondences and approved final tailoring are still unavailable. No art similarity score is computed. Pose (especially palm/sphere, shoulder and garment) is **not approved**. This code is not a replacement for V85_R30's 30-round 2D/3D sculpt/refit pipeline. Outputs must never be presented as passing the 95% per-angle final statue gate.

Independent MakeHuman source and license: https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md

Blender source: https://download.blender.org/release/Blender4.5/

Follow the run and download the verified workflow artifact in the GitHub Actions tab.
