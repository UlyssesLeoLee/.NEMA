# V147 real 2D→3D rebuild — adversarial review: ART REJECTED

## Proof of engineering execution
- GitHub Actions run [45515724811](https://github.com/UlyssesLeoLee/.NEMA/actions/runs/45515724811): **success**.
- A new skinned GLB exported and reimported, 163 official MakeHuman bones retained.
- **60** legacy unapproved costume / hair / decor objects removed before modeling.
- New unique geometry: 16 sewn white chiton gores, 2 upper crossed white bodice sections, 3 purple sculptural panels, scalp cap, 18 hair-root curves, 9 interwoven braid strands, sphere, gold thread and circular pedestal.
- Hand/orb **nearest anatomical surface tangency** numerical error ~0.00394 m. This is not proof of palm contact.
- Opposite wrist IK target numerical error ~0.000007 m. This does not prove the artist's relaxed-hand pose or plausible shoulder anatomy.
- 10 actual GLB-reimported Blender images.
- Exact user-established art-board image SHA256: `1e5046524ad3d188f58bc09afa117657517f190b9c83664ff0c80fbc27d00f8e`. This image is present in the chat and external deliverable bundle but not committed as full binary in this branch.
- Cropping a previously approved eight-view art board into same-labeled views does **not** establish calibrated per-camera pixel correspondence.
- No genuine completed 2D redraw -> shared 3D edit -> export/reimport -> rerender -> global regression ReAct cycle is claimed.

## Art review from 8 target-vs-GLB side-by-side pairs
Status: **REJECT**.

P0 failures:
1. Face is not the beautiful target sculpture: head approximates an unsculpted cylinder/mask; approved eyes, nose, mouth and Greek profile have not been recreated in authentic topology.
2. Golden orb is floating at the end of a line rather than supported by the fully opened palm and believable fingers; geometric surface tangency is to an unverified skinned surface and misleading if called a palm solution.
3. White skirt still resembles a systematic pleated flared tube, not properly cut and sculpted chiton with target-specific nested folds; procedural gores are physical geometry, but not acceptable couture.
4. Purple himation folds are grossly different from independent art in front, side and back; unrealistic large bulging and unsupported edges; do not compound edit old geometric patches.
5. Long braids still do not match target hairstyle, ears are not appropriately framed, authentic facial sculptural likeness is missing.
6. Gold thread does not follow user-designed front/side/back path, and no certified collision-free outer-body route is available.
7. Top/bottom rendering reveals wrong anatomical scene relationships, non-compliant camera composition and pedestal geometry.
8. Front/side/back camera coordinate system does not have trustworthy pixel-exact calibration to the board, so >95% art scores cannot be measured.

## Required path to release
P00 bit-exact art-board registration -> P01 anatomically plausible 2D 5-view underdrawing -> P02 human-quality face/hair and sewn garments 2D -> P03 24 targets & persistent 256 anatomical/component landmarks -> P04 266 calibrated camera art refs -> P05 genuine corrected high-quality shared sculpture -> P06 30 real SVG re-draw / 3D geometry changes / 2D rerender / global regression per spherical camera (7980 cycles) -> P07 all strict per-angle >95% and user approval.

Truthful accounting at this point:
- **1 substantive 2D-guided geometric reconstruction** (V147 candidate from authored 2D, not an accepted art ReAct cycle).
- **10 true GLB renders**.
- **0/7980 true per-angle 30x ReAct cycles verified**.
- **0 certified per-camera 95% art passes**.
- Formal release remains **BLOCKED**.

Do not redeploy .NEMA website. Do not mark art as complete or merge draft PR as final.
