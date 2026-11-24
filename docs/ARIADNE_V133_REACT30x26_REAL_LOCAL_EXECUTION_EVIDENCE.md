# Ariadne V133 — 30 rounds × 26 actual GLB 2D projections

Executed locally on V132's real 240-mesh GLB. User-approved art is ONE full-resolution front hero in a composite, not 26 independent calibrated reference views. **Art approval remains BLOCKED.**

## Verified artifacts (delivered as a local downloadable ZIP)
- The latest final reimported V133 GLB SHA-256: `a9d59c423daa81181b0163813f47802ab903443719830d97ef05cb19069e9b0c`.
- Source V132 GLB SHA-256: `6a5f6db3be76609931ac4eca05cc9eb8062b113b4ba28a5066ee9a485c96e125`.
- **30 actual 3D candidate ReAct iterations, 26 genuine 2D vertex projection diagnostics per iteration: 780 PNGs** (24 × 15° azimuth + top + bottom).
- Accepted / rolled back **12 / 18**; **79** mesh nodes genuinely changed, original MakeHuman body and gold sphere locked, 0 face winding inversions.
- Displacement limits: purple shoulder root **24.664 mm**, max altered geometry vertex **85.101 mm**. Unsafe unconstrained initial attempt was **discarded** and all 30 rounds rerun with the shoulder-root hard gate.
- Front user-art **coarse manually traced** purple edge RMS (approximate camera): **87.67→73.61 px**. This is NOT exact art similarity, not a pixel-perfect claim.
- Hair coarse edge RMS 16.42→15.96 px. Hair design and facial artistry are still insufficient.
- Independently rendered 26 full VTK shaded PNGs from the same final GLB, SHA and actual loaded mesh verified.
- Full inherited cumulative YAML, original approved art, runnable source code, 30 round JSON logs, 780 2D projection images, 26 final shaded renders, before/after GLB and independent validation JSON **are in the ZIP**, not yet committed in binary to GitHub.

### Critical distinction
The 26 per-round 2D views are **real mesh vertex projections**, not independently approved 2D artwork and not full shaded renders. The final 26 images ARE actual shaded GLB renders. Without the artist-approved high-resolution reference views for each angle (especially top) it is impossible to claim independent per-angle >95% pixel-level restoration.

This V133 run is a **local verified build**, not a GitHub Actions job. The companion governance YAML is filed in this branch. **Not a final art-approved sculpture.**
