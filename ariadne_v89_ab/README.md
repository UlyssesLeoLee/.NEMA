# .NEMA Ariadne V89 — A/B tested YAML

**Single full source of truth:** `NEMA_Ariadne_V89_AB_Optimized_Master.yaml`.

This work compares **A = immutable V88** against **B = V89** on the same real V87.1 engineering GLB. The first-stage A/B measures source GLB pose capability and hand-region sphere proximity, checks GLB thread-export rules, checks independent art hashes and tests fail-closed art approval rules. It is *not* a 24-angle final sculpture-quality A/B, and it did not create a corrected model.

## Run complete local A/B

```bash
python -m pip install numpy scipy trimesh PyYAML pytest
python src/ab_benchmark.py
python -m pytest -q tests/test_ab_real_source.py
```

Artifacts are written to `report/AB_Results.json`, `report/AB_Cases.csv` and `report/AB_Adversarial_Audit.md`.

## GitHub subset

The GitHub Actions workflow `ariadne_v89_ab.yml` downloads **the exact V87.1 GLB** (pinned SHA256) from prior run #45062111861, and independently runs `src/github_smoke.py`. It rechecks real geometry and reports an explicit *engineering-only* pass; it does **not** have access to the full private art images or certified 256 landmark/rig annotations. Those are only in the full local ZIP.

## Decision

- Use **V89 YAML (B)** for the next actual Blender iteration: capability scan and valid rig binding first; sphere after anatomical palm pose; thread 3D clearance, convert to mesh before GLB export, mandatory roundtrip; 24 independent art angles strict >0.95 each and artist approval.
- Do **not** call V89 a final GLB or claim it wins visual quality. The input V87.1 GLB has **no skin** and still needs a correct rig and pose.
