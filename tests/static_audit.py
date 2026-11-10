from pathlib import Path
from bs4 import BeautifulSoup
import json,subprocess,hashlib,sys
import trimesh
ROOT=Path(__file__).resolve().parents[1]; WEB=ROOT/'website'
assert (WEB/'assets/ariadne-relief-3d.glb').stat().st_size>3_000_000
assert (WEB/'assets/ariadne-hero-texture.png').exists()
htmls=list(WEB.glob('*.html'));assert len(htmls)==4,htmls
links=[]
for p in htmls:
 s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 assert s.find('h1'),str(p)
 assert s.find('nav'),str(p)
 for tag in s.find_all(['a','link','script','img']):
  v=tag.get('href') or tag.get('src')
  if not v or v.startswith(('http:','https:','mailto:','data:','#')):continue
  target=(p.parent/v.split('#')[0].split('?')[0]).resolve()
  if not target.exists():links.append((p.name,v))
assert not links,links
# All local JavaScript is syntactically well-formed.
for p in WEB.rglob('*.js'):
 cp=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
 assert cp.returncode==0,(str(p),cp.stderr)
assert len(json.loads((ROOT/'bench/RULE_MATRIX.json').read_text(encoding='utf-8')))==139
# Real 3D GLB, not SVG or a reference to a future download
scene=trimesh.load(WEB/'assets/ariadne-relief-3d.glb',force='scene',process=False)
assert len(scene.geometry)>=20,len(scene.geometry)
assert len(scene.geometry['sculpture_front'].faces)>60_000
assert len(scene.geometry['gold_thread'].faces)>1000
assert len(scene.geometry['gold_orb'].faces)>1000
thickness=float(scene.bounds[1,2]-scene.bounds[0,2]);assert thickness>1.0,thickness
assert scene.geometry['sculpture_front'].visual.material.baseColorTexture is not None
s=BeautifulSoup((WEB/'index.html').read_text(encoding='utf-8'),'html.parser')
assert s.select_one('#ariadneStatue3d .sculpture-viewport')
assert s.select_one('#benchmarkGraph')
assert s.select_one('[data-bench="node_edge"]')
assert (WEB/'js/sculpture-three.js').exists()
assert (WEB/'js/sculpture-native.js').exists()
assert (WEB/'js/playground-graph.js').exists()
pg=BeautifulSoup((WEB/'playground.html').read_text(encoding='utf-8'),'html.parser')
assert pg.select_one('#liveNodeGraph') and len(pg.select('[data-graph-case]'))==5
assert len(s.select('.hero-grid > *'))==2
assert not any(x in (WEB/'index.html').read_text(encoding='utf-8') for x in ('ariadne-fallback.svg','ariadne-statue-model.js'))
print('PASS / 4 public pages / all internal links / JS syntax / 139 syntax cases / 3D GLB meshes / 5 Node–Edge demos / no old fake statue')
print('3D geometry:',len(scene.geometry),'components,',sum(len(x.faces) for x in scene.geometry.values()),'triangles, Z-depth',round(thickness,3))
print('GLB sha256:',hashlib.sha256((WEB/'assets/ariadne-relief-3d.glb').read_bytes()).hexdigest())
