"""GitHub-side Blender worker. No arbitrary code from vision model."""
import bpy, sys, json, math, hashlib
from pathlib import Path
from mathutils import Vector
args=json.loads(Path(sys.argv[sys.argv.index("--")+1]).read_text())
def load(p):
 bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(p))
 bpy.context.view_layer.update()
load(args["source"])
if args["mode"]=="mutate":
 change=args["proposal"]
 ob=bpy.data.objects.get(change["object"])
 assert ob and ob.type=="MESH","unknown mesh"
 name=ob.name.lower()
 # Protect the real body, hands, base, and gold endpoints from unvalidated
 # freeform edits. A gold/palm/eye topology redesign must use reviewed builder.
 assert any(k in name for k in ("hair","braid","scalp","iris","pupil","eyebrow","cloth","drape","himation","chiton")),"object outside safe edit set"
 assert not any(k in name for k in ("pedestal","plinth","thread","anatomy","hand","wrist","orb","gold")),"protected mesh"
 assert change["op"] in ("normal_offset","local_translate","scale_local")
 c=Vector(change["center"]);radius=float(change["radius_m"])
 assert .002<=radius<=.08
 assert all(math.isfinite(x) for x in c)
 delta=Vector(change.get("delta_m",[0,0,0])); amount=float(change.get("amount",0))
 assert delta.length<=.002 and abs(amount)<=.002
 assert all(math.isfinite(x) for x in (*delta,amount))
 mat=ob.matrix_world; inv=mat.inverted(); nmat=mat.to_3x3().inverted().transposed()
 moved=0
 for v in ob.data.vertices:
  pos=mat@v.co;dist=(pos-c).length
  if dist>=radius:continue
  t=1-dist/radius;w=t*t*(3-2*t)
  if change["op"]=="normal_offset":d=(nmat@v.normal).normalized()*amount*w
  elif change["op"]=="local_translate":d=delta*w
  else:d=(pos-c)*(amount/radius)*w
  if d.length>1e-9:v.co=inv@(pos+d);moved+=1
 assert moved>0,"no geometry changed"
 ob.data.update()
 bpy.ops.export_scene.gltf(filepath=args["output"],export_format="GLB",export_animations=False,export_cameras=False,export_lights=False)
 assert Path(args["output"]).stat().st_size>100000
 Path(args["result"]).write_text(json.dumps({"changed_vertices":moved,"object":ob.name,"proposal":change}))
elif args["mode"]=="inventory":
 out=[]
 for o in bpy.context.scene.objects:
  if o.type!="MESH":continue
  b=[o.matrix_world@Vector(v) for v in o.bound_box]
  out.append({"object":o.name,"min":[min(v[i] for v in b) for i in range(3)],"max":[max(v[i] for v in b) for i in range(3)],"vertices":len(o.data.vertices)})
 Path(args["result"]).write_text(json.dumps(out))
elif args["mode"]=="render":
 scene=bpy.context.scene
 scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.light="STUDIO"
 scene.display.shading.color_type="MATERIAL"
 scene.display.shading.show_cavity=True
 scene.render.film_transparent=True
 scene.render.image_settings.file_format="PNG"
 scene.render.image_settings.color_mode="RGBA"
 scene.render.resolution_x,args_y=args["resolution"]
 scene.render.resolution_y=args_y
 scene.render.resolution_percentage=100
 cam=bpy.data.objects.new("ReactCamera",bpy.data.cameras.new("ReactCamera"))
 scene.collection.objects.link(cam);scene.camera=cam
 cam.data.type="ORTHO";cam.data.ortho_scale=args["ortho_scale"]
 out=Path(args["output"]);out.mkdir(parents=True,exist_ok=True)
 target=Vector(args["target"])
 for a,e in args["views"]:
  az,el=map(math.radians,(a,e))
  d=Vector((math.sin(az)*math.cos(el),math.cos(az)*math.cos(el),math.sin(el)))
  cam.location=target+d*args["distance"]
  cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
  scene.render.filepath=str(out/("AZ%03d_EL%+03d.png"%(a,e)))
  bpy.ops.render.render(write_still=True)
else:raise ValueError(args["mode"])
