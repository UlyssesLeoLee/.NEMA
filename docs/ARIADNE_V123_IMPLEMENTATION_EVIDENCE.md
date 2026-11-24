# Ariadne V123 — V122.2 implementation actual GitHub build (2026-11-24)

Source and CI:
- GitHub Actions: https://github.com/UlyssesLeoLee/.NEMA/actions/runs/45336612851 — SUCCESS.
- Source: ariadne_v123/src/build_complete_v123.py
- Official MakeHuman CC0 model and original weight source recovered from run 45160529755.
- Complete GLB SHA256: 1237706fcbc180ed2eb7a1b1536fc7439d3833c4bf38aabaad33c7be6fc59c55
- V123 full editable Blender source, sculpted costume, gold orb/thread, bun/scarf and pedestal all exported; GLB imported back successfully.

Independent source-mesh bilateral anatomy audit:
- Left forearm: 537 unique edges, p02=0.6882049, p98=1.3592565, severe compression <0.50 count=0.
- Right forearm: 537 unique edges, p02=0.7404518, p98=1.3627894, severe compression <0.50 count=0.
- Left palm upward normal dot world Z = 0.9663194.
- Real skin patch vs locked provisional ball: palmar nearest absolute gap = 0.1035mm.
- Distinct contacting distal finger bones: 4 (thumb, index, middle, ring); little finger NOT contacting.
- Right free arm: independent local joint constrained solve, wrist target error ~70.8mm to provisional IK target, NOT art-authorized.
- Ball source: frozen anatomical support patches, positioned once before finger optimization; V20 reference NOT available, so no false art claim.

Garment and camera audits:
- 7 primary + 4 secondary + 3 tertiary real mesh fold relief paths; continuous torso/waist/skirt garment with separate real fitted belt; waist layer offset <=18.08mm in sampled design.
- Actual GLB rendered externally into 24 horizontal, 5 top/obliques and regional closeup diagnostics.
- Exactly 256 source-bound candidate landmarks, 29-view projected / depth occlusion status; these are NOT 256 approved art correspondences.
- A single unmodified GLB was rendered into 360 1-degree frames; 359-to-0 seam MAD=0.9365, ordinary 0-to-1 MAD=0.9474.

**Release status:** ENGINEERING CANDIDATE ONLY. No independently approved original V20 horizontal 24 or top-family 5 art, no verified per-angle >95% art similarity, no approved right-hand pose, and art-direction/garment refinement remains incomplete. Source and rendering file hashes are preserved inside the user delivery zip.
