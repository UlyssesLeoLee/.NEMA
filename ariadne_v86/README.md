# Ariadne V86 — design-first GitHub Blender workflow

**Purpose:** hard block free-drop cloth generated from tubes/sheets. Garment silhouette, primary folds, chest–shoulder–waist draping and royal costume composition must exist as authored 3D geometry **before** secondary Blender cloth simulation.

## GitHub Actions

Workflow: `.github/workflows/ariadne_v86_design_first.yml` on branch `ariadne_v86_design_first`.

Actual execution graph: `policy-tests` → `design-input-gate` → `blender-design-first` → optional `independent-art-release-check`.

- `policy-tests`: run V86 unit tests including adversarial input mutations. Pass does **not** certify the model.
- `design-input-gate`: strictly validate independent V20 original front and turnaround images, reviewed design manifest with binding SHA256, actual `.blend` header and required drawings. Missing or mismatched assets **fail the GitHub job** (no `|| true`), and upload JSON diagnostics.
- `blender-design-first`: starts **only if design inputs are accepted**. Uses MakeHuman CC0 female mesh, Blender 4.5.15 on GitHub Ubuntu runner, genuine `.blend` garment asset containing authored main folds, PIN/locked areas, controlled Cloth simulation, displacement audit, 24 locked-view Blender renders, engineering-only GLB and GLB roundtrip verification.
- Optional release audit is **separate** and requires independently approved art, independent 24-view scoring all strictly >95%, and explicit user approval. Neither a green runner nor a contact sheet authorizes final release.

## Required design source assets (not included or fabricated)

Copy files into the repository (the path is relative to `ariadne_v86/`):

```
assets/reference/V20_Original_Front_Art_Reference.png
assets/reference/V20_24Art_Turnaround.png
assets/pattern/garment_design_first.blend
assets/pattern/garment_design_manifest.json
assets/pattern/garment_design_map.yaml
assets/pattern/fold_flow_map.svg
assets/pattern/layer_structure_map.svg
assets/pattern/primary_fold_review_sheet.png
```

The manifest MUST be prepared from actual checked/approved design assets. See `garment_design_manifest.EXAMPLE.json` as an **unapproved** structural template. Fill the SHA256 of all source and drawing bytes; `reviewer` must name the actual human reviewer. A template cannot authorize simulation.

The `.blend` must contain mesh `Garment_DesignFirst`, with actually sculpted primary-fold geometry, custom properties `primary_fold_sculpt_locked=true`, `design_revision=<manifest.pattern_revision>`, **one connected primary fabric surface**, plus these vertex groups:

```
PIN
PRIMARY_OUTLINE_LOCK
PRIMARY_FOLD_LOCK
SECONDARY_SIM_ZONE
WAIST_GATHER
SHOULDER_DRAPE
CHEST_U_DRAPE
BACK_VEIL_ANCHOR
```

Every protected silhouette/main-fold/waist/shoulder/chest/veil vertex must have **PIN ≥0.98**; at least 1% of cloth vertices must remain unpinned within `SECONDARY_SIM_ZONE`. The solver uses **PIN** as an actual positional constraint, not a material-stiffness proxy. Simulation is rejected if individual or mean protected vertex displacement exceeds the V86 thresholds.

This is necessary but **not sufficient** for an artistically correct sculpt: fabric outline, major folds, silhouette, hand/sphere contact, face, pose and 24 independent art alignments still require real review and repair.

## Current status

The approved cloth `.blend`, manifest, 2D artwork and art-review files are not in the branch. The first GitHub run is therefore **expected to fail at the design-input gate** and skip all modeling/rendering jobs. This is a deliberate fix of V85's unapproved automatic garment generation, **not** a rendering success claim.

## Local policy tests

```bash
python -m pip install pytest==8.4.1 PyYAML==6.0.2 Pillow==11.3.0
python -m pytest -q ariadne_v86/tests
python ariadne_v86/src/gates.py --stage design --strict
```

## Provenance / limitations

MakeHuman source generator retained from existing verified V85 branch and records an official CC0 female-target mesh. This is not evidence that its pose is anatomically suited to V20 or that hand/ball contact has been solved. Art measurements cannot be replaced with re-rendered viewpoints of the same mesh.
