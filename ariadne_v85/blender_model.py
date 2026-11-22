#!/usr/bin/env python3
"""V85 real MakeHuman female mesh + genuine Blender cloth solver, engineering NOT_ART.

This cannot score 2D similarity because V20 original art was not provided. Never
promote the exported GLB to the final Ariadne statue without 24 art approvals.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
R24 = OUT / "render_24"
R24.mkdir(exist_ok=True)

def clamp01(x): return max(0., min(1., x))
def smooth(a,b,x):
    t=clamp01((x-a)/(b-a))
    return t*t*(3-2*t)

def mesh_obj(name, verts, faces):
    me=bpy.data.meshes.new(name+"_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    for poly in me.polygons: poly.use_smooth=True
    return ob

def mat(name,rgba,metallic=0,rough=.58):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgba,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*rgba,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    return m

stone=cloth_m=gold=hair_m=None
def setmat(ob, m): ob.data.materials.clear();ob.data.materials.append(m)

def load_body():
    p=OUT/"MakeHuman_CC0_female_1p74m.obj"
    if not p.is_file(): raise RuntimeError("REAL_MAKEHUMAN_ASSET_REQUIRED")
    verts=[];faces=[]
    for line in p.read_text().splitlines():
        if line.startswith("v "):
            verts.append([float(a) for a in line.split()[1:4]])
        if line.startswith("f "):
            faces.append([int(a)-1 for a in line.split()[1:]])
    if len(verts)<15000 or len(faces)<10000:
        raise RuntimeError("INVALID_ANATOMICAL_BASE_MESH")
    # Whole anatomical mesh preserved; do not construct an approximation from cylinders.
    # The next stage is engineering pose exploration, NOT approved artistic fitting.
    for p in verts:
        x,y,z=p
        if x>.19 and z>1.05:
            w=smooth(.19,.35,x)*smooth(1.05,1.23,z)
            a=.28*w
            dx=x-.205; dz=z-1.38
            nx=.205+math.cos(a)*dx-math.sin(a)*dz
            nz=1.38+math.sin(a)*dx+math.cos(a)*dz
            p[0]=nx;p[2]=nz
        elif x<-.19 and z>1.05:
            w=smooth(.19,.34,-x)*smooth(1.05,1.23,z)
            a=-.20*w
            dx=x+.205;dz=z-1.38
            p[0]=-.205+math.cos(a)*dx-math.sin(a)*dz
            p[2]=1.38+math.sin(a)*dx+math.cos(a)*dz
    body=mesh_obj("Human_CC0_Female_OriginalTopology_PoseStudy",verts,faces)
    setmat(body,stone)
    collision=body.modifiers.new("Body_Collision","COLLISION")
    collision.settings.thickness_outer=.009
    return body

def dress():
    # One physically connected chiton pattern. Pleats deform its own surface,
    # not stacked fake panels added to hide silhouette errors.
    N=72; M=62; vv=[];ff=[]
    for j in range(M):
        t=j/(M-1)
        z=.09+1.19*t
        if z<.48: r=.445-(z-.09)*.25
        elif z<.89:r=.347-(z-.48)*.20
        elif z<1.10:r=.265-(z-.89)*.21
        elif z<1.32:r=.221+(z-1.10)*.19
        else:r=.263+(z-1.32)*.06
        for i in range(N):
            phi=2*math.pi*i/N
            pleat=(.013+.024*(1-t)**1.5)*math.cos(12*phi+2.0*t)
            secondary=.009*math.cos(19*phi-4*t)
            radius=r+pleat+secondary
            vv.append((radius*math.cos(phi), radius*.83*math.sin(phi)-.008, z))
    for j in range(M-1):
        for i in range(N):
            a=j*N+i; b=j*N+(i+1)%N
            ff.append((a,b,b+N,a+N))
    ob=mesh_obj("Chiton_One_Connected_Cloth_Surface",vv,ff)
    setmat(ob,cloth_m)
    vg=ob.vertex_groups.new(name="PIN")
    top=[i for j in range(M-2,M) for i in range(j*N,(j+1)*N)]
    vg.add(top,1.0,"REPLACE")
    return ob

def himation():
    # Separate real garment layer, physically justifiable as a sash.
    rows=38; cols=9; vv=[];ff=[]
    for i in range(rows):
        t=i/(rows-1)
        c=Vector((-.19+.42*t,-.19-.035*math.sin(math.pi*t),1.33-.29*t))
        width=.095+.025*math.sin(math.pi*t)
        for k in range(cols):
            s=(k/(cols-1)-.5)
            vv.append((c.x+.035*s,c.y-.012*math.sin(4*math.pi*t)*s,c.z+width*s))
    for i in range(rows-1):
        for k in range(cols-1):
            q=i*cols+k
            ff.append((q,q+1,q+cols+1,q+cols))
    ob=mesh_obj("Himation_Independent_Structural_Cloth_Layer",vv,ff)
    setmat(ob,cloth_m)
    vg=ob.vertex_groups.new(name="PIN")
    vg.add([r*cols+k for r in (0,1,rows-2,rows-1) for k in range(cols)],1.,'REPLACE')
    return ob

def add_cloth(ob):
    mod=ob.modifiers.new("REAL_BLENDER_CLOTH","CLOTH")
    mod.settings.quality=5
    mod.settings.mass=.25
    mod.settings.vertex_group_mass="PIN"
    mod.collision_settings.use_collision=True
    mod.collision_settings.use_self_collision=True
    mod.collision_settings.distance_min=.008
    mod.collision_settings.self_distance_min=.009
    return mod

def evaluate_frozen(ob):
    deps=bpy.context.evaluated_depsgraph_get()
    ev=ob.evaluated_get(deps)
    me=bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=deps)
    before=[v.co.copy() for v in ob.data.vertices]
    if len(me.vertices)!=len(before):raise RuntimeError("CLOTH_SOLVER_CHANGED_TOPOLOGY")
    displacement=sum((v.co-before[i]).length for i,v in enumerate(me.vertices))/len(before)
    if displacement<1e-5: raise RuntimeError("CLOTH_DID_NOT_SIMULATE")
    ob.modifiers.clear()
    old=ob.data;ob.data=me
    bpy.data.meshes.remove(old)
    return displacement

def sphere(name,loc,scale,m,sub=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=sub,ring_count=20,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale
    setmat(o,m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(name,points,radius,m):
    cu=bpy.data.curves.new(name+"_curve","CURVE")
    cu.dimensions="3D";cu.resolution_u=24
    cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new("BEZIER");sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):
        p.co=co;p.handle_left_type="AUTO";p.handle_right_type="AUTO"
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob)
    setmat(ob,m)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object

def add_detail(body):
    top=sorted([v.co.z for v in body.data.vertices])[-1]
    sphere("Hair_Sculpted_Back_Mass",(0,.058,top-.12),(.134,.126,.145),hair_m,40)
    sphere("Hair_Rear_3D_Chignon",(0,.17,top-.18),(.098,.082,.08),hair_m,32)
    for side in (-1,1):
        pts=[]
        for i in range(9):
            t=i/8
            theta=math.pi*(.12+.85*t)
            pts.append((side*(.082+.054*math.sin(theta)),-.070+.19*t,top-.075-.095*t))
        tube("Braided_Hair_3D_"+str(side),pts,.018,hair_m)
    # Decorative headband is actual mesh, not an image decal.
    circ=[(.117*math.cos(a),.119*math.sin(a)+.045,top-.116+.012*math.cos(a*2))
          for a in [2*math.pi*i/24 for i in range(25)]]
    tube("Golden_Circlet",circ,.005,gold)
    armpts=[v.co for v in body.data.vertices if v.co.x>.50 and v.co.z>1.22]
    if len(armpts)<15:
        ball_center=(.62,-.02,1.63)
    else:
        far=max(armpts,key=lambda v:v.x)
        ball_center=(float(far.x)-.030,float(far.y)-.015,float(far.z)+.092)
    sphere("Ariadne_Golden_Ball_Pose_Unverified",ball_center,(.098,)*3,gold,48)
    curve=[ball_center, (ball_center[0]+.10,ball_center[1]+.025,ball_center[2]-.10),
           (.44,.12,1.35),(.38,.13,1.07),(.42,.1,.72),(.43,.11,.38),
           (.34,-.10,.18),(.03,-.42,.15),(-.37,-.03,.18)]
    tube("One_Continuous_Golden_Thread",curve,.007,gold)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.51,depth=.12,location=(0,0,-.055))
    o=bpy.context.object;o.name="Marble_Pedestal";setmat(o,stone)
    bev=o.modifiers.new("Pedestal_Bevel","BEVEL");bev.width=.018;bev.segments=3
    o.modifiers.new("WeightedNormal","WEIGHTED_NORMAL")

def camera(deg):
    ob=bpy.data.objects.get("CAMERA_LOCKED")
    if ob is None:
        ca=bpy.data.cameras.new("CAMERA_LOCKED")
        ob=bpy.data.objects.new("CAMERA_LOCKED",ca)
        bpy.context.collection.objects.link(ob)
    a=math.radians(deg);target=Vector((0,0,.89))
    ob.location=Vector((4.2*math.sin(a),-4.2*math.cos(a),.89))
    ob.rotation_euler=(target-ob.location).to_track_quat("-Z","Y").to_euler()
    ob.data.type="PERSP";ob.data.lens=50;ob.data.sensor_width=36
    bpy.context.scene.camera=ob
    return ob

def render(angle, width, height, path):
    scene=bpy.context.scene
    camera(angle)
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size<1000:
        raise RuntimeError("RENDER_OUTPUT_MISSING_"+str(angle))

def main():
    global stone,cloth_m,gold,hair_m
    bpy.ops.wm.read_factory_settings(use_empty=True)
    stone=mat("Ivory_Greek_Marble",(.77,.74,.67),0,.44)
    cloth_m=mat("Warm_Sculpted_Limestone_Chiton",(.84,.77,.65),0,.64)
    gold=mat("Gold_Thread_and_Sphere",(.80,.49,.10),.78,.22)
    hair_m=mat("Dark_Stone_Carved_Hair",(.41,.32,.28),0,.62)
    body=load_body()
    chiton=dress();sash=himation()
    scene=bpy.context.scene
    scene.frame_start=1;scene.frame_end=42
    for o in (chiton,sash):add_cloth(o)
    first = [tuple(p.co) for p in chiton.data.vertices]
    scene.frame_set(1)
    for f in range(2,43):scene.frame_set(f)
    deltas={o.name:evaluate_frozen(o) for o in (chiton,sash)}
    if not all(d>1e-5 for d in deltas.values()):
        raise RuntimeError("REAL_CLOTH_SIMULATION_FAILED")
    (OUT/"cloth_solver_proof.json").write_text(json.dumps({
        "blender_version":bpy.app.version_string,
        "solver":"Blender CLOTH modifier actual frame evaluation",
        "frames_evaluated":42,"collision":True,"self_collision":True,
        "displacement_mean_m":deltas,"face_count":len(chiton.data.polygons),
        "primary_garment_connected_topology_declared":True,
        "art_approved":False
    },indent=2))
    add_detail(body)
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.display.shading.background_type="VIEWPORT"
    scene.display.shading.background_color=(.11,.12,.14)
    scene.render.image_settings.file_format="PNG"
    scene.render.film_transparent=False
    scene.render.image_settings.color_mode="RGBA"
    for deg in range(0,360,15):
        render(deg,288,432,R24/("VIEW_%03d.png"%deg))
    keydir=OUT/"key_views";keydir.mkdir(exist_ok=True)
    for deg in (0,45,90,135,180,270):
        render(deg,600,900,keydir/("VIEW_%03d.png"%deg))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Ariadne_V85_CC0_Cloth_Engineering.blend"))
    bpy.ops.object.select_all(action="DESELECT")
    selected=[o for o in scene.objects if o.type=="MESH" and o.name!="CAMERA_LOCKED"]
    for o in selected:o.select_set(True)
    bpy.context.view_layer.objects.active=selected[0]
    path=OUT/"Ariadne_V85_Engineering_NOT_ART.glb"
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,export_yup=True)
    if not path.is_file() or path.stat().st_size<300000:
        raise RuntimeError("GLB_EXPORT_INVALID")
    original_size=path.stat().st_size
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    if len(imported)<5:raise RuntimeError("GLB_REIMPORT_LOST_MESHES")
    audit={"status":"ENGINEERING_GLTF_EXPORTED_NOT_ART",
           "release_approved":False,"v20_reference_present":False,
           "all_24_view_art_similarity_95pct":False,
           "independent_2d_reference_missing":True,
           "blender_version":bpy.app.version_string,
           "actual_24_renders":24,"actual_key_renders":6,
           "glb_bytes":original_size,"reimport_mesh_count":len(imported),
           "real_cc0_base_mesh":True,"female_makehuman_macro_target":True,
           "cloth_solver_evaluated":True,"cloth_displacements_m":deltas,
           "unresolved":["V20 24-angle source art","256 landmark correspondence",
             "anatomical hand-ball contact","artist-approved garment pattern and folds",
             "24-view independent art review","pose and face 2D approval"]}
    (OUT/"BUILD_AUDIT.json").write_text(json.dumps(audit,indent=2)+"\n")
    print("NEMA_BUILD_SUCCESS_ENGINEERING_ONLY "+json.dumps(audit))

if __name__=="__main__":
    main()
