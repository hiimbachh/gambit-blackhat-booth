import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Deliverables/v3'; OUT.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
def obj(prefix): return next(o for o in s.objects if o.name.startswith(prefix))
def box(name,loc,dims,mat,collection=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if mat:o.data.materials.append(mat)
 if collection:
  for c in list(o.users_collection):c.objects.unlink(o)
  collection.objects.link(o)
 mod=o.modifiers.new('Small fabricated edge','BEVEL');mod.width=.003;mod.segments=2
 return o
white=obj('Bar | Countertop').data.materials[0]; pink=obj('Merch | Recess').data.materials[0];blue=obj('Bar | Cabinet').data.materials[0]
col=obj('Merch | Recess').users_collection[0]
# Preserve the user's scene; only revise the five requested areas.
# Alternating long sides and short ends replace the tiled lower skin.
for face in 'ABCD':
 for row in range(1,6):
  pieces=[o for o in s.objects if o.name.startswith(f'Base {face} | Row {row} panel')]
  long=(face in 'AC') == (row%2==1)
  if long:
   keep=pieces[0]; axis=0 if face in 'AC' else 1
   keep.location[axis]=-.95 if axis==0 else 0
   keep.dimensions[axis]=2.032 if axis==0 else 1.5367
   keep.name=f'Base {face} | Row {row} long block face'
   for o in pieces[1:]:bpy.data.objects.remove(o,do_unlink=True)
  else:
   # Consistent colour across a course, retaining its separate block ends.
   for o in pieces:o.data.materials.clear();o.data.materials.append(pink if row>1 else blue)
# Raise and compress merchandise display above a real lower cabinet.
for o in list(s.objects):
 if o.name.startswith('Merch |'):
  o.location.z=.93+(o.location.z-.53)*.70
  if any(k in o.name for k in ['Recess backing','Side cheek']):o.dimensions.z*=.70
box('Merch | Lower cabinet',(.31,0,.43),(.49,1.57,.86),white,col)
box('Merch | Lower countertop',(.34,0,.895),(.59,1.63,.07),white,col)
for y in [-.39,.39]:box('Merch | Cabinet door',(.561,y,.45),(.018,.75,.77),white,col)
# Repair the interaction group after its counter was moved independently.
target_x=1.72; original_x=.97
for o in list(s.objects):
 if o.name.startswith('Interaction |'):o.location.x=target_x
for j in [1,2]:
 mount=obj(f'Tablet {j} | Tilt mount');mount.location.x=target_x+.10
 obj(f'Tablet {j} | Stem').location.x=target_x+.07
 bezel=obj(f'Tablet {j} | Bezel');bezel.location=(0,0,0)
 screen=obj('SCREEN_17 |' if j==1 else 'SCREEN_18 |');screen.location=(.018,0,0)
# Hollow L bar: service aisle remains open from the side and in front of door.
obj('Bar | Cabinet body').location.x=-1.73;obj('Bar | Cabinet body').dimensions.x=.50
obj('Bar | Countertop').location.x=-1.73;obj('Bar | Countertop').dimensions.x=.57
for o in list(s.objects):
 if o.name.startswith(('Bar | Inner white cupboard','Bar | Cupboard door','Bar | Cupboard knob')):bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith(('Bar | Bottle','Bar | Tumbler')):o.location.x=-1.72 if 'Bottle' in o.name else -1.88
box('Bar | Rear return cabinet',(-1.00,2.46,.476),(1.0,.54,.952),white,col)
box('Bar | Rear return worktop',(-1.00,2.46,1.003),(1.04,.58,.063),white,col)
# Keep user-selected opposite station orientations; position within footprint.
for k,y in [(1,-2.02),(2,2.02)]:
 frame=obj(f'Demo {k} | Tall frame'); center=frame.matrix_world.translation.copy()
 group=frame.parent; group.location+=Vector((3.48,y,center.z))-center
 bpy.context.view_layer.update()
 frame=obj(f'Demo {k} | Tall frame'); rot=frame.matrix_world.to_quaternion().to_matrix().to_4x4()
 origin=Vector((3.48,y,0)); coll=frame.users_collection[0]
 def station_box(label,local,dims):
  o=box(f'Demo {k} | '+label,origin+rot.to_3x3()@Vector(local),dims,white,coll);o.rotation_euler=rot.to_euler();return o
 bpy.data.objects.remove(frame,do_unlink=True)
 for x in [-.505,.505]:station_box('Full-height frame upright',(x,0,2.02),(.065,.12,4.04))
 station_box('Frame top crossbar',(0,0,4.01),(1.075,.12,.065))
 # Counter projects behind the freestanding portal, as in footage.
 for o in list(s.objects):
  if o.name.startswith(f'Demo {k} |') and any(t in o.name for t in ['Base','Worktop','Drawer']):
   w=o.matrix_world.copy();o.parent=None;o.matrix_world=w
   o.location+=rot.to_3x3()@Vector((0,.30,0))
 # Raise the mesh area slightly above desk displays, preserving all screen IDs.
 for suffix in ['FP','RP']:
  o=obj(f'SCREEN_D{k}{suffix} |');o['structure_note']='Separate mesh panel within floor-standing white portal'
s.name='GAMBIT | V3 user feedback revision'
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1200;s.render.resolution_percentage=100
# Keep movies portable from the new version folder.
for im in bpy.data.images:
 if im.source=='MOVIE':
  absolute=Path(bpy.path.abspath(im.filepath));
  if not absolute.exists():raise RuntimeError('Missing movie '+str(absolute))
  im.filepath=str(absolute)
s.camera=obj('CAM_03');s.frame_set(181)
obj('CAM_04').location.x=.75;obj('CAM_04').data.ortho_scale=10.8
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v3.blend'))
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v3.blend'))
manifest=json.loads((ROOT/'Deliverables/v2/screens.json').read_text());manifest['version']=3
(OUT/'screens.json').write_text(json.dumps(manifest,indent=2))
for cam,name in [('CAM_03','01_Merchandise_and_bar'),('CAM_02','02_Flower_and_blocks'),('CAM_04','03_Plan')]:
 s.camera=obj(cam);s.render.filepath=str(OUT/(name+'.png'))
 hidden=[]
 if cam=='CAM_04':
  for o in s.objects:
   if o.name.startswith(('Sign |','TOWER_','Bar | Canopy','Bar canopy','SCREEN_14','SCREEN_15','SCREEN_16')):
    hidden.append((o,o.hide_render));o.hide_render=True
 bpy.ops.render.render(write_still=True)
 for o,state in hidden:o.hide_render=state
print('V3_COMPLETE')
