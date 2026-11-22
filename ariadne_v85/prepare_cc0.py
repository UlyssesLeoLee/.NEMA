#!/usr/bin/env python3
"""Prepare an anatomically real, provenance-locked MakeHuman CC0 female mesh."""
from pathlib import Path
import hashlib, json, urllib.request

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)
BASE = "https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj"
FEMALE = "https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/targets/macrodetails/caucasian-female-young.target"
SOURCES = [
    ("base.obj", BASE, "d26635e9326e3cca30778fd7b9c00062b03cce09"),
    ("caucasian-female-young.target", FEMALE, "9d1f0cbeedc9a6a51abe33f1ebb5fa7c5a7edbf1"),
]

def download(name, url, expected_git_sha):
    destination = OUT / name
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"NEMA-Ariadne-CC0-Builder"}), timeout=150) as response:
        data = response.read()
    actual = hashlib.sha1(("blob " + str(len(data)) + "\0").encode() + data).hexdigest()
    if actual != expected_git_sha:
        raise RuntimeError(f"UPSTREAM_BLOB_MISMATCH {name} expected={expected_git_sha} actual={actual}")
    if b"CC0" not in data[:2000]:
        raise RuntimeError(f"UPSTREAM_CC0_LICENSE_NOT_IN_SOURCE_HEADER {name}")
    destination.write_bytes(data)
    return {"name":name,"url":url,"github_blob_sha":actual,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}

def main():
    evidence = [download(*asset) for asset in SOURCES]
    base_data = (OUT/"base.obj").read_text().splitlines()
    verts = []
    faces = []
    for line in base_data:
        if line.startswith("v "):
            verts.append([float(v) for v in line.split()[1:4]])
        elif line.startswith("f "):
            faces.append([int(item.split("/")[0]) for item in line.split()[1:]])
    if len(verts) < 15000 or len(faces) < 10000:
        raise RuntimeError(f"WRONG_BODY_TOPOLOGY vertices={len(verts)} faces={len(faces)}")
    changed = 0
    for line in (OUT/"caucasian-female-young.target").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 4:
            raise RuntimeError("MALFORMED_FEMALE_MORPH_TARGET")
        i = int(parts[0])
        if i < 0 or i >= len(verts):
            raise RuntimeError("MORPH_VERTEX_ID_OUT_OF_RANGE")
        for j in range(3):
            verts[i][j] += float(parts[j+1])
        changed += 1
    if changed < 12000:
        raise RuntimeError("FEMALE_MORPH_TOO_FEW_VERTICES")
    # Official MakeHuman OBJ uses Y as world up, Z as its depth axis.
    # Explicitly transform to Blender Z-up before mesh construction.
    points = [[v[0], -v[2], v[1]] for v in verts]
    z0 = min(p[2] for p in points)
    height = max(p[2] for p in points) - z0
    if not 10.0 < height < 25.0:
        raise RuntimeError(f"MAKEHUMAN_UNIT_CONVENTION_UNEXPECTED height={height}")
    s = 1.74/height
    xc = (min(p[0] for p in points)+max(p[0] for p in points))/2
    yc = (min(p[1] for p in points)+max(p[1] for p in points))/2
    mesh = OUT/"MakeHuman_CC0_female_1p74m.obj"
    with mesh.open("w", encoding="utf8") as f:
        f.write("# Derived from official MakeHuman CC0 base + caucasian-female-young target\n")
        f.write("o MakeHuman_Female_RealTopology\n")
        for x,y,z in points:
            f.write("v %.7f %.7f %.7f\n"%((x-xc)*s,(y-yc)*s,(z-z0)*s))
        for face in faces:
            f.write("f "+" ".join(str(i) for i in face)+"\n")
    summary = {
        "asset_license":"CC0-1.0",
        "license_basis":"Official MakeHuman core mesh and macro target, explicit CC0 file headers",
        "status":"REAL_CC0_SOURCE_NOT_ART_POSE_APPROVAL",
        "source_assets":evidence,
        "base_vertices":len(verts),"faces":len(faces),"morph_modified_vertices":changed,
        "unit_conversion":{"source":"MakeHuman Y-up, source units","target":"Blender Z-up, meters","height_m":1.74},
        "output_sha256":hashlib.sha256(mesh.read_bytes()).hexdigest()
    }
    (OUT/"source_provenance.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
