# Blender true-art sculpt production from MakeHuman CC0 anatomical mesh.
# The front illustration is art direction, not a photogrammetric reconstruction.
import bpy, math, pathlib, random, json, hashlib, urllib.request
from mathutils import Vector
from math import sin, cos, pi, exp
ROOT=pathlib.Path.cwd()
OUT=ROOT/"ariadne_art_output"
OUT.mkdir(exist_ok=True)
SRC="https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
random.seed(28)

def fetch(name, suffix):
    p=OUT/name
    if not p.exists(): urllib.request.urlretrieve(SRC+suffix,str(p))
    return p
base=fetch("makehuman_base.obj","3dobjs/base.obj")
target=fetch("female.target","targets/macrodetails/caucasian-female-young.target")
verts=[];faces=[];group=""
for line in base.open():
    if line.startswith("v "):
        x,y,z=map(float,line.split()[1:4]);verts.append([x/10,-z/10,y/10])
    elif line.startswith("g "): group=line[2:].strip()
    elif line.startswith("f ") and group=="body":
        faces.append(tuple(int(n.split("/")[0])-1 for n in line.split()[1:]))
for line in target.open():
    a=line.split()
    if len(a)==4 and not a[0].startswith("#"):
        i=int(a[0]);dx,dy,dz=map(float,a[1:])
        verts[i][0]+=dx/10;verts[i][1]-=dz/10;verts[i][2]+=dy/10
assert len(verts)==19158 and len(faces)==13378

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def material(name, rgb,metal=0,rough=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*rgb,1)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    return m
ivory=material("01_Ivory_Greek_Stone",(0.84,.787,.689),rough=.59)
marble=material("02_Polished_Marble",(0.91,.846,.755),rough=.37)
shadow=material("03_Deep_Fold_Undertone",(.60,.53,.45),rough=.72)
gold=material("04_Warm_Solid_Gold",(.76,.39,.075),metal=.89,rough=.23)
brightgold=material("05_Highlight_Gold",(1,.69,.17),metal=.88,rough=.18)
darkgold=material("06_Antique_Gold",(.36,.17,.027),metal=.79,rough=.35)
hairmat=material("07_Warm_Ivory_Hair",(.79,.728,.625),rough=.66)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)

def meshobj(name,vs,fs,mat):
    mesh=bpy.data.meshes.new(name+"_Mesh");mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    return o

# Whole female mesh retained; never recreate body from capsules.
# Right arm anatomically continuous and rotated around shoulder in the X/Z plane.
# Piecewise blending limited to shoulder insertion.
z0=min(v[2] for v in verts[:13380])
for v in verts:
    v[2]-=z0
    x,y,z=v
    # right shoulder approx (0.20,0,1.28) ; positive X arm. 78 degree arm lift
    w=smooth(.175,.285,x)*smooth(.71,.91,z)
    dx=x-.202;dz=z-1.285
    a=math.radians(78)
    rx=.202+dx*cos(a)-dz*sin(a)
    rz=1.285+dx*sin(a)+dz*cos(a)
    v[0]=x+(rx-x)*w;v[2]=z+(rz-z)*w
    # weight shift for contrapposto subtly moves pelvis and torso
    z=v[2]
    if z>.53 and z<1.33:
        drift=.026*sin(pi*(z-.53)/.8)
        v[0]+=drift*(1-.35*smooth(1.20,1.36,z))
human=meshobj("01_TRUE_FEMALE_ANATOMY_CC0_K_POSE_DRAFT",verts,faces,ivory)
human["anatomy_source"]="MakeHuman CC0 19158 original mesh vertices / 13378 body quads"
human["morph_source"]="caucasian-female-young.target"
human["sculpt_status"]="UNAPPROVED_ARTISTIC_DRAFT"
# Curves and tubes (actual volumetric tubes, no projected/painted ropes).
def curve(name,coords,rad,mat,cyclic=False,res=14):
    c=bpy.data.curves.new(name,"CURVE");c.dimensions="3D";c.resolution_u=res
    c.bevel_depth=rad;c.bevel_resolution=3;c.use_fill_caps=True
    s=c.splines.new("POLY");s.points.add(len(coords)-1)
    for q,p in zip(s.points,coords):q.co=(*p,1)
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o)
    o.data.materials.append(mat);return o
def UVsphere(name,pos,scale,mat,seg=40,rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=pos)
    o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(name,r1,r2,depth,z,mat,vertices=128):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=depth,location=(0,0,z))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat)
    bevel=o.modifiers.new("Carved_Stone_Edge","BEVEL");bevel.width=.009;bevel.segments=3
    o.modifiers.new("Weighted_Normals","WEIGHTED_NORMAL")
    return o
# Pedestal with layered real geometry; the statue stands at z=0.
cyl("20_Bottom_Platform",.49,.47,.09,-.085,marble)
cyl("21_Gold_Band",.459,.459,.038,-.018,darkgold)
cyl("22_Greek_Key_Stone_Ring",.452,.452,.092,.041,ivory)
cyl("23_Upper_Carved_Lip",.49,.48,.045,.095,marble)
for radius,z,rad,mat in [(.454,.014,.004,gold),(.452,.064,.003,gold),(.484,.108,.004,brightgold),(.467,-.045,.003,gold)]:
    curve("Pedestal_Continuous_Molding",[(radius*cos(i*2*pi/180),radius*sin(i*2*pi/180),z) for i in range(180)],rad,mat,True)
# Greek key hand-crafted bands, continuous 3D engraved tubes.
for j in range(48):
    a=2*pi*j/48
    pts=[]
    grid=[(0,0),(.7,0),(.7,.75),(.2,.75),(.2,.25),(.48,.25),(.48,.52)]
    for u,v in grid:
        ang=a+u*2*pi/48
        pts.append((.454*cos(ang),.454*sin(ang),.025+v*.038))
    curve("Greek_Key_%02d"%j,pts,.0027,gold,res=2)
# Main draped skirt: physically distinct 3D surface with asymmetric fold crests.
# Sculpted multiscale fold locations; non-repeating widths/depths and asymmetric contact.
foldangles=[.05,.32,.61,.98,1.36,1.70,2.12,2.55,2.93,3.34,3.66,4.05,4.43,4.92,5.28,5.73]
foldamps=[.025,.040,.024,.060,.044,.018,.035,.049,.028,.056,.021,.047,.032,.063,.037,.022]
def wrapdiff(a,b):return (a-b+pi)%(2*pi)-pi
def radii(theta,z):
    # z runs hem -> waist, varying oval cross-section with cloth expansion near hem
    t=max(0,min(1,(z-.17)/.85))
    rx=.31*(1-t)+.165*t
    ry=.235*(1-t)+.110*t
    out=0
    for j,(az,amp) in enumerate(zip(foldangles,foldamps)):
        # folds converge into waist gatherings and split near hem
        centre=az+(.30*sin(az*2.1))*(1-t)+.10*sin(5*t+j*.3)
        d=wrapdiff(theta,centre)
        width=.105+.045*(j%3)+(.015*(1-t))
        positive=amp*exp(-.5*(d/width)**2)
        valley=-.018*exp(-.5*((d-.15)/(width*.6))**2)
        out+=(positive+valley)*(.30+.70*(1-t))
    return rx,ry,out
n=256;m=90;sv=[];sf=[]
for iz in range(m+1):
    t=iz/m;z=.16+t*.90
    for j in range(n):
        a=2*pi*j/n
        rx,ry,depth=radii(a,z)
        # silhouette is elliptical, differs front/back
        x=(rx+depth)*cos(a)+.019*t+.015*(1-t)*sin(a*3)
        y=(ry+.8*depth)*sin(a)+.029*sin(z*3)
        sv.append((x,y,z+.012*sin(a*4)*(1-t)))
for iz in range(m):
    for j in range(n):
        a=iz*n+j;b=iz*n+(j+1)%n;c=(iz+1)*n+(j+1)%n;d=(iz+1)*n+j
        sf.append((a,b,c,d))
skirt=meshobj("30_True_Three_Dimensional_Chiton_Skirt",sv,sf,marble)
s=skirt.modifiers.new("Sculpted_Fabric_Thickness","SOLIDIFY");s.thickness=.008
# Outer hem deep dramatic drape
curve("31_Hem_Highlight",[(sv[j][0],sv[j][1],sv[j][2]-.004) for j in range(n)],.003,ivory,True)
# Tunic bodice over ribcage, anatomically contacted with fabric relief
tv=[];tf=[];bn=160;bm=45
for i in range(bm+1):
    t=i/bm;z=1.0+t*.36
    for j in range(bn):
        a=2*pi*j/bn
        r=.155+.027*sin(pi*t)+.012*cos(5*a+3*t)*sin(pi*t)
        x=r*cos(a)+.025
        y=(.113+.018*sin(pi*t))*sin(a)-.012
        # neckline broad sloping asymmetry
        z1=z+.022*t*cos(a*1.5)
        tv.append((x,y,z1))
for i in range(bm):
    for j in range(bn):
        a=i*bn+j;b=i*bn+(j+1)%bn;c=(i+1)*bn+(j+1)%bn;d=(i+1)*bn+j
        tf.append((a,b,c,d))
bodice=meshobj("32_Anatomical_Bodice_Fabric",tv,tf,ivory)
solid=bodice.modifiers.new("Bodice_Thin_Marble","SOLIDIFY");solid.thickness=.004
# Crossed himation: large diagonally draped genuine curved ribbon surface,
# with separately varying thickness/ridges and explicit sculptural boundary.
def ribbon(name,pts,widths,mat,rad=.003,div=120,col=24,arch=.018):
    # interpolate cubic Catmull-Rom curve for center line; generate real strip surface
    def sample(t):
        u=t*(len(pts)-1);i=min(int(u),len(pts)-2);f=u-i
        a=Vector(pts[max(i-1,0)]);b=Vector(pts[i]);c=Vector(pts[i+1]);d=Vector(pts[min(i+2,len(pts)-1)])
        f2=f*f;f3=f2*f
        q=.5*((2*b)+(-a+c)*f+(2*a-5*b+4*c-d)*f2+(-a+3*b-3*c+d)*f3)
        return q
    vv=[];ff=[];left=[];right=[]
    for i in range(div+1):
        t=i/div;p=sample(t);prev=sample(max(0,t-.005));nxt=sample(min(1,t+.005))
        tang=(nxt-prev).normalized()
        across=Vector((-tang.z,0,tang.x))
        if across.length<.1:across=Vector((0,0,1))
        across.normalize()
        w=widths[0]*(1-t)+widths[-1]*t
        for j in range(col+1):
            v=j/col*2-1
            point=p+across*v*w*.5
            point.y-=arch*(1-v*v)*sin(pi*t)**2
            # Vary large folds genuinely in the surface, not normals/texture
            point.y+=.012*sin(3.6*pi*v+.5*sin(4*pi*t))*sin(pi*t)
            vv.append(tuple(point))
        left.append(vv[-(col+1)]);right.append(vv[-1])
    for i in range(div):
        for j in range(col):
            a=i*(col+1)+j;ff.append((a,a+1,a+col+2,a+col+1))
    o=meshobj(name,vv,ff,mat)
    so=o.modifiers.new("Sculptural_Cloth_Thickness","SOLIDIFY");so.thickness=.007
    curve(name+"_Sewn_Edge_A",left,rad,mat)
    curve(name+"_Sewn_Edge_B",right,rad,mat)
    return o
# large chest diagonal across body from left shoulder to right waist
ribbon("33_Diagonal_Chest_Drape",[(-.19,-.085,1.31),(-.16,-.17,1.245),(.035,-.194,1.18),(.19,-.14,1.07)], [.09,.115],marble)
# upper grecian cowl and golden shoulder chord
ribbon("34_Cowl_Over_Clavicles",[(-.20,-.055,1.32),(-.10,-.16,1.295),(.03,-.18,1.275),(.19,-.11,1.33)], [.075,.055],ivory)
# prominent waist to left hip diagonal curtain in front
ribbon("35_Hip_Diagonal_Fold",[(.18,-.13,.98),(.16,-.25,.89),(-.03,-.32,.72),(-.23,-.28,.60),(-.27,-.21,.55)], [.095,.16],marble,arch=.042)
# broad angular long skirt overlay crossing lower thighs
ribbon("36_Main_Sculpted_Sash",[(.12,-.28,.94),(.01,-.36,.69),(-.13,-.39,.43),(-.22,-.33,.25),(-.32,-.24,.17)], [.13,.24],ivory,arch=.015)
# A second lower wrap from left hip into center front diagonal
ribbon("37_Lower_Fabric_Sweep",[(-.25,-.18,.52),(-.24,-.28,.38),(-.11,-.34,.26),(.07,-.28,.21)], [.075,.11],marble)
# Draped panels attached from back of shoulders; actual 3D with hanging arcs.
ribbon("38_Back_Veil_Left",[(-.085,.05,1.52),(-.20,.16,1.36),(-.25,.20,1.11),(-.30,.19,.83),(-.26,.15,.59)], [.15,.17],ivory)
ribbon("39_Back_Veil_Right",[(.095,.045,1.51),(.18,.15,1.35),(.23,.23,1.06),(.29,.24,.78),(.30,.18,.50)], [.14,.19],marble)
# waist braid/belt with actual raised roped texture
curve("40_Waist_Braided_Gold",[(.19*cos(2*pi*i/180)+.025,.136*sin(2*pi*i/180)-.015,1.035+.012*sin(2*pi*i/180*2)) for i in range(180)],.005,darkgold,True)
curve("41_Necklace_Cowl_Gold",[(-.20,-.085,1.32),(-.13,-.176,1.285),(0,-.197,1.26),(.13,-.160,1.30),(.20,-.08,1.34)],.006,brightgold)
# Hair and braided Greek tiara — fully 3D spiral ropes around temple.
head=(0,.010,1.505)
UVsphere("50_Sculpted_Hair_Cap",(0,.03,1.526),(.090,.079,.095),hairmat)
for n in range(16):
    ang=2*pi*n/16
    x=.084*cos(ang);y=.02+.068*sin(ang);z=1.573+.019*cos(ang*3)
    UVsphere("Braid_Knot_%02d"%n,(x,y,z),(.022,.018,.019),hairmat,20,12)
for j in range(6):
    ang=2*pi*j/6
    pts=[]
    for k in range(85):
        t=k/84; a=ang+2*pi*2*t
        x=.093*cos(ang)+.013*cos(a)*(1-t)
        y=.01+.066*sin(ang)+.012*sin(a)*(1-t)
        z=1.569-.09*t
        pts.append((x,y,z))
    curve("Braided_Curl_%02d"%j,pts,.0033,hairmat)
# golden circlet and small filigree ornaments
curve("51_Gold_Forehead_Diadem",[(.096*cos(2*pi*i/120),.014+.08*sin(2*pi*i/120),1.582) for i in range(120)],.006,gold,True)
for n in range(24):
    a=n*2*pi/24
    UVsphere("Tiara_Pearl_%02d"%n,(.096*cos(a),.014+.08*sin(a),1.583),(.006,.006,.006),brightgold,10,8)
# Orb with 3D criss-cross threads. Ball held above raised hand.
ball=Vector((.72,-.085,1.48))
UVsphere("60_Ariadne_Golden_Thread_Orb",ball,(.089,.089,.089),darkgold,64,40)
for k in range(14):
    a=k*pi/14
    pts=[]
    for i in range(160):
        t=i*2*pi/160
        # great circle tilted in space; wire curve lies on sphere
        x=.090*cos(t)*cos(a)
        y=.090*cos(t)*sin(a)
        z=.090*sin(t)
        pts.append(tuple(ball+Vector((x,y,z))))
    curve("Orb_Real_Wound_Gold_%02d"%k,pts,.0028,brightgold,True)
# gold cord a SINGLE spatial 3D curve (bevel creates real mesh on export)
cord=[(.69,-.136,1.407),(.70,-.150,1.28),(.72,-.17,1.13),(.73,-.185,.96),(.71,-.22,.78),(.63,-.265,.68),
 (.48,-.34,.60),(.23,-.39,.52),(-.015,-.39,.43),(-.24,-.36,.34),(-.405,-.31,.23),(-.46,-.23,.14),
 (-.45,-.19,.06),(-.36,-.29,.035),(-.25,-.39,.026),(-.35,-.46,.035),(-.49,-.28,.035),
 (-.44,.05,.038),(-.30,.29,.04),(-.03,.36,.04)]
# Smooth single connected curve with Catmull Rom (actual spatial line).
def catmull(p0,p1,p2,p3,t):
    return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
cord_points=[]
for i in range(len(cord)-1):
    a=Vector(cord[max(0,i-1)]);b=Vector(cord[i]);c=Vector(cord[i+1]);d=Vector(cord[min(len(cord)-1,i+2)])
    for j in range(20):cord_points.append(tuple(catmull(a,b,c,d,j/20)))
cord_points.append(cord[-1])
curve("61_SINGLE_3D_GOLDEN_THREAD",cord_points,.0044,brightgold)
# visual pearl in palm touching ball edge
# improve hand-to-ball contact: art draft first, not anatomical hand IK validation
UVsphere("62_Palm_Orb_Contact_Highlight",(.662,-.106,1.430),(.026,.014,.022),ivory,24,16)
# lighting and camera for beautiful studio, 24-angle sample
world=bpy.context.scene.world;world.color=(.10,.10,.10)
def area(name,loc,energy,color,size):
    data=bpy.data.lights.new(name,"AREA");data.energy=energy;data.color=color;data.shape="DISK";data.size=size
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((0,0,1.03))-ob.location).to_track_quat("-Z","Y").to_euler()
area("Warm_Key",(-3.2,-4,4.8),750,(1,.86,.73),4)
area("Cool_Fill",(3,-3,2.5),500,(.64,.77,1),3)
area("Golden_Rim",(1,3,3.0),1000,(1,.86,.55),3)
camdata=bpy.data.cameras.new("Locked_Orthographic_Camera")
cam=bpy.data.objects.new("Locked_Orthographic_Camera",camdata);bpy.context.collection.objects.link(cam)
camdata.type="ORTHO";camdata.ortho_scale=2.03
scene=bpy.context.scene;scene.camera=cam;scene.render.engine="CYCLES";scene.cycles.samples=16
scene.render.resolution_x=560;scene.render.resolution_y=760;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.world.color=(.045,.09,.15)
scene.view_settings.view_transform="AgX"
scene.render.filepath=str(OUT/"Ariadne_Art_Draft_front.png")
def camera_at(angle):
    a=math.radians(angle)
    cam.location=(-5*sin(a),-5*cos(a),1.00)
    cam.rotation_euler=(Vector((.045,0,.81))-cam.location).to_track_quat("-Z","Y").to_euler()
camera_at(0)
# Save editable primary art scene, export only objects with geometry, not lights.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Ariadne_Sculptural_Art_Draft.blend"))
# Convert curves to genuine mesh before glTF export: preserve geometry of gold cord.
bpy.ops.object.select_all(action="DESELECT")
for obj in list(scene.objects):
    if obj.type=="CURVE":
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target="MESH")
objects=[o for o in scene.objects if o.type=="MESH"]
bpy.ops.object.select_all(action="DESELECT")
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=human
status=bpy.ops.export_scene.gltf(filepath=str(OUT/"Ariadne_Sculptural_Art_Draft.glb"),export_format="GLB",use_selection=True)
assert "FINISHED" in status and (OUT/"Ariadne_Sculptural_Art_Draft.glb").stat().st_size>200000
for ang in range(0,360,15):
    camera_at(ang)
    scene.render.filepath=str(OUT/f"angle_{ang:03d}.png")
    bpy.ops.render.render(write_still=True)
# Source scene and GLB are validated separately, no art 95% claims.
counts={o.name:len(o.data.polygons) for o in objects if o.type=="MESH"}
audit={"status":"DIAGNOSTIC_UNAPPROVED","geometry":"real MakeHuman CC0 female body, geometric dress and multiple independent sculptural parts",
"body_source_quads":13378,"orb_thread_object_count":1,"art_source":"one front artwork only","multiview_source_art":"NOT_MEASURABLE",
"model_parts":len(objects),"rendered_views":24,"mesh_counts":counts,
"art_gate":"UNAPPROVED_NEEDS_INDEPENDENT_REVIEW","uv_pbr_gate":"PENDING_FINAL_SCULPT","sculpt_technique":"non-destructive spatial deformation of verified body + parametric garment meshes, not hand sculpting",
"known_issues":["Anatomical raised hand to orb grip still unverified","Garment collision and artistic accuracy not professionally certified","No independent back/side art source","Not equivalent to a detailed manual museum-grade sculpt"]}
(OUT/"Art_QA.json").write_text(json.dumps(audit,indent=2))
print("ART_DRAFT_SCENE_EXPORTED", (OUT/"Ariadne_Sculptural_Art_Draft.glb").stat().st_size)
