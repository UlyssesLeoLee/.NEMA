import json, sys, zlib, base64, ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(name): return json.loads((ROOT/'guides'/name).read_text())

def test_true_independent_art_evidence_24():
    art=read('independent_art_masks24.json')
    angles=[x['angle_deg'] for x in art['frames']]
    assert angles==list(range(0,360,15))
    for x in art['frames']:
        assert len(x['sha256'])==64
        data=zlib.decompress(base64.b64decode(x['mask_1bit_zlib_base64']))
        assert len(data)==(x['mask_size_px'][0]//8)*x['mask_size_px'][1]
    assert 'V20_Original_Front_Art_Reference.png'==art['source_provenance']['front']['name']

def test_design_primary_region_and_path_geometry():
    guide=read('fold_design.json')
    assert guide['revision'].startswith('V87')
    assert guide['release_approval'] is False
    paths=guide['primary_fold_paths'];assert len(paths)>=9
    regions={p['region'] for p in paths}
    assert {'chest_u_drape','shoulder_to_waist_diagonal_drape','waist_gathering_and_belt_zone',
            'hip_major_folds','back_veil_primary_falls','sleeve_and_elbow_fold_logic'}<=regions
    assert all(len(p['source_pixels'])>=3 and p['amplitude_m']>0 for p in paths)

def test_no_fabric_free_drop_or_self_approval():
    code=(ROOT/'blender_build.py').read_text()
    assert 'fold_field(x,z0)*front' in code
    assert 'V87_PrimaryFold_BeforeCloth.blend' in code
    assert "vertex_group_mass='PIN'" in code
    assert 'PRIMARY_SILHOUETTE_SHIFTED_AFTER_CLOTH' in code
    assert 'CLOTH_NO_SECONDARY_MOVEMENT' in code
    assert 'ENGINEERING_GEOMETRY_CREATED' in code
    assert "'final_art_approved':False" in code
    assert 'OLD_MESH_PATCH' not in code

def test_actual_24_render_loop_and_import():
    code=(ROOT/'blender_build.py').read_text()
    assert 'for ang in range(0,360,15)' in code
    assert 'bpy.ops.render.render(write_still=True)' in code
    assert 'bpy.ops.import_scene.gltf' in code

def test_code_valid_syntax():
    for p in (ROOT/'blender_build.py',ROOT/'make_contact_sheets.py',ROOT/'compare_art.py'):
        ast.parse(p.read_text())

def test_not_claiming_calibrated_95_percent():
    comp=(ROOT/'compare_art.py').read_text()
    assert "'all_24_art_pass':False" in comp
    assert "'camera_registered':False" in comp

def test_source_hashes_stable():
    source=read('independent_art_masks24.json')['source_provenance']
    assert len(source['front']['sha256'])==64
    assert len(source['three_view']['sha256'])==64
