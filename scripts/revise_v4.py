"""Derive v4 directly from the user's saved v3; do not rebuild the booth."""
import bpy,json,hashlib,math,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
OUT=ROOT/'Deliverables/v4';OUT.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
source=Path(bpy.data.filepath)
def fingerprint(o):
 return {'matrix':[list(r) for r in o.matrix_world],'mesh':hashlib.sha256(str(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) if o.type=='MESH' else None).encode()).hexdigest(),'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []}
before={o.name:fingerprint(o) for o in s.objects if not o.name.startswith('Demo ')}
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
def get(name):return bpy.data.objects[name]
def make(name,loc,dims,mat,rot,origin,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=origin+rot@Vector(loc));o=bpy.context.object;o.name=name;o.rotation_euler=rot.to_euler();o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
 bevel=o.modifiers.new('Fabricated edge','BEVEL');bevel.width=.002;bevel.segments=3
 o['revision']='v4 opposing open counters';return o
for k in [1,2]:
 work=get(f'Demo {k} | Worktop');rot=work.matrix_world.to_quaternion().to_matrix();col=work.users_collection[0];white=work.data.materials[0]
 cross=get(f'Demo {k} | Frame top crossbar');origin=cross.matrix_world.translation.copy();origin.z=0
 topz=work.matrix_world.translation.z;thick=work.dimensions.z;width=work.dimensions.x
 red=next(m for m in bpy.data.materials if 'coral' in m.name.lower()) if any('coral' in m.name.lower() for m in bpy.data.materials) else white
 # Only the old solid cabinet/drawer/worktop parts are replaced. Existing frame and both display faces stay intact.
 for o in list(s.objects):
  if o.name.startswith(f'Demo {k} |') and any(o.name.startswith(f'Demo {k} | '+label) for label in ['Base','Worktop','Drawer']):bpy.data.objects.remove(o,do_unlink=True)
 for sign,label in [(-1,'Front'),(1,'Back')]:
  center=sign*.41;depth=.70;under=topz-thick/2
  make(f'Demo {k} | {label} counter worktop',(0,center,topz),(width,depth,thick),white,rot,origin,col)
  for side in [-1,1]:
   make(f'Demo {k} | {label} side support {side}',(side*(width/2-.035),center,under/2),(.035,depth-.04,under),white,rot,origin,col)
  make(f'Demo {k} | {label} inner modesty panel',(0,sign*.085,under/2),(width-.105,.035,under),white,rot,origin,col)
  make(f'Demo {k} | {label} upper apron',(0,sign*.7375,under-.065),(width-.105,.025,.13),red,rot,origin,col)
bpy.context.view_layer.update()
unchanged=all(name in s.objects and fingerprint(s.objects[name])==value for name,value in before.items())
assert unchanged,'Non-station scene data changed'
manifest=json.loads((ROOT/'Deliverables/v3/screens.json').read_text());manifest['version']=4;(OUT/'screens.json').write_text(json.dumps(manifest,indent=2))
audit={'source':str(source.relative_to(ROOT)),'source_sha256':source_hash,'preserved_non_station_objects':len(before),'non_station_objects_unchanged':unchanged,'countertops_per_station':2,'open_outer_knee_space':True,'note':'Counter depth and panel thickness inferred from annotated photos. Existing worktop height and width retained.'};(OUT/'preservation.json').write_text(json.dumps(audit,indent=2))
s.name='GAMBIT | V4 opposing open demo counters'
# All version folders are siblings, so existing relative movie paths remain valid.
assert all(Path(bpy.path.abspath(im.filepath)).exists() for im in bpy.data.images if im.source=='MOVIE')
for name in ['START HERE']:
 t=bpy.data.texts.get(name)
 if t:t.write('\nV4: both demo stations have two opposing open counters. See project HANDOFF.md.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v4.blend'))
# Review cameras are temporary; keep the user's saved camera and render setup in the editable file.
bpy.ops.object.camera_add(location=(7.5,-5.0,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((3.48,-2.02,1.9))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.6;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.filepath=str(OUT/'01_Station_detail.png');bpy.ops.render.render(write_still=True)
cam.location=(8,-7,4.0);cam.rotation_euler=(Vector((3.48,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.7;s.render.filepath=str(OUT/'02_Both_stations.png');bpy.ops.render.render(write_still=True)
print('V4_COMPLETE',json.dumps(audit))
