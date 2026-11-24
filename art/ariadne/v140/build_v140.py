"""V140 actual sculptural geometry iteration using official V139 MakeHuman anatomy.
Engineering candidate: NOT pixel-grade and NOT approved. All additions are real meshes.
"""
import bpy,math,hashlib,json,runpy
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v139/build_cc0_foundation.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v140"
OUT.mkdir(parents=True,exist_ok=True)
body=bpy.data.objects.get("Ariadne_CC0_Female_Anatomy_MASTER")
assert body and body.type=="MESH"
scene=bpy.context.scene

def material(name,color,metallic=0,roughness=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
 m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(*color,1)
 p.inputs["Metallic"].default_value=metallic
 p.inputs["Roughness"].default_value=roughness
 return m
ivory=material("Ivory_Marble",(0.83,.78,.68))
purple=material("Royal_Amethyst_Drapery",(.17,.08,.27))
gold=material("Ancient_Gold",(.72,.40,.09),.72,.28)
hairmat=material("Carved_Bronze_Hair",(.22,.13,.085),.2,.52)
stone=material("Pentelic_Stone",(.58,.54,.5))
body.data.materials.clear();body.data.materials.append(ivory)
# Anchor body/world measurements, model is 1.7m tall.
bounds=[body.matrix_world @ Vector(p) for p in body.bound_box]
cx=(min(p.x for p in bounds)+max(p.x for p in bounds))/2
cy=(min(p.y for p in bounds)+max(p.y for p in bounds))/2
base_z=min(p.z for p in bounds)
top_z=max(p.z for p in bounds)
H=top_z-base_z
assert 1.68<H<1.72

def mesh_obj(name,vertices,faces,mat):
 m=bpy.data.meshes.new(name+"_mesh")
 m.from_pydata(vertices,[],faces);m.update()
 o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 for p in m.polygons:p.use_smooth=True
 return o

def ring_surface(name,mat,rings,radial=96,noise=0,phase=0):
 v=[];f=[]
 for j,(z,rx,ry,dx,dy) in enumerate(rings):
  for k in range(radial):
   t=2*math.pi*k/radial
   pleat=(.011*math.sin(17*t+phase+4*z)+.006*math.sin(31*t+z*6))*(.4+max(0,1.5-z))
   v.append((cx+dx+(rx+pleat)*math.cos(t),cy+dy+(ry+pleat)*math.sin(t),base_z+z+.006*math.sin(9*t+2*z)))
 for j in range(len(rings)-1):
  for k in range(radial):
   a=j*radial+k;b=j*radial+(k+1)%radial
   c=(j+1)*radial+(k+1)%radial;d=(j+1)*radial+k
   f.append((a,b,c,d))
 o=mesh_obj(name,v,f,mat)
 solid=o.modifiers.new("Physical_Textile_Thickness","SOLIDIFY");solid.thickness=.006
 sub=o.modifiers.new("Smooth_Curvature","SUBSURF");sub.levels=1
 return o

# White garment with sculpted skirt expansion; does not replace the anatomical mesh.
ring_surface("Chiton_Sewn_Volume",ivory,[
 (.045,.31,.23,0,0),(.10,.28,.21,0,0),(.24,.265,.20,.015,0),
 (.45,.24,.185,.024,0),(.7,.205,.16,.018,0),(.85,.18,.135,0,0),
 (1.02,.165,.135,0,0),(1.18,.17,.14,0,0),(1.30,.18,.145,0,0)
],phase=.3)

# Royal purple himation is a genuine continuous 3D ribbon over shoulder and hip,
# with varying sectional width and raised folds. Distinct from cylindrical shell.
def cloth_ribbon(name,mat,sections,width_steps=14):
 verts=[];faces=[]
 for i,(c,width,tilt) in enumerate(sections):
  p=Vector(c)
  tangent=Vector(sections[min(i+1,len(sections)-1)][0])-Vector(sections[max(i-1,0)][0])
  tangent.normalize()
  side=tangent.cross(Vector((0,0,1)))
  if side.length<.05:side=Vector((1,0,0))
  side.normalize()
  radial=Vector((0,1,0))
  for j in range(width_steps):
   s=2*j/(width_steps-1)-1
   fold=.018*math.cos(3*math.pi*s+1.4*i)+.009*math.sin(5*math.pi*s+1.1*i)
   q=p+side*s*width/2+radial*(fold+.035*math.sin(tilt)*s)
   verts.append(tuple(q))
 for i in range(len(sections)-1):
  for j in range(width_steps-1):
   a=i*width_steps+j
   faces.append((a,a+1,a+width_steps+1,a+width_steps))
 o=mesh_obj(name,verts,faces,mat)
 m=o.modifiers.new("Hem_Thickness","SOLIDIFY");m.thickness=.009
 m=o.modifiers.new("Subdivision","SUBSURF");m.levels=2
 return o
# An explicitly 3D draped strip with asymmetric shoulder-to-waist route.
cloth_ribbon("Purple_Himation_Sculpted_Panels",purple,[
 ((cx-.19,cy+.055,base_z+1.43),.16,.4),
 ((cx-.15,cy+.155,base_z+1.33),.24,.5),
 ((cx-.03,cy+.195,base_z+1.15),.31,.2),
 ((cx+.19,cy+.17,base_z+.99),.34,-.2),
 ((cx+.18,cy+.16,base_z+.78),.40,.4),
 ((cx+.13,cy+.17,base_z+.57),.43,.8),
 ((cx+.18,cy+.13,base_z+.30),.41,.6),
 ((cx+.20,cy+.10,base_z+.055),.37,.5)
])
# Real back drape cross-body volume, independent of front panels.
cloth_ribbon("Himation_Back_Fold",purple,[
 ((cx-.18,cy-.12,base_z+1.42),.13,.2),
 ((cx-.18,cy-.19,base_z+1.18),.24,.6),
 ((cx+.01,cy-.23,base_z+.92),.39,.9),
 ((cx+.18,cy-.22,base_z+.71),.44,.3),
 ((cx+.17,cy-.16,base_z+.42),.40,.8),
 ((cx+.09,cy-.12,base_z+.06),.33,1)
])

def curve_tube(name,points,mat,bevel=.008,resolution=3):
 cr=bpy.data.curves.new(name,"CURVE");cr.dimensions="3D";cr.resolution_u=18
 sp=cr.splines.new("BEZIER");sp.bezier_points.add(len(points)-1)
 for bp,pos in zip(sp.bezier_points,points):
  bp.co=pos;bp.handle_left_type="AUTO";bp.handle_right_type="AUTO"
 cr.bevel_depth=bevel;cr.bevel_resolution=resolution;cr.resolution_u=18
 o=bpy.data.objects.new(name,cr);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 return o

# Head crown and hair, all volumetric hair tendrils attached to upper skull.
head=Vector((cx,cy,base_z+1.57))
for n in range(16):
 a=2*math.pi*n/16
 x=head.x+.088*math.cos(a);y=head.y+.084*math.sin(a)
 points=[(x,y,head.z+.055),(x*1.0, y-.008,head.z+.01),
         (x+.010*math.sin(a),y-.035,head.z-.07),
         (x+.018*math.sin(a),y-.062,head.z-.19)]
 curve_tube(f"Rooted_Hair_Lock_{n:02d}",points,hairmat,.0075)
# Braids down the rear of the garment, not a flat mapped hairstyle.
for strand in range(3):
 points=[]
 for i in range(22):
  z=base_z+1.55-i*.023
  x=cx+(.036+.015*strand)*math.sin(i*.9+strand*2.094)
  y=cy-.125-.015*strand-.015*math.cos(i*.9+strand*2.094)
  points.append((x,y,z))
 curve_tube(f"Interwoven_Back_Braid_{strand}",points,hairmat,.012)
curve_tube("Crown_Gold_Diadem",[
 (cx-.10,cy+.015,base_z+1.64),(cx-.07,cy+.085,base_z+1.675),
 (cx,cy+.106,base_z+1.692),(cx+.07,cy+.085,base_z+1.675),
 (cx+.10,cy+.015,base_z+1.64)],gold,.008)

def uv_sphere(name,loc,radius,mat,segments=48,rings=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=radius,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for poly in o.data.polygons:poly.use_smooth=True
 return o

# Gold sphere and one spatial gold thread. Hand contact is NOT YET anatomically verified.
orb=Vector((cx-.46,cy+.04,base_z+1.43))
uv_sphere("Golden_Orb_Real_Sphere",orb,.062,gold)
thread=[]
for i in range(40):
 t=i/39
 ang=2*math.pi*1.65*t
 radius=.30-.14*t
 z=base_z+.10+1.28*t
 thread.append((cx+radius*math.cos(ang),cy+radius*math.sin(ang),z))
thread.extend([tuple(orb+Vector((-.04,0,-.03))),tuple(orb)])
curve_tube("One_Continuous_Golden_Thread",thread,gold,.0035)

# Marble base, separate rings and detail (all real volume).
def cylinder(name,z,rad,depth,mat,vertices=96):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=rad,depth=depth,location=(cx,cy,z))
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 be=o.modifiers.new("Carved_Stone_Edge","BEVEL");be.width=.012;be.segments=3
 o.modifiers.new("Weighted_Normals","WEIGHTED_NORMAL")
 return o
cylinder("Pedestal_Plinth",base_z-.057,.37,.11,stone)
cylinder("Pedestal_Carved_Border",base_z-.105,.395,.022,ivory)
cylinder("Pedestal_Upper_Border",base_z-.005,.365,.018,ivory)

# Render the same shared scene from eight cardinal and two pole viewpoints.
outglb=OUT/"Ariadne_V140_REAL_3D_Sculpture_Candidate_NOT_ART_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(outglb),export_format="GLB",export_cameras=False,export_lights=False)
assert outglb.stat().st_size>100000
camera=scene.camera
camera.data.ortho_scale=2.75
scene.render.resolution_x=640;scene.render.resolution_y=840
scene.cycles.samples=10
camera_target=Vector((cx,cy,base_z+.86))
views=[(0,0),(45,0),(90,0),(135,0),(180,0),(225,0),(270,0),(315,0),(0,90),(0,-90)]
records=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 d=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 camera.location=camera_target+d*4.4
 camera.rotation_euler=(camera_target-camera.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V140_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 records.append({"az":az,"el":el,"path":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
summary={
 "stage":"SCULPTURE_GEOMETRY_ITERATION_NOT_FINAL",
 "source":"V139 official CC0 body geometry rebuilt in same process",
 "source_body_mesh":len(body.data.vertices),
 "new_volumetric_nodes":[o.name for o in scene.objects if o.type in ("MESH","CURVE") and o!=body],
 "glb_sha256":hashlib.sha256(outglb.read_bytes()).hexdigest(),
 "rendered_views":records,
 "art_95_percent_verified":False,
 "formal_user_approval":False,
 "blocked":["target arm pose not rig-validated","gold orb palmar contact not verified","garment tailoring and seam fidelity incomplete","face likeness not sculpted","hair artistry unapproved","266-view similarity has no independent truth"],
 "status":"ENGINEERING_CANDIDATE_ONLY"
}
(OUT/"V140_AUDIT.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print("V140_EXPORT_SUCCESS",outglb,flush=True)
