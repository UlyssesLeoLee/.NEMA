#!/usr/bin/env python3
"""Reuse the verified MakeHuman CC0 download and female morph script from V85.

Geometry provenance means only source validity; it is not sculpture approval.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
script=REPO/'ariadne_v85'/'prepare_cc0.py'
if not script.is_file():
    raise RuntimeError('VERIFIED_MAKEHUMAN_SOURCE_PREPARER_MISSING')
subprocess.run([sys.executable,str(script)],cwd=REPO,check=True)
source=REPO/'ariadne_v85'/'output'
prior=json.loads((source/'source_provenance.json').read_text('utf8'))
if prior.get('status')!='REAL_CC0_SOURCE_NOT_ART_POSE_APPROVAL' or prior.get('morph_modified_vertices',0)<12000:
    raise RuntimeError('FEMALE_CC0_TARGET_PREPARATION_UNVERIFIED')
out=ROOT/'assets'/'base';out.mkdir(parents=True,exist_ok=True)
shutil.copy2(source/'MakeHuman_CC0_female_1p74m.obj',out/'MakeHuman_CC0_female.obj')
prov={'license':'CC0-1.0','source_url':'https://github.com/makehumancommunity/makehuman',
      'female_morph_target_applied':True,'anatomical_pose_art_approved':False,
      'sha256':prior['output_sha256'],'source_assets':prior['source_assets']}
(out/'source_provenance.json').write_text(json.dumps(prov,indent=2)+'\n','utf8')
print('Prepared source-verified MakeHuman female body, not V20 pose-approved')
