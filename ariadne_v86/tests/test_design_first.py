"""Offline tests of fail-closed V86 asset and renderer policies."""
import json
import sys
import shutil
from pathlib import Path

import pytest
import yaml
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gates import check_design,check_release,sha256


def config():
    return json.loads((ROOT/'config/production.json').read_text('utf8'))


def fixture(tmp_path):
    c=config()
    (tmp_path/'config').mkdir(parents=True)
    (tmp_path/'config/production.json').write_text(json.dumps(c),'utf8')
    for k in ('front_art','turnaround'):
        p=tmp_path/c['reference_sources'][k]
        p.parent.mkdir(parents=True,exist_ok=True)
        Image.new('RGB',(512,768),'white').save(p)
    pattern=tmp_path/c['reference_sources']['garment_pattern']
    pattern.parent.mkdir(parents=True,exist_ok=True)
    # A fixture is not a real Blender file; real Blender reopens it in pipeline.
    pattern.write_bytes(b'BLENDER'+b'\0'*110_000)
    drawings={}
    for name in c['garment_design']['required_design_evidence']:
        p=tmp_path/'assets/pattern'/name
        if p.suffix=='.png':
            Image.new('RGB',(512,512),'white').save(p)
        else:
            p.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50"><path d="M0 0 L20 20"/></svg>','utf8')
        drawings[name]={'path':str(p.relative_to(tmp_path)),'sha256':sha256(p)}
    man={
        'design_principle':'designed_drapery_not_free_hanging_cloth',
        'no_free_drop_base':True,
        'garment_object_name':'Garment_DesignFirst',
        'pattern_revision':'TEST_FIXTURE_ONLY',
        'artist_review':{'reviewed':True,'reviewer':'UNIT_TEST_ONLY'},
        'primary_regions_authored':c['garment_design']['required_primary_regions'],
        'required_vertex_groups':c['simulation']['required_vertex_groups'],
        'source_sha256':{key:sha256(tmp_path/c['reference_sources'][key]) for key in ('garment_pattern','front_art','turnaround')},
        'design_evidence':drawings
    }
    mf=tmp_path/c['reference_sources']['garment_design_manifest']
    mf.write_text(json.dumps(man),'utf8')
    return c,man,mf


def test_missing_design_sources_fail_closed(tmp_path):
    assert check_design(tmp_path, config())['status']=='BLOCKED'
    assert any('MISSING_REQUIRED_DESIGN_INPUT:garment_pattern:' in v for v in check_design(tmp_path,config())['reasons'])


def test_valid_manifest_passes_only_preliminary_design_gate(tmp_path):
    c,_,_=fixture(tmp_path)
    assert check_design(tmp_path,c)['status']=='PASS'
    # Final art still blocked absent independent art proof.
    assert check_release(tmp_path,c)['status']=='BLOCKED'


def test_mismatch_source_hash_fails(tmp_path):
    c,m,mf=fixture(tmp_path)
    m['source_sha256']['garment_pattern']='0'*64
    mf.write_text(json.dumps(m),'utf8')
    assert 'MANIFEST_SOURCE_HASH_MISMATCH:garment_pattern' in check_design(tmp_path,c)['reasons']


def test_unsigned_or_unreviewed_fold_fails(tmp_path):
    c,m,mf=fixture(tmp_path)
    m['artist_review']['reviewed']=False
    mf.write_text(json.dumps(m),'utf8')
    assert 'PRIMARY_GARMENT_ARTIST_REVIEW_REQUIRED' in check_design(tmp_path,c)['reasons']


def test_fold_area_or_pin_group_missing_fails(tmp_path):
    c,m,mf=fixture(tmp_path)
    m['primary_regions_authored']=['hip_major_folds']
    m['required_vertex_groups']=['PIN']
    mf.write_text(json.dumps(m),'utf8')
    reasons=check_design(tmp_path,c)['reasons']
    assert 'PRIMARY_FOLD_REGION_EVIDENCE_MISSING' in reasons
    assert 'MANIFEST_INCOMPLETE_PIN_AND_FOLD_GROUPS' in reasons


def test_corrupted_evidence_fails(tmp_path):
    c,m,mf=fixture(tmp_path)
    p=tmp_path/'assets/pattern/fold_flow_map.svg'
    p.write_text('<svg>INVALID','utf8')
    m['design_evidence']['fold_flow_map.svg']['sha256']=sha256(p)
    mf.write_text(json.dumps(m),'utf8')
    assert any(x.startswith('CORRUPT_DESIGN_DRAWING:fold_flow_map.svg:') for x in check_design(tmp_path,c)['reasons'])


def test_free_drop_design_fails(tmp_path):
    c,m,mf=fixture(tmp_path)
    m['no_free_drop_base']=False
    mf.write_text(json.dumps(m),'utf8')
    assert 'FREE_DROP_BASE_FORBIDDEN' in check_design(tmp_path,c)['reasons']


def test_no_art_release_with_fabricated_high_mean_score(tmp_path):
    c,m,mf=fixture(tmp_path)
    approved=tmp_path/c['reference_sources']['approval_manifest']
    approved.write_text(json.dumps({'human_art_approval':True,'independent_2d_art':True,'camera_registration_verified':True,
                                    'approved_by':'TEST','approved_views':[f'VIEW_{x:03d}' for x in range(0,360,15)]}))
    o=tmp_path/'output';o.mkdir()
    views=[{'view_id':f'VIEW_{x:03d}','silhouette_iou':.999,'major_region_score':.999,
            'independent_art_source_sha256':'3'*64} for x in range(0,360,15)]
    views[7]['silhouette_iou']=.94
    (o/'per_view_art_metrics.json').write_text(json.dumps({'views':views}))
    assert 'AN_ANGLE_FAILED_95_PERCENT_THRESHOLD' in check_release(tmp_path,c)['reasons']


def test_blender_script_real_pins_and_no_default_tube():
    t=(ROOT/'src/blender_build.py').read_text('utf8')
    assert 'PRIMARY_DESIGN_VERTEX_NOT_ACTUALLY_PINNED' in t
    assert 'PRIMARY_FOLD_LOCAL_DRIFT_TOO_HIGH' in t
    assert "m.settings.vertex_group_mass='PIN'" in t
    assert 'def dress(' not in t
    assert 'def himation(' not in t
    import ast
    ast.parse(t)


def test_workflow_not_permanently_skipped_or_masked():
    t=(ROOT.parent/'.github/workflows/ariadne_v86_design_first.yml').read_text('utf8')
    y=yaml.safe_load(t)
    assert {'policy-tests','design-input-gate','blender-design-first','optional-independent-art-release-check'} <= set(y['jobs'])
    assert 'if: false' not in t
    assert '|| true' not in t
    assert '--stage design --strict' in t
    for cmd in ('graybox','simulate','render','reimport'):
        assert f'-- {cmd}' in t
    assert 'ariadne_v85/blender_model.py' not in t
    assert 'if: always()' in t


def test_no_missing_modules():
    import py_compile
    for path in (ROOT/'src').glob('*.py'):
        py_compile.compile(str(path), doraise=True)
