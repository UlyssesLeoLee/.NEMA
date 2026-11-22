#!/usr/bin/env python3
"""Fail-closed design and final-art evidence gates for V86.

This module checks declared provenance and completeness; it cannot determine
whether the sculpt is aesthetically faithful to independent reference art.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config' / 'production.json'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as fp:
        for data in iter(lambda: fp.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def check_design(root=ROOT, cfg=None):
    root = Path(root)
    if cfg is None:
        cfg = json.loads((root / 'config' / 'production.json').read_text('utf8'))
    refs = cfg['reference_sources']
    failures = []
    paths = {}
    for name in ('front_art','turnaround','garment_pattern','garment_design_manifest'):
        p = root / refs[name]
        paths[name] = {'path': str(p.relative_to(root)), 'present': p.is_file(),
                       'sha256': sha256(p) if p.is_file() else None}
        if not p.is_file():
            failures.append(f'MISSING_REQUIRED_DESIGN_INPUT:{name}:{refs[name]}')
    # Validate bytes, not only filenames and operator declarations.
    for key in ('front_art','turnaround'):
        image_file = root/refs[key]
        if image_file.is_file():
            try:
                with Image.open(image_file) as im:
                    if im.width < 256 or im.height < 256:
                        raise ValueError('Reference resolution too low')
                    im.verify()
            except Exception as ex:
                failures.append(f'UNREADABLE_INDEPENDENT_ART:{key}:{ex}')
    pattern_file = root/refs['garment_pattern']
    if pattern_file.is_file():
        with pattern_file.open('rb') as stream:
            if stream.read(7) != b'BLENDER' or pattern_file.stat().st_size < 100_000:
                failures.append('UNREADABLE_OR_PLACEHOLDER_BLEND_PATTERN')
    manifest_path = root / refs['garment_design_manifest']
    manifest = None
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text('utf8'))
            if not isinstance(manifest, dict):
                raise ValueError('manifest must be JSON object')
        except Exception as exc:
            failures.append(f'INVALID_DESIGN_MANIFEST:{exc}')
    if manifest is not None:
        if manifest.get('design_principle') != 'designed_drapery_not_free_hanging_cloth':
            failures.append('WRONG_GARMENT_DESIGN_PRINCIPLE')
        if manifest.get('no_free_drop_base') is not True:
            failures.append('FREE_DROP_BASE_FORBIDDEN')
        required = set(cfg['garment_design']['required_primary_regions'])
        if not required.issubset(set(manifest.get('primary_regions_authored', []))):
            failures.append('PRIMARY_FOLD_REGION_EVIDENCE_MISSING')
        if not set(cfg['simulation']['required_vertex_groups']).issubset(set(manifest.get('required_vertex_groups',[]))):
            failures.append('MANIFEST_INCOMPLETE_PIN_AND_FOLD_GROUPS')
        if manifest.get('garment_object_name') != 'Garment_DesignFirst':
            failures.append('GARBAGE_OR_UNKNOWN_GARMENT_OBJECT')
        if manifest.get('artist_review', {}).get('reviewed') is not True or not manifest.get('artist_review',{}).get('reviewer'):
            failures.append('PRIMARY_GARMENT_ARTIST_REVIEW_REQUIRED')
        for key in ('garment_pattern', 'front_art', 'turnaround'):
            target = paths[key]
            claimed = manifest.get('source_sha256', {}).get(key)
            if not isinstance(claimed, str) or len(claimed) != 64:
                failures.append(f'INVALID_SHA256_DECLARATION:{key}')
            elif target['sha256'] is not None and claimed != target['sha256']:
                failures.append(f'MANIFEST_SOURCE_HASH_MISMATCH:{key}')
        # Evidence drawings must actually exist and be linked by hash.
        evidence = manifest.get('design_evidence', {})
        for name in cfg['garment_design']['required_design_evidence']:
            source = evidence.get(name, {})
            rel = source.get('path') if isinstance(source, dict) else None
            hash_ = source.get('sha256') if isinstance(source,dict) else None
            if not isinstance(rel, str) or not rel.startswith('assets/pattern/') or '..' in Path(rel).parts:
                failures.append(f'MISSING_DESIGN_DRAWING:{name}')
                continue
            p = root/rel
            if not p.is_file():
                failures.append(f'MISSING_DESIGN_DRAWING_FILE:{name}:{rel}')
            elif sha256(p) != hash_:
                failures.append(f'DESIGN_DRAWING_HASH_MISMATCH:{name}')
            else:
                try:
                    if p.suffix.lower() == '.svg':
                        if not ET.parse(p).getroot().tag.endswith('svg'):
                            raise ValueError('not an SVG')
                    elif p.suffix.lower() == '.png':
                        with Image.open(p) as img:
                            img.verify()
                except Exception as ex:
                    failures.append(f'CORRUPT_DESIGN_DRAWING:{name}:{ex}')
        if not isinstance(manifest.get('pattern_revision'),str) or not manifest['pattern_revision']:
            failures.append('PATTERN_REVISION_REQUIRED')
    return {'stage':'design-first-gate','status':'BLOCKED' if failures else 'PASS',
            'art_approved':False,'files':paths,'reasons':failures}


def check_release(root=ROOT, cfg=None):
    root=Path(root)
    if cfg is None:
        cfg = json.loads((root/'config/production.json').read_text('utf8'))
    checked = check_design(root,cfg)
    errors=list(checked['reasons'])
    manifest_path = root / cfg['reference_sources']['approval_manifest']
    measured_path = root/'output'/'per_view_art_metrics.json'
    if not manifest_path.is_file():
        errors.append('MISSING_FINAL_ART_APPROVAL')
    if not measured_path.is_file():
        errors.append('MISSING_24_INDEPENDENT_ART_METRICS')
    if manifest_path.is_file() and measured_path.is_file():
        try:
            a=json.loads(manifest_path.read_text('utf8'))
            data=json.loads(measured_path.read_text('utf8'))
            cam_ids={f'VIEW_{i:03d}' for i in range(0,360,15)}
            actual={v['view_id']:v for v in data['views']}
            if set(actual)!=cam_ids: errors.append('NOT_EXACT_24_ANGLE_METRICS')
            if not (a.get('human_art_approval') is True and a.get('independent_2d_art') is True
                    and a.get('camera_registration_verified') is True and a.get('approved_by')):
                errors.append('ART_APPROVAL_UNVERIFIED')
            if set(a.get('approved_views',[])) != cam_ids: errors.append('NOT_EXACT_24_ANGLE_APPROVALS')
            if any(float(v.get('silhouette_iou',0.)) <= .95 or float(v.get('major_region_score',0.)) <= .95
                   or v.get('independent_art_source_sha256') is None for v in actual.values()):
                errors.append('AN_ANGLE_FAILED_95_PERCENT_THRESHOLD')
        except Exception as exc:
            errors.append('UNREADABLE_FINAL_ART_EVIDENCE:'+str(exc))
    return {'stage':'final-art-gate','status':'BLOCKED' if errors else 'PASS','reasons':errors}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['design','release'],default='design')
    p.add_argument('--strict',action='store_true')
    args=p.parse_args()
    result=check_design() if args.stage=='design' else check_release()
    out=ROOT/'output';out.mkdir(parents=True,exist_ok=True)
    (out/f'{args.stage}_gate_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.strict and result['status']!='PASS':
        sys.exit(2)

if __name__=='__main__':main()
