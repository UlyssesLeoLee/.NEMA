#!/usr/bin/env python3
"""Fail-closed P02 gate for Ariadne V16.

This script does not invent missing views, mirror the front image, or create fake
landmark coordinates. It audits real source files and emits machine-readable
BLOCKED/PASS evidence for GitHub Actions.
"""
from __future__ import annotations
import hashlib
import json
import os
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ariadne_v16_artifacts"
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST_PATH = ROOT / "references/ariadne/reference_manifest.json"
LANDMARK_PATH = ROOT / "references/ariadne/Landmark_ID_Correspondence.json"
ANCHOR_DIR = ROOT / "references/ariadne/anchors"
REQUIRED_VIEWS = ("front", "right_side", "back")
REQUIRED_LANDMARKS = 256


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def image_dimensions(path: Path) -> tuple[int, int]:
    # PNG header parser: avoids an undeclared imaging dependency in the gate.
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", header[16:24])
    # JPEG/WebP are intentionally not guessed; Pillow can be added if those
    # formats are explicitly admitted to the reference manifest.
    raise ValueError("Only PNG is currently accepted for orthographic source views")


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    issues: list[str] = []
    view_results = {}
    seen_hashes: dict[str, str] = {}

    if manifest is None:
        issues.append("REFERENCE_MANIFEST_MISSING")
        manifest = {"views": {}}

    views = manifest.get("views", {})
    for view in REQUIRED_VIEWS:
        entry = views.get(view)
        if not isinstance(entry, dict) or not entry.get("path"):
            view_results[view] = {"state": "MISSING", "path": None}
            issues.append(f"VIEW_{view.upper()}_MISSING")
            continue
        path = (ROOT / entry["path"]).resolve()
        if ROOT.resolve() not in path.parents and path != ROOT.resolve():
            view_results[view] = {"state": "FAIL", "reason": "PATH_OUTSIDE_REPOSITORY"}
            issues.append(f"VIEW_{view.upper()}_PATH_INVALID")
            continue
        if not path.is_file():
            view_results[view] = {"state": "MISSING", "path": entry["path"]}
            issues.append(f"VIEW_{view.upper()}_FILE_MISSING")
            continue
        try:
            width, height = image_dimensions(path)
        except Exception as exc:
            view_results[view] = {"state": "FAIL", "reason": str(exc)}
            issues.append(f"VIEW_{view.upper()}_IMAGE_INVALID")
            continue
        digest = sha256(path)
        approved = entry.get("approval_state") == "APPROVED"
        projection = entry.get("projection") == "ORTHOGRAPHIC"
        if digest in seen_hashes:
            issues.append(f"VIEW_{view.upper()}_DUPLICATES_{seen_hashes[digest].upper()}_NO_MIRRORING")
        else:
            seen_hashes[digest] = view
        if entry.get("sha256") and entry["sha256"] != digest:
            issues.append(f"VIEW_{view.upper()}_SHA256_MISMATCH")
        if not approved:
            issues.append(f"VIEW_{view.upper()}_NOT_APPROVED")
        if not projection:
            issues.append(f"VIEW_{view.upper()}_NOT_ORTHOGRAPHIC")
        view_results[view] = {
            "state": "PASS" if approved and projection else "PENDING_APPROVAL",
            "path": entry["path"], "sha256": digest,
            "width": width, "height": height,
            "approval_state": entry.get("approval_state"),
            "projection": entry.get("projection"),
        }

    anchors = manifest.get("anchors", [])
    anchor_valid = []
    if len(anchors) != 24:
        issues.append(f"EXPECTED_24_ANCHORS_FOUND_{len(anchors)}")
    for idx, anchor in enumerate(anchors):
        p = ROOT / anchor.get("path", "")
        valid = p.is_file() and anchor.get("approval_state") == "APPROVED"
        anchor_valid.append(valid)
        if not valid:
            issues.append(f"ANCHOR_{idx:02d}_MISSING_OR_NOT_APPROVED")

    landmarks = load_json(LANDMARK_PATH)
    landmark_count = len(landmarks.get("landmarks", [])) if isinstance(landmarks, dict) else 0
    if landmark_count != REQUIRED_LANDMARKS:
        issues.append(f"EXPECTED_256_SEMANTIC_LANDMARKS_FOUND_{landmark_count}")
    else:
        ids = [x.get("id") for x in landmarks["landmarks"]]
        if len(set(ids)) != REQUIRED_LANDMARKS:
            issues.append("LANDMARK_IDS_NOT_UNIQUE")
        for item in landmarks["landmarks"]:
            if not item.get("semantic_name") or not item.get("view_observations"):
                issues.append(f"LANDMARK_{item.get('id')}_MISSING_SEMANTIC_OR_VIEW_OBSERVATION")

    # P02 cannot pass unless all three orthographic references, all approved
    # anchors, and real semantic landmark observations are present.
    hard_missing = any(view_results.get(v, {}).get("state") != "PASS" for v in REQUIRED_VIEWS)
    hard_missing = hard_missing or len(anchors) != 24 or not all(anchor_valid)
    hard_missing = hard_missing or landmark_count != REQUIRED_LANDMARKS
    state = "BLOCKED" if hard_missing or issues else "PASS"

    audit = {
        "pipeline": "Ariadne V16",
        "stage": "P02_THREE_VIEW_ART_MASTER_AND_24_ANGLE_ANCHORS",
        "state": state,
        "reference_policy": "FRONT_RIGHT_SIDE_BACK_REQUIRED_NO_MIRRORING_NO_GUESSING",
        "views": view_results,
        "approved_24_anchor_count": sum(anchor_valid),
        "expected_24_anchor_count": 24,
        "semantic_landmark_count": landmark_count,
        "expected_semantic_landmark_count": REQUIRED_LANDMARKS,
        "issues": sorted(set(issues)),
        "downstream_unlocked": state == "PASS",
        "glb_build_permitted": state == "PASS",
        "note": "A BLOCKED P02 intentionally prevents pose, sculpt, GLB and release stages. Missing views are not synthesized.",
    }
    (OUT / "P02_Reference_Audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Ariadne V16 — P02 Reference Gate",
        "",
        f"**State: {state}**",
        "",
        "## View evidence",
    ]
    for name, result in view_results.items():
        lines.append(f"- {name}: {result.get('state')} — {result.get('path') or 'no source'}")
    lines += [
        "",
        f"- Approved 24-angle anchors: {sum(anchor_valid)}/24",
        f"- Semantic landmarks: {landmark_count}/256",
        "",
        "## Blocking issues",
    ]
    lines.extend([f"- {issue}" for issue in sorted(set(issues))] or ["- None"])
    lines += ["", "No 3D modeling was started unless P02 passed."]
    (OUT / "P02_Reference_Gaps.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as f:
            f.write(f"gate_state={state}\n")
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
