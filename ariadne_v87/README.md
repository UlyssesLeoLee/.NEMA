# NEMA Ariadne V87 — Art-reference recovered, authored garments first

The original V20 front and three-view references and historical 24-angle artwork frames were recovered from the user's .NEMA file Library. Their source SHA-256 values, authored fold paths and 24 independent-art-derived silhouettes are recorded in `guides/`.

## Scope

This repo contains a new Blender engineering garment study built from an actual MakeHuman female body, with a **primary 3D garment fold relief defined before any cloth solver**. Structural layers are separate only when physically justified. Small hem motion can use constrained simulation. The job outputs GLB, editable .blend and actual render screenshots.

This is **not** final and may be visibly inferior to the original art; full V20 source images and human approval are still needed for the release gate. Recovered artwork masks are diagnostic evidence and cannot be treated as 95% final similarity proof without camera registration.

Use GitHub Actions `.github/workflows/ariadne_v87_rebuild.yml` on branch `ariadne_v86_design_first`.

Sources: official MakeHuman CC0 original mesh and young-female macro target, pinned blob hashes in `ariadne_v85/prepare_cc0.py`.
