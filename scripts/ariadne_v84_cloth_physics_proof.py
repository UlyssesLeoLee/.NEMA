"""Blender headless real cloth solve on MakeHuman CC0 body.
This is an Actions RUNTIME proof, not the V84 garment artistic solve.
"""
import bpy, math, json, pathlib, os, urllib.request
ROOT=pathlib.Path(os.environ.get("GITHUB_WORKSPACE", "."))
OUT=ROOT/"ariadne_v84_cloth_smoke_artifacts";OUT.mkdir(exist_ok=True)
SRC="https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
def get(name,source):
 p=OUT/name
 if not p.exists():urllib.request.urlretrieve(SRC+source,str(p))
 assert p.stat().st_size>100000
 return p
base=get("base.obj","3dobjs/base.obj")
female=get("female.target","targets/macrodetails/caucasian-female-young.target")
vs=[];fs=[];group=""
for line in base.open():
 if line.startswith("v "):
  x,y,z=map(float,line.split()[1:4]);vs.append([x/10.,-z/10.,y/10.])
 elif line.startswith("g "):group=line.strip()[2:]
 elif line.startswith("f ") and group=="body":fs.append([int(q.split("/")[0])-1 for q in line.split()[1:]])
for line in female.open():
 a=line.split()
 if len(a)==4 and a[0].isdigit():
  i=int(a[0]);dx,dy,dz=map(float,a[1:]);vs[i][0]+=dx/10.;vs[i][1]-=dz/10.;vs[i][2]+=dy/10.
z0=min(q[2] for q in vs[:13380])
for q in vs:q[2]-=z0
assert len(fs)==13378
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
m=bpy.data.meshes.new("MakeHuman_CC0_Collider");m.from_pydata(vs,[],fs);m.update()
body=bpy.data.objects.new("MakeHuman_CC0_Collider",m);bpy.context.collection.objects.link(body)
collision=body.modifiers.new("BodyCollision","COLLISION");collision.settings.thickness_outer=.006
cloth=[]
def panel(name,nx,ny,width,top,height,front,widen=0):
 verts=[];faces=[]
 for j in range(ny+1):
  v=j/ny
  for i in range(nx+1):
   u=i/nx
   verts.append(((u-.5)*(width+widen*v),front+.012*math.sin(u*math.tau)*v,top-v*height+.01*math.cos(u*math.tau)*v))
 for j in range(ny):
  for i in range(nx):
   k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 vg=ob.vertex_groups.new(name="PIN_SEAM");vg.add(list(range(nx+1)),1.0,"REPLACE")
 cm=ob.modifiers.new("RealClothSimulation","CLOTH")
 cm.settings.quality=5;cm.settings.mass=.25;cm.settings.vertex_group_mass=vg.name
 cm.collision_settings.use_collision=True;cm.collision_settings.distance_min=.005
 cm.collision_settings.use_self_collision=True;cm.collision_settings.self_distance_min=.006
 cm.point_cache.frame_start=1;cm.point_cache.frame_end=48
 cloth.append(ob)
panel("PROOF_CONTINUOUS_U_BODICE",24,24,.52,1.37,.43,-.28)
panel("PROOF_BACK_VEIL",24,40,.45,1.62,.89,.31,.16)
panel("PROOF_HIP_DRAPE",24,24,.55,1.04,.45,-.35)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=48
for frame in range(1,49):
 scene.frame_set(frame)
 if frame%12==0:print("SIMULATED_FRAME",frame,flush=True)
deps=bpy.context.evaluated_depsgraph_get()
report={"type":"REAL_BLENDER_CLOTH_ENGINE_PROOF","status":"NOT_ART_APPROVED","frame_count":48,"cloth":{}}
for ob in cloth:
 ev=ob.evaluated_get(deps);em=ev.to_mesh()
 original=[tuple(v.co) for v in ob.data.vertices];current=[tuple(v.co) for v in em.vertices]
 assert len(original)==len(current)
 movement=[math.dist(a,b) for a,b in zip(original,current)]
 assert max(movement)>.0001,(ob.name,max(movement))
 mesh=bpy.data.meshes.new(ob.name+"_FinalFrozen")
 mesh.from_pydata(current,[],[tuple(p.vertices) for p in ob.data.polygons]);mesh.update()
 final=bpy.data.objects.new(ob.name+"_SIMULATED_FINAL",mesh);bpy.context.collection.objects.link(final)
 report["cloth"][ob.name]={"max_motion_m":max(movement),"mean_motion_m":sum(movement)/len(movement),"vertex_count":len(current)}
 ev.to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Cloth_Editable_DIAGNOSTIC.blend"))
bpy.ops.object.select_all(action="DESELECT")
for ob in bpy.context.scene.objects:
 if ob==body or ob.name.endswith("_SIMULATED_FINAL"):ob.select_set(True)
glb=OUT/"V84_Cloth_Solver_Proof_Not_Art.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True)
report["glb_bytes"]=glb.stat().st_size
(OUT/"Actual_Physics_Audit.json").write_text(json.dumps(report,indent=2))
print("REAL_CLOTH_SOLVER_PROOF",json.dumps(report),flush=True)
