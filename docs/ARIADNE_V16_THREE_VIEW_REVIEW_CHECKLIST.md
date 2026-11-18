# Ariadne V16 — Three-View Reference Review Checklist

**State:** DRAFT / NOT APPROVED  
**Purpose:** Review the right-side and rear concept against the accepted front artwork before any geometry is inferred from them.

## 1. Reference-sheet invariants

- [ ] Front, right-side and back are true orthographic views, not perspective or 3/4 views.
- [ ] All views use the same model scale, ground line, vertical axis and pedestal height.
- [ ] Camera elevation is level and identical; no view has a tilted horizon.
- [ ] Left/right identity is explicitly labelled and consistent.
- [ ] Entire sculpture, orb, thread, yarn ball and pedestal remain inside frame.
- [ ] No missing or occluded anatomical region is silently mirrored from another view.
- [ ] Each source file has provenance, SHA-256, approval state and projection declaration.

## 2. Right-side profile review

- [ ] Forehead, nose bridge, nose tip, lips, chin and jaw profile agree with the accepted front artwork.
- [ ] Ear placement, skull volume, hairline, braid and rear chignon are anatomically plausible.
- [ ] Neck transitions naturally into clavicle, shoulder and thorax.
- [ ] Rib cage, breast/chest contour, abdomen, pelvis and gluteal profile remain anatomically coherent.
- [ ] Raised shoulder, upper arm, elbow, forearm, wrist and palm form a plausible continuous limb.
- [ ] Thumb opposition and finger curvature support the orb; the orb is not merely near the hand.
- [ ] Weight-bearing leg, knee, ankle and foot align with the pedestal.
- [ ] Chiton and himation folds have believable gravity, attachment and thickness.
- [ ] Golden cord has a traceable continuous spatial route and does not cut through the body.

## 3. Back-view review

- [ ] Rear skull, braid arrangement and chignon volume are fully sculpted.
- [ ] Neck, trapezius, shoulder blades, spine, rib cage and pelvis form a plausible posterior anatomy.
- [ ] Raised-arm scapular rotation and shoulder transition are credible.
- [ ] Elbow, forearm, wrist and hand orientation remain consistent with the orb grip.
- [ ] Back drapery has real attachment points, gravity-driven folds and a readable hem.
- [ ] The posterior legs and feet have complete geometry, not a flat or mirrored closure.
- [ ] Golden cord remains continuous and does not float or intersect the sculpture.
- [ ] Rear silhouette preserves the approved K-shaped composition without anatomical distortion.

## 4. Composition and artistic review

- [ ] The vertical body axis and upper/lower diagonal gestures read as one graceful K-shaped composition.
- [ ] The golden orb, raised arm, opposite arm, drapery and thread form a coherent visual rhythm.
- [ ] Golden-ratio guides are used as soft composition aids only; human anatomy takes precedence.
- [ ] Sculpture remains a classical ivory-stone figure with restrained gold accents.
- [ ] No new ornament, garment panel or pose gesture is introduced without review against the accepted front artwork.

## 5. Landmark and anchor registration

- [ ] 256 persistent semantic IDs remain stable; no ID is reassigned between revisions.
- [ ] Each landmark has an observation in front, right-side and back views.
- [ ] Every view observation is either VISIBLE (normalized image coordinates, confidence, source SHA-256) or OCCLUDED (explicit reason and source SHA-256).
- [ ] The 24 separate 15-degree SVG anchors are individually reviewed and approved.
- [ ] Unknown geometry remains UNKNOWN; no guessed coordinates are promoted to truth.

## 6. Approval record

| View / item | Reviewer decision | Notes |
|---|---|---|
| Front | PENDING | |
| Right side | PENDING | |
| Back | PENDING | |
| 24-angle anchors | PENDING | |
| 256 landmark correspondence | PENDING | |
| Overall art lock | PENDING | |

**Approval rule:** P02 remains BLOCKED until the three orthographic views and all required landmark/anchor evidence pass. This checklist does not itself approve the generated concept image.

## 7. Required 24-angle SVG anchor manifest fields

Each anchor entry must provide:
- `path`: repository-relative SVG path;
- `angle_degrees`: exact sequence 0, 15, 30, …, 345;
- `sha256`: exact SHA-256 of the SVG bytes;
- `approval_state: APPROVED`;
- `projection: ORTHOGRAPHIC`.

Each SVG must parse successfully and contain a valid `viewBox`. The P02 gate verifies all of these fields and the file hash; merely creating 24 filenames is not sufficient.
