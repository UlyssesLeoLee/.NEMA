#!/usr/bin/env python3
"""V87 anatomical-body garment sculpture from explicit 2D fold paths, NOT final art.

Cloth solver operates ONLY on a narrow unprotected hem area after the PRIMARY
folds and structural layers have already been sculpted into actual 3D meshes.
"""
import json, math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
PLAN=json.loads((ROOT/'guides/fold_design.json').read_text())
assert PLAN['release_approval'] is False
MESH_PATH=ROOT.parent/'ariadne_v85/output/MakeHuman_CC0_female_1p74m.obj'

def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)))
    return t*t*(3-2*t)

def asset(name,rgba,metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgba,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgba,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=.56 if not metallic else .23
    return m

def mesh(name,vertices,faces,material):
    data=bpy.data.meshes.new(name+'_topology');data.from_pydata(vertices,[],faces);data.update()
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
    data.materials.append(material)
    for f in data.polygons:f.use_smooth=True
    return o

def load_cc0(mat):
    if not MESH_PATH.is_file(): raise RuntimeError('OFFICIAL_MAKEHUMAN_REAL_MESH_MISSING')
    verts=[];faces=[]
    for line in MESH_PATH.read_text().splitlines():
        if line.startswith('v '):verts.append(tuple(map(float,line.split()[1:4])))
        elif line.startswith('f '):faces.append(tuple(int(p)-1 for p in line.split()[1:]))
    if len(verts)<15000 or len(faces)<10000:raise RuntimeError('INCORRECT_BODY_TOPOLOGY')
    o=mesh('MakeHuman_CC0_Female_UNPOSED_PREVIEW',verts,faces,mat)
    c=o.modifiers.new('Body_collision','COLLISION')
    c.settings.thickness_outer=.008
    return o

def dist_segment(x,z,p,q):
    dx=q[0]-p[0];dz=q[1]-p[1];t=((x-p[0])*dx+(z-p[1])*dz)/(dx*dx+dz*dz+1e-8)
    t=max(0.,min(1.,t))
    return math.hypot(x-(p[0]+dx*t),z-(p[1]+dz*t))

def map_art(u,v):
    # Explicit provisional artistic registration; not calibrated 1:1 lens geometry.
    return (u-515)/665,(1190-v)/1160*1.74

def fold_field(x,z):
    val=0.
    for line in PLAN['primary_fold_paths']:
        if line['region'] in ('back_veil_primary_falls','sleeve_and_elbow_fold_logic'):continue
        points=[map_art(*p) for p in line['source_pixels']]
        d=min(dist_segment(x,z,a,b) for a,b in zip(points,points[1:]))
        w=line['width_m'];a=line['amplitude_m']
        # Real grooves are a raised ridge flanked by soft valleys, not texture.
        val+=a*(math.exp(-.5*(d/w)**2)-.23*math.exp(-.5*((d-2.2*w)/w)**2))
    return max(-.025,min(.080,val))

def main_chiton(fabric):
    # Authored silhouette with locked waist, unequal front/back volumes,
    # sculpted fold *curves*, sculpted neckline, asymmetry, and open hem.
    cols=96;rows=100;vertices=[];faces=[]
    groups={name:[] for name in ('PIN','PRIMARY_OUTLINE_LOCK','PRIMARY_FOLD_LOCK','SECONDARY_SIM_ZONE',
             'WAIST_GATHER','SHOULDER_DRAPE','CHEST_U_DRAPE','BACK_VEIL_ANCHOR')}
    for j in range(rows):
        t=j/(rows-1);z0=.10+1.37*t
        skirt=smooth(.9,.22,z0) if False else 1.-smooth(.15,1.00,z0)
        waist=math.exp(-((z0-1.04)/.17)**2)
        rx=.245+.148*skirt-.040*waist
        ry=.183+.105*skirt-.019*waist
        for i in range(cols):
            phi=2*math.pi*i/cols
            x=rx*math.cos(phi)
            y=ry*math.sin(phi)
            front=smooth(.07,.62,-math.sin(phi))
            rear=smooth(.07,.62,math.sin(phi))
            # K-shaped authored asymmetric hem; pleats are actual mesh deformation.
            z=z0 + (1-t)**12*(.025*math.cos(3*phi)-.032*max(0.,math.sin(phi)))
            if j>=rows-3:
                z+=(-.12*front*math.exp(-((x/.14)**2)) + .045*math.cos(2*phi))*(t**40)
            if z0<.22: z+=.025*math.cos(5*phi)+.014*math.cos(9*phi)
            relief=fold_field(x,z0)*front
            # Back has its own descending pleat rhythm (3D geometry), protected from sim.
            rear_fold=.020*rear*(1.-smooth(1.08,1.35,z0))*math.cos(5*phi+2.1*(1-t))
            y=y-relief+rear_fold
            # Waist gathered into the belt: geometry has discrete gathered tucks.
            y-=front*waist*.013*math.cos(8*phi)
            vertices.append((x,y,z))
            k=j*cols+i
            if z0<.24 and (i%3)!=0:
                groups['SECONDARY_SIM_ZONE'].append(k)
            else:
                groups['PIN'].append(k)
                groups['PRIMARY_OUTLINE_LOCK'].append(k)
            if .30<z0<1.32:
                groups['PRIMARY_FOLD_LOCK'].append(k)
            if .92<z0<1.14:
                groups['WAIST_GATHER'].append(k)
            if z0>1.29:
                groups['SHOULDER_DRAPE'].append(k)
            if 1.12<z0<1.36:
                groups['CHEST_U_DRAPE'].append(k)
            if z0>1.38 and math.sin(phi)>.1:
                groups['BACK_VEIL_ANCHOR'].append(k)
    for j in range(rows-1):
        for i in range(cols):
            k=j*cols+i;q=j*cols+(i+1)%cols
            faces.append((k,q,q+cols,k+cols))
    ob=mesh('ChitonDesignSculpt_ContinuousFoldSurface',vertices,faces,fabric)
    for name,idx in groups.items():
        vg=ob.vertex_groups.new(name=name)
        if idx:vg.add(idx,1.0,'REPLACE')
    # Secondary hem vertices intentionally unpinned; everything else preserves design.
    ob['primary_fold_sculpt_locked']=True
    ob['design_revision']=PLAN['revision']
    ob['source']='historical V20 art fold flow (not camera calibrated)'
    return ob,groups

def garment_front_depth(x,z):
    # Sample a continuous authored chiton frontal volume rather than suspending
    # a free panel in the air. This is a design-space approximation, not raycast.
    skirt=1.-smooth(.15,1.00,z)
    waist=math.exp(-((z-1.04)/.17)**2)
    rx=.245+.148*skirt-.040*waist
    ry=.183+.105*skirt-.019*waist
    normalized=min(.998,abs(x)/max(.001,rx))
    return -ry*math.sqrt(max(.0,1-normalized*normalized))

def front_sash(fabric,name,starts,ends,width=.12,stages=88,sections=19,surface_wrap=False):
    # Hand-designed 3D sewn drape sheet. The cross section has controlled
    # shallow folds, never four rectangular bands floating in front of body.
    pts=[];fs=[]
    tangent=Vector((ends[0]-starts[0],0,ends[2]-starts[2])).normalized()
    across=Vector((tangent.z,0,-tangent.x))
    for j in range(stages):
        t=j/(stages-1)
        x0=(1-t)*starts[0]+t*ends[0]
        z0=(1-t)*starts[2]+t*ends[2]-.070*math.sin(math.pi*t)
        # The material widens softly toward the center and tapers into seams.
        taper=.27+.73*math.sin(math.pi*t)**.43
        for i in range(sections):
            s=(i/(sections-1)-.5)*2
            xx=x0+across.x*width*taper*s
            zz=z0+across.z*width*taper*s
            if surface_wrap:
                # Maintain real contact with the outer dress profile as x turns
                # around the hip; this avoids floating plank-like fabric bands.
                yy=garment_front_depth(xx,zz)-.018
            else:
                yy=(1-t)*starts[1]+t*ends[1]-.018*math.sin(math.pi*t)
            # Low-amplitude *sculpted* bias folds, consistent through the sheet.
            yy-=.0045*math.cos(2*math.pi*s+2.2*t)*math.sin(math.pi*t)
            pts.append((xx,yy,zz))
    for j in range(stages-1):
        for i in range(sections-1):
            a=j*sections+i
            fs.append((a,a+1,a+sections+1,a+sections))
    o=mesh(name,pts,fs,fabric)
    o['structural_layer']=True
    o['primary_fold_sculpt_locked']=True
    return o

def veil(fabric):
    # Back veil: one pinned shoulder/head layer with carved longitudinal ridges,
    # complex curved hem and realistic curved sheet, never free-dropped.
    rows=100;cols=36;v=[];f=[]
    for j in range(rows):
        t=j/(rows-1)
        z=1.60-1.27*t
        breadth=.205+.13*smooth(.1,.8,t)
        for i in range(cols):
            s=(i/(cols-1)-.5)*2
            x=breadth*s+.035*math.sin(math.pi*t)*s
            yy=.10+.17*t+.070*(1-s*s)*math.sin(math.pi*t)
            yy+=.010*math.cos(4*math.pi*s+1.3*t)*(t**.5)
            zz=z+.08*(s*s)+(.046*math.sin(3*math.pi*s) if t>.95 else 0)
            v.append((x,yy,zz))
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;f.append((a,a+1,a+cols+1,a+cols))
    ob=mesh('BackVeilPattern_FoldSculpt_Connected',v,f,fabric)
    ob['primary_fold_sculpt_locked']=True
    ob['attachment']='headband_back_shoulder_seams'
    return ob

def add_design_layers(fabric):
    # Image evidence at V20: front shoulder U, diagonal across bodice, hip swag,
    # side sleeves and distinctive back veil form physically justified layers.
    # Chest diagonal is carved in the continuous chiton; no independent fake panel.
    front_sash(fabric,'HimationCrossHipDrape',(.245,-.26,1.03),(-.305,-.25,.68),.115,surface_wrap=True)
    front_sash(fabric,'LeftShoulderDrape',(-.22,-.10,1.42),(-.29,.08,.99),.095)
    front_sash(fabric,'RightShoulderDrape',(.22,-.07,1.42),(.28,.08,1.01),.080)
    veil(fabric)

def modifier_primary_protection(chiton,groups):
    # Only hem vertices may relax. This uses actual Blender CLOTH modifier;
    # old wrong pipeline free-dropped the entire garment body.
    mod=chiton.modifiers.new('V87_SECONDARY_HEM_RELAXATION','CLOTH')
    mod.settings.quality=5
    mod.settings.mass=.23
    mod.settings.vertex_group_mass='PIN'
    mod.collision_settings.use_collision=True
    mod.collision_settings.distance_min=.006
    mod.collision_settings.use_self_collision=True
    mod.collision_settings.self_distance_min=.006
    return mod

def sim(chiton,groups):
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=22
    before=[v.co.copy() for v in chiton.data.vertices]
    m=modifier_primary_protection(chiton,groups)
    scene.frame_set(1)
    for frame in range(2,23):scene.frame_set(frame)
    deps=bpy.context.evaluated_depsgraph_get()
    evaluated=chiton.evaluated_get(deps)
    deformed=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
    if len(deformed.vertices)!=len(before):raise RuntimeError('SOLVER_TOPOLOGY_CHANGED')
    protected=groups['PRIMARY_OUTLINE_LOCK']
    hem=groups['SECONDARY_SIM_ZONE']
    drifts=[(before[i]-deformed.vertices[i].co).length for i in range(len(before))]
    max_primary=max(drifts[i] for i in protected)
    p95_hem=sorted(drifts[i] for i in hem)[int(.95*(len(hem)-1))]
    proof={'solver':'Blender CLOTH evaluated 22 frames','actual_modifier_evaluated':True,
           'primary_fold_geometry_authored_before_solver':True,
           'pinned_primary_vertices':len(protected),'free_secondary_hem_vertices':len(hem),
           'maximum_primary_displacement_m':max_primary,'secondary_hem_p95_displacement_m':p95_hem,
           'max_primary_allowance_m':.012,'max_secondary_p95_allowance_m':.075,
           'artifact_type':'ENGINEERING_NOT_ART'}
    (OUT/'controlled_cloth_audit.json').write_text(json.dumps(proof,indent=2)+'\n')
    if max_primary>.012:raise RuntimeError('PRIMARY_SILHOUETTE_SHIFTED_AFTER_CLOTH')
    if p95_hem>.075:raise RuntimeError('SECONDARY_HEM_TOO_DISTORTED')
    if p95_hem<.000001:raise RuntimeError('CLOTH_NO_SECONDARY_MOVEMENT')
    chiton.modifiers.clear()
    old=chiton.data;chiton.data=deformed;bpy.data.meshes.remove(old)
    return proof

def camera(angle):
    ca=bpy.data.objects.get('V87_LOCKED_CAMERA')
    if ca is None:
        cam=bpy.data.cameras.new('V87_LOCKED_CAMERA');ca=bpy.data.objects.new('V87_LOCKED_CAMERA',cam);bpy.context.collection.objects.link(ca)
    a=math.radians(angle)
    ca.location=(4.2*math.sin(a),-4.2*math.cos(a),.91)
    target=Vector((0,0,.91))
    ca.rotation_euler=(target-ca.location).to_track_quat('-Z','Y').to_euler()
    ca.data.lens=50;ca.data.sensor_width=36;ca.data.type='PERSP'
    bpy.context.scene.camera=ca

def render_all():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.render.film_transparent=True
    scene.render.resolution_x=288;scene.render.resolution_y=432
    scene.render.resolution_percentage=100
    location=OUT/'render_24';location.mkdir(exist_ok=True)
    for ang in range(0,360,15):
        camera(ang)
        dest=location/f'VIEW_{ang:03d}.png'
        scene.render.filepath=str(dest)
        bpy.ops.render.render(write_still=True)
        if not dest.is_file() or dest.stat().st_size<1000:raise RuntimeError('MISSING_BLENDER_IMAGE')

def export_and_verify():
    path=OUT/'Ariadne_V87_DesignFirst_Engineering_NOT_ART.glb'
    scene=bpy.context.scene
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Ariadne_V87_DesignFirst_Editable.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    objects=[o for o in scene.objects if o.type=='MESH']
    if len(objects)<5:raise RuntimeError('GARMENT_STRUCTURAL_LAYERS_MISSING')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True)
    if path.stat().st_size<300_000:raise RuntimeError('GLB_TOO_SMALL')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    reimport=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if len(reimport)<len(objects):raise RuntimeError('GLB_ROUND_TRIP_LOST_OBJECTS')
    return {'bytes':path.stat().st_size,'mesh_count':len(reimport),'export_reimport_pass':True}

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    anatomy=asset('CC0 anatomical statue gray',(.68,.64,.59))
    fabric=asset('Royal sculpted ivory fold surfaces',(.87,.82,.74))
    body=load_cc0(anatomy)
    chiton,groups=main_chiton(fabric)
    add_design_layers(fabric)
    # Preserve a geometry-before-cloth checkpoint and evidence of authored folds.
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'V87_PrimaryFold_BeforeCloth.blend'))
    proof=sim(chiton,groups)
    render_all()
    exported=export_and_verify()
    data={'status':'ENGINEERING_GEOMETRY_CREATED','final_art_approved':False,
          'source_reference_recovered':True,'source_2d_in_github':'derived fold guides and reference silhouettes only',
          'independent_24_art_camera_registered':False,
          'body_mesh_type':'MakeHuman_CC0_true_original_topology_unposed',
          'garment_primary_sculpt_before_sim':True,'controlled_secondary_cloth':proof,
          'actual_24_views':24,'glb_round_trip':exported,
          'unresolved':['independent art camera-registration','human anatomy K pose and palm sphere',
                        'primary fold artistic fidelity and drape depth','head and hair sculpture',
                        'external V20 24-angle formal art signoff']}
    (OUT/'BUILD_AUDIT.json').write_text(json.dumps(data,indent=2)+'\n')
    print('V87 REAL ENGINEERING BUILD COMPLETED; 24-VIEW ART GATE NOT MET')

if __name__=='__main__':main()