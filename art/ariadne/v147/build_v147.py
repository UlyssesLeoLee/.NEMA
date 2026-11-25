"""V147: rebuild from previously established 2D pose/couture design, not from V145
art meshes. This is a true Blender GLB engineering candidate, NOT an art-approved
2D->3D->2D ReAct iteration without an independently calibrated art image.
"""
import bpy,runpy,math,hashlib,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[3]
runpy.run_path(str(ROOT/"art/ariadne/v144/build_ik.py"),run_name="__main__")
OUT=ROOT/"artifacts"/"ariadne_v147"
OUT.mkdir(parents=True,exist_ok=True)

# V144 has already imported its own real GLB. All unapproved visual geometry
# is removed; only licensed full-round anatomical mesh + official armature remain.
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
candidates=[o for o in meshes if "Anatomy" in o.name or "Anatomy" in o.data.name]
assert len(candidates)==1,[(o.name,len(o.data.vertices)) for o in meshes[-5:]]
body=candidates[0]
rigs=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(rigs)==1
rig=rigs[0]
purged=0
for o in list(bpy.data.objects):
 if o.type in ("MESH","CURVE") and o!=body:
  bpy.data.objects.remove(o,do_unlink=True);purged+=1
assert purged>30, "failed to discard old V140-V145 garment/hair/art geometry"
bpy.context.view_layer.update()
bodycoords=[body.matrix_world@Vector(c) for c in body.bound_box]
cx=(min(p.x for p in bodycoords)+max(p.x for p in bodycoords))/2
cy=(min(p.y for p in bodycoords)+max(p.y for p in bodycoords))/2
base=min(p.z for p in bodycoords)
assert -0.2<base<.2,(base,cx,cy)
def mat(name,color,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 p.inputs["Base Color"].default_value=(*color,1)
 p.inputs["Metallic"].default_value=metal
 p.inputs["Roughness"].default_value=rough
 return m
marble=mat("V147_Pentelic_Ivory",(0.83,.79,.72),0,.55)
amethyst=mat("V147_Royal_Amethyst",(0.22,.09,.29),0,.71)
gold=mat("V147_Embossed_Gold",(0.72,.44,.14),.72,.31)
hair=mat("V147_Sculpted_Ochre_Hair",(0.34,.23,.14),.05,.63)
stone=mat("V147_Carved_Stone",(0.69,.66,.61),0,.71)
body.data.materials.clear();body.data.materials.append(marble)

# Pose authored using the 2D master: raised orb hand, OTHER hand descends at side.
# Preserve official MakeHuman weights; no local fake vertex pulling.
ball_side="L" if (rig.pose.bones.get("wrist.L") and
                   (rig.matrix_world@rig.pose.bones["wrist.L"].tail).x <
                   (rig.matrix_world@rig.pose.bones["wrist.R"].tail).x) else "R"
other_side="R" if ball_side=="L" else "L"
other_wrist=rig.pose.bones.get("wrist."+other_side)
assert other_wrist
# Temporarily add IK to the relaxed wrist, make its world target near side hip.
side_sign=1 if (rig.matrix_world@other_wrist.tail).x>cx else -1
goal=bpy.data.objects.new("V147_Opposite_Relaxed_Palm_2D_Target",None)
bpy.context.scene.collection.objects.link(goal)
goal.location=Vector((cx+side_sign*.24,cy+.04,base+.96))
constraint=other_wrist.constraints.new("IK")
constraint.target=goal;constraint.chain_count=5;constraint.iterations=180
bpy.context.view_layer.update()
# Preserve a constrained armature in export; glTF exporter evaluates skinned pose.
# Do not count this as a 30-cycle ReAct nor claim anatomical fit validated.
relaxed_wrist_error=(rig.matrix_world@other_wrist.tail-goal.location).length

def mesh_obj(name,verts,faces,material,thick=.006,sub=1):
 m=bpy.data.meshes.new(name+"_geometry")
 m.from_pydata(verts,[],faces);m.update()
 obj=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(obj)
 obj.data.materials.append(material)
 for f in obj.data.polygons:f.use_smooth=True
 if thick:
  mod=obj.modifiers.new("FabricTrueThickness","SOLIDIFY");mod.thickness=thick
 if sub:
  mod=obj.modifiers.new("SculptureFolds","SUBSURF");mod.levels=sub
 return obj

def tube(name,points,r,material,closed=False):
 cu=bpy.data.curves.new(name+"_curve","CURVE");cu.dimensions="3D"
 cu.bevel_depth=r;cu.bevel_resolution=3;cu.resolution_u=18
 spline=cu.splines.new("BEZIER")
 spline.bezier_points.add(len(points)-1)
 for p,point in zip(spline.bezier_points,points):
  p.co=point;p.handle_left_type="AUTO";p.handle_right_type="AUTO"
 spline.use_cyclic_u=closed
 obj=bpy.data.objects.new(name,cu)
 bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
 return obj

# Real 3D fitted sculptural chiton cut into 16 sewn gores with non-concentric
# flared silhouette, longitudinal fold valleys and authored asymmetry.
N=16;rows=29;U=11
for panel in range(N):
 v=[];f=[]
 for i in range(rows):
  t=i/(rows-1)
  z=base+1.03-t*.99
  waist=.165
  flare=.33
  r=waist+(flare-waist)*(t**1.22)
  for j in range(U):
   u=j/(U-1)
   th=2*math.pi*(panel+u)/N
   # Broad pleat in each gore, with deeper fold near the hem.
   wave=(.007+.018*t**1.3)*math.sin(2*math.pi*u)
   ridge=(.013+.025*t)*(1-math.cos(2*math.pi*u))/2
   rr=r+wave+ridge+.008*math.cos(th*5+t*3)
   x=cx+rr*math.cos(th)
   y=cy+.72*rr*math.sin(th)
   zz=z+.009*t*math.sin(3*th)
   v.append((x,y,zz))
 for i in range(rows-1):
  for j in range(U-1):
   a=i*U+j;f.append((a,a+1,a+U+1,a+U))
 mesh_obj(f"V147_White_Chiton_CutGore_{panel:02d}",v,f,marble,.006,1)
# White asymmetric shoulder seams and upper bodice.
def panel_mesh(name,waypoints,material,widths,depth_sign=1):
 vertices=[];faces=[]
 U=15
 for i,(px,py,pz) in enumerate(waypoints):
  w=widths[i]
  for j in range(U):
   u=2*j/(U-1)-1
   # Displaced, art-directed large pleats, not flat ribbon.
   depth=.021*math.sin(2.6*math.pi*u+i*.6)+.009*math.sin(6.3*math.pi*u+i*.3)
   vertices.append((px+u*w*.5,py+depth_sign*depth,pz+.008*math.sin(math.pi*u+i*.45)))
 for i in range(len(waypoints)-1):
  for j in range(U-1):
   a=i*U+j;faces.append((a,a+1,a+U+1,a+U))
 o=mesh_obj(name,vertices,faces,material,.009,2)
 return o,vertices

def interpolate(path,count):
 out=[]
 for i in range(count):
  t=i/(count-1)*(len(path)-1)
  k=min(int(t),len(path)-2);u=t-k
  out.append(tuple(a*(1-u)+b*u for a,b in zip(path[k],path[k+1])))
 return out

# Structured white upper chiton, two cloth-over-shoulder diagonals.
white_left=interpolate([
 (cx-.16,cy+.065,base+1.47),(cx-.13,cy+.19,base+1.31),
 (cx+.035,cy+.17,base+1.12),(cx+.01,cy+.145,base+1.02)],17)
white_right=interpolate([
 (cx+.16,cy+.065,base+1.47),(cx+.13,cy+.19,base+1.30),
 (cx-.04,cy+.16,base+1.13),(cx+.01,cy+.145,base+1.02)],17)
panel_mesh("V147_White_Chiton_Crossed_Bodice_Left",white_left,marble,[.14+.12*i/16 for i in range(17)])
panel_mesh("V147_White_Chiton_Crossed_Bodice_Right",white_right,marble,[.14+.12*i/16 for i in range(17)])

# Artist-directed shoulder-supported himation: cross-waist drapery in front,
# back volumetric cloak and distinct overfold, instead of free-floating ribbons.
front_path=interpolate([
 (cx+.14,cy+.08,base+1.45),(cx+.19,cy+.205,base+1.21),
 (cx+.07,cy+.245,base+1.04),(cx-.18,cy+.21,base+.88),
 (cx-.21,cy+.21,base+.62),(cx-.25,cy+.20,base+.16)],34)
front_widths=[.14+.27*math.sin(math.pi*(i/33*.85+.10)) for i in range(34)]
panel_mesh("V147_Amethyst_Himation_Front_ArtFolds",front_path,amethyst,front_widths)
back_path=interpolate([
 (cx+.18,cy-.09,base+1.46),(cx+.25,cy-.21,base+1.20),
 (cx+.10,cy-.26,base+.95),(cx-.06,cy-.29,base+.78),
 (cx-.19,cy-.22,base+.48),(cx-.12,cy-.19,base+.10)],34)
back_widths=[.19+.23*math.sin(math.pi*(i/33*.87+.08)) for i in range(34)]
panel_mesh("V147_Amethyst_Himation_Back_Layered",back_path,amethyst,back_widths,-1)
# Another sculpted waist overfold drapes over the main panel, independent volume.
waist_path=interpolate([
 (cx+.21,cy+.16,base+1.07),(cx+.07,cy+.29,base+.94),
 (cx-.15,cy+.26,base+.85),(cx-.22,cy+.18,base+.76)],22)
panel_mesh("V147_Purple_Waist_Overfold",waist_path,amethyst,[.16+.055*math.sin(math.pi*i/21) for i in range(22)])
# Golden structural trim follows three dimensional fabric edges, not texture.
for name,rows3,widths in [
 ("V147_Gold_Front_Hem",front_path,front_widths),
 ("V147_Gold_Back_Hem",back_path,back_widths)]:
 points=[]
 for (px,py,pz),ww in zip(rows3,widths):
  points.append((px-ww/2,py-.009,pz))
 tube(name,points,.0032,gold)

# Anatomy-preserving hair: rooted scalp cap and multiple actual braids.
hz=base+1.57
capv=[];capf=[]
seg=64;ring=16
for i in range(ring+1):
 phi=i/ring*math.pi*.67
 for j in range(seg):
  t=2*math.pi*j/seg
  capv.append((cx+.105*math.sin(phi)*math.cos(t),
               cy+.090*math.sin(phi)*math.sin(t),
               hz+.118*math.cos(phi)))
for i in range(ring):
 for j in range(seg):
  a=i*seg+j;b=i*seg+(j+1)%seg
  capf.append((a,b,b+seg,a+seg))
mesh_obj("V147_Carved_Hair_Scalp_Cap",capv,capf,hair,.009,1)
# Visible criss-cross braids wrap the skull without ears remaining bald.
for i in range(18):
 theta=2*math.pi*(i+.5)/18
 pts=[]
 for j in range(12):
  t=j/11
  pts.append((cx+.10*math.cos(theta+t*.40),
              cy+.087*math.sin(theta+t*.40),
              hz+.10-.19*t))
 tube(f"V147_Head_Rooted_Lock_{i:02d}",pts,.009,hair)
for i in range(9):
 points=[]
 for j in range(26):
  t=j/25;ang=2*math.pi*(3*t+i/9)
  points.append((cx+.033*math.cos(ang),
                 cy-.105+.022*math.sin(ang),
                 hz-.07-.53*t))
 tube(f"V147_Interlaced_Back_Braid_{i:02d}",points,.0055,hair)
# Crown diadem, art target calls for intricate but no facial texture shortcut.
tube("V147_Crown_Diadem",[
 (cx-.10,cy+.03,hz+.082),(cx-.075,cy+.084,hz+.104),
 (cx,cy+.112,hz+.125),(cx+.075,cy+.084,hz+.104),
 (cx+.10,cy+.03,hz+.082)],.0055,gold)
for i in range(7):
 a=(i-3)/3
 point=(cx+a*.081,cy+.102-.032*abs(a),hz+.12+.024*(1-abs(a)))
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.011,location=point)
 jewel=bpy.context.object;jewel.name=f"V147_Crown_Gold_Jewel_{i:02d}"
 jewel.data.materials.append(gold)

# Gold orb measured against skinned actual palm neighbourhood, not wrist guess.
deps=bpy.context.evaluated_depsgraph_get()
e=body.evaluated_get(deps);me=e.to_mesh()
try:
 points=[e.matrix_world@v.co for v in me.vertices]
 faces=[tuple(p.vertices) for p in me.polygons]
 bvh=BVHTree.FromPolygons(points,faces)
 wrist=rig.pose.bones["wrist."+ball_side]
 w=rig.matrix_world@wrist.tail
 guess=w+Vector((0,.045,.07))
 nearest=bvh.find_nearest(guess,.23)
 assert nearest and nearest[0] is not None
 contact,normal,_,_=nearest
 normal.normalize()
 orb_radius=.063
 orb_pos=contact+normal*orb_radius
 gap=abs((orb_pos-bvh.find_nearest(orb_pos,.24)[0]).length-orb_radius)
 assert gap<.021
finally:
 e.to_mesh_clear()
bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=28,radius=orb_radius,location=orb_pos)
orb=bpy.context.object;orb.name="V147_Golden_Orb_Actual_Sphere";orb.data.materials.append(gold)
bpy.ops.object.shade_smooth()
# 1 continuous gold curve connecting bottom sculpture to actual orb location.
curve=[]
for i in range(83):
 t=i/82;theta=2*math.pi*1.63*t
 r=.30-.05*t
 p=Vector((cx+r*math.cos(theta),cy+r*math.sin(theta),base+.08+1.36*t))
 if t>.88:
  v=(t-.88)/.12
  p=p.lerp(orb_pos,v*v*(3-2*v))
 curve.append(tuple(p))
tube("V147_ONE_Continuous_3D_Gold_Thread",curve,.0037,gold)

# Sculptural round pedestal with real geometry and embossed bands.
def cylinder(name,radius,depth,z,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=(cx,cy,z))
 o=bpy.context.object;o.name=name;o.data.materials.append(material)
 bev=o.modifiers.new("CarvedEdge","BEVEL");bev.width=.005;bev.segments=3
 o.modifiers.new("WeightedNormals","WEIGHTED_NORMAL")
 return o
cylinder("V147_Marble_Round_Base",.36,.082,base-.058,stone)
cylinder("V147_Marble_Plinth_UpperBand",.365,.018,base-.017,stone)
cylinder("V147_Marble_Plinth_LowerBand",.373,.016,base-.101,stone)
for rr,z in [(.363,base-.015),(.368,base-.047),(.370,base-.091)]:
 tube(f"V147_Plinth_Carved_Ring_{z:.3f}",[
 (cx+rr*math.cos(2*math.pi*j/48),cy+rr*math.sin(2*math.pi*j/48),z)
 for j in range(48)],.0037,gold,closed=True)

# Export from actual authored source and reimport to check final GLB render.
glb=OUT/"Ariadne_V147_ArtFirst_Rebuild_Engineering_NOT_APPROVED.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
assert glb.stat().st_size>100000
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
armatures=[o for o in bpy.data.objects if o.type=="ARMATURE"]
assert len(armatures)==1
assert len(armatures[0].data.bones)>=150

scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=5
scene.cycles.use_denoising=False;bpy.context.view_layer.cycles.use_denoising=False
scene.render.resolution_x=640;scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.film_transparent=True
target=Vector((cx,cy,base+.80))
def area(pos,power):
 bpy.ops.object.light_add(type="AREA",location=pos)
 o=bpy.context.object;o.data.energy=power;o.data.size=3.7
 o.rotation_euler=(target-o.location).to_track_quat("-Z","Y").to_euler()
area((cx+3,cy+2,base+4),750);area((cx-3,cy-2,base+3),520)
camera=bpy.data.objects.new("V147_Art_Registered_Orthographic",bpy.data.cameras.new("V147_Camera"))
scene.collection.objects.link(camera);scene.camera=camera
camera.data.type="ORTHO";camera.data.ortho_scale=2.52
# Front is +Y, authoring convention comes from actual art reference.
views=[(a,0) for a in (0,45,90,135,180,225,270,315)]+[(0,90),(0,-90)]
records=[]
for az,el in views:
 a=math.radians(az);e=math.radians(el)
 d=Vector((math.sin(a)*math.cos(e),math.cos(a)*math.cos(e),math.sin(e)))
 camera.location=target+d*4.5
 camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
 path=OUT/f"V147_AZ{az:03d}_EL{el:+04d}.png"
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 records.append({"az":az,"el":el,"image":path.name,
                 "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
source2d=ROOT/"art/ariadne/v147/02d_art_candidate_front_side_back.svg"
report={
 "status":"V147_TRUE_ART_FIRST_REBUILD_CANDIDATE_ART_BLOCKED",
 "new_glb":glb.name,"glb_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
 "source_2d_svg":str(source2d.relative_to(ROOT)),
 "source_2d_sha256":hashlib.sha256(source2d.read_bytes()).hexdigest(),
 "2d_authority":"CANDIDATE_DERIVED_FROM_SELECTED_CONCEPT_BOARD_NOT_PIXEL_APPROVED",
 "legacy_unapproved_art_objects_purged":purged,
 "real_official_cc0_armature_count":len(armatures[0].data.bones),
 "raised_hand_orb_tangency_error_m":gap,
 "relaxed_arm_ik_target_error_m":relaxed_wrist_error,
 "new_white_gore_panels":16,
 "new_white_upper_panels":2,
 "new_purple_volumetric_panels":3,
 "new_rooted_hair_locks":18,
 "new_back_braid_strands":9,
 "new_actual_blender_renders":records,
 "all_266_reference_cameras_registered":False,
 "actual_2d_redraw_3d_modify_react_cycles_completed":0,
 "per_view_strict_gt_95_percent":False,
 "formal_release":False
}
(OUT/"V147_AUDIT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("V147_2D_FIRST_SHARED_GLB_BUILT",json.dumps(report,ensure_ascii=False)[:1500],flush=True)
