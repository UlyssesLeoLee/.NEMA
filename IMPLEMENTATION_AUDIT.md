# V86 GitHub integration — execution and adversarial review

- Intended branch: `ariadne_v86_design_first`
- Artifact: `.github/workflows/ariadne_v86_design_first.yml`
- Legacy V85: preserved only for history, **not used** by the V86 workflow.
- No `if: false` modeling placeholders, no swallowed nonzero preflight exit.
- Design source gate must fail before Blender when approved `.blend` or independent art is absent.
- V86 Blender runtime requires real garment mesh, design revision, authored-fold declaration, group weights, pin coverage, and real topology before CLOTH.
- Cloth can change only permitted secondary regions; protected outline and fold positions are compared with both mean and maximum drift (not just average).
- Real-body source (MakeHuman/CC0) is verified separately from art/pose approval.
- Only engineering model GLB can be emitted without artwork approval. The independent final 24-view release audit is opt-in, fail closed and separate.
- Local test report created by actual pytest run. GitHub run result will be reported separately.

**Current input blocker:** independent V20 artwork and approved design-first `.blend` and approved pattern evidence unavailable. Lack of these inputs must be visible as a failed `design-input-gate` job, not a success badge.
