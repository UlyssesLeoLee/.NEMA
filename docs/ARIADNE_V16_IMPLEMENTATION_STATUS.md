# Ariadne V16 implementation status

## What is implemented in this branch

- V16 production specification: `spec/Ariadne_V16_Production.yaml`
- Reference manifest: `references/ariadne/reference_manifest.json`
- Fail-closed P02 validator: `scripts/ariadne_v16_reference_gate.py`
- GitHub Actions P02 gate: `.github/workflows/ariadne-v16-production.yml`

## Current verified source state

The repository contains one original front artwork source:

- `website/assets/ariadne-hero-texture.png`

It is recorded as approved front art direction, but it is **not certified as a calibrated orthographic model sheet**.

The repository does not currently contain independently approved right-side or back artwork, the 24 approved angle anchors, or the 256 semantic landmark correspondences.

## Expected reference files

Place independently reviewed artwork in:

- `references/ariadne/front.png`
- `references/ariadne/right_side.png`
- `references/ariadne/back.png`

Then update `reference_manifest.json` with:
- the exact relative path;
- SHA-256;
- `approval_state: APPROVED`;
- `projection: ORTHOGRAPHIC`;
- a source/provenance note.

Do not mirror the front image to create a side or back view. Do not label a generated guess as an approved view.

The 24 anchor SVGs must be separate approved files under `references/ariadne/anchors/`. The 256 landmark registry must contain stable semantic IDs and actual observations or explicit occlusion states.

## Current gate result expected

P02 must remain **BLOCKED** until all three primary views, 24 independently approved anchors, and 256 semantic landmark correspondences are supplied and verified.

No rigging, sculpting, GLB export, or formal release may run while P02 is blocked. This is intentional: the legacy art-draft workflow is not allowed to bypass the V16 reference gate.

## Scope not yet implemented

P05-P16 production workers (full Rigify generation, anatomical pose solving, constrained hand/orb contact, garment pattern/cloth simulation, hair sculpt, multi-view sculpt, UV/PBR, independent GLB validation, and release) are not claimed as implemented by this change. They must be added and tested as real workers before the downstream workflow is unlocked.
