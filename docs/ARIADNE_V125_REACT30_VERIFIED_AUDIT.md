# Ariadne V125 — Actual 30-round ReAct 2D-assisted hand and ball optimization

## Execution

- Actual GitHub Actions success: [run 45342735674](https://github.com/UlyssesLeoLee/.NEMA/actions/runs/45342735674)
- Final artifact ID: 14896782684, name Ariadne-V125-30RealReAct-Top2D-OfficialCC0-NOT-ART
- Blender 4.5, official MakeHuman CC0 base mesh / original weights / 163 bone skeleton
- Actual final GLB SHA256: `037fafca75fd99ac04b195057a3c5a4d2d446455d83922c217376e1f8ad198b6`
- The loop ran on the **true skinned articulated mesh before baking/export**, not rendered 2D deformation.
- Stage script: `ariadne_v125/src/react_top2d_30.py`; full build `ariadne_v125/src/build_v125_react.py`.

## Strict final result

| Criterion | Before | After |
|---|---:|---:|
| 2D authored-top seven-point no-mirror Procrustes RMS | 72.31393 px | 49.44382 px |
| Gold ball position held-out error (not used in similarity fitting) | 51.73555 px | 53.47002 px |
| Actual palmar up vector dot world +Z | 0.91190 | 0.90285 |
| Distinct finger tips within 5mm of fixed sphere | 5 | 4 |
| Deep penetrations (penetration > 3mm) | 0 | 0 |
| Severely compressed L/R forearm edges | 0 / 0 | 0 / 0 |

- Exactly **30 genuine record entries** (round 1–30); 21 accepted and 9 rejected/rolled back.
- Earlier unconstrained 30-round experiment was explicitly **rejected**: despite 72.31→39.99 px it worsened the held-out sphere error to 75.61px and had **24 deep finger penetration vertices**. The revised second loop corrected these fail-open conditions.
- Each accepted change was made with CC0 finger MCP/PIP/DIP joint-local bounded angles. Distinct real pad class tests, palmar/dorsal depth and penetration checks were applied.
- Real GLB reimport passed; user-facing 24 horizontal + 5 high-angle screenshots and 360 1-degree GIF should be rendered from unchanged final GLB hash, not from imagined per-angle meshes.
- Complete 30-round trace available in cloud artifact as `V125_REACT30_TOP2D_ITERATION_LOG.json`.

## Artistic release blockers

**NOT ART APPROVED.** The 2D SVG is an independently authored **provisional** hand guide, not user-approved original V20 top art. Actual top-2D RMS remains ~49.44 px; right-hand art gesture, shoulder/chest garment fold geometry, actual palms/thenar/hypothenar relief and original 24 × 15° >95% art anchors all require further independent artistic review. Procedural mesh-quality metrics are not an artistic similarity score.
