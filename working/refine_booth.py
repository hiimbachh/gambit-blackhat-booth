import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path.cwd();OUT=ROOT/'Deliverables';s=bpy.context.scene;tx=-1.05
R=Matrix.Translation((tx,0,0))@Matrix.Rotation(-math.pi/2,4,'Z')@Matrix.Translation((-tx,0,0))
for o in list(s.objects):
 if o.name.startswith(('Bar |','Bar prop |','LED D | Bar','LED E | Bar','Light | Bar','Merchandise |','Rear |','Rear fascia |')):
  o.matrix_world=R@o.matrix_world
 if o.name.startswith(('Welcome |','Tablet |')):o.location.y-=1.25
 if o.name.startswith('Activation |'):o.location.y+=.65
# Move the service door to the free fourth side.
R2=Matrix.Translation((tx,0,0))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation((-tx,0,0))
for o in s.objects:
 if o.name.startswith(('Tower | Service door','Tower | Door handle')):o.matrix_world=R2@o.matrix_world
# The visible monitor material uses clean source media, without guide labels.
im=bpy.data.images.load(str(ROOT/'Ref Material/LED For Booth + Mesh Screen (BlackHat USA 2026)/LED For Booth/LED A/A2.mov'),check_existing=True)
for m in bpy.data.materials:
 if m.name.startswith(('SCREEN | Main display','SCREEN | Demo display')):
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':n.image=im;n.image_user.frame_duration=im.frame_duration
for o in s.objects:
 if o.name.startswith(('65 inch | Animated','Demo 1 | 50 inch','Demo 2 | 50 inch')):
  for uv in o.data.uv_layers.active.data:uv.uv.x=.28+uv.uv.x*.44

# Associate emissive faces with their blocks so optional motion carries the LEDs.
blocks=[o for o in s.objects if o.name.startswith('Upper stack |')]
for o in list(s.objects):
 if o.name.startswith(('LED A','LED B','LED C','LED E2 | Front')):
  block=min(blocks,key=lambda b:(b.location-o.location).length)
  world=o.matrix_world.copy();o.parent=block;o.matrix_world=world
# Add missing reverse LED faces and the broad lower ribbon visible in photos.
col=bpy.data.collections['06 | Screens - linked movies']
for o in list(s.objects):
 if o.name.startswith(('LED B2 | Front','LED C2 | Front')):
  n=o.copy();n.data=o.data.copy();col.objects.link(n);n.parent=None;n.matrix_world=o.matrix_world.copy();n.name=o.name.replace('Front','Reverse')
  n.location.y=2*o.parent.location.y-o.matrix_world.translation.y;n.rotation_euler.z=math.pi
  world=n.matrix_world.copy();n.parent=o.parent;n.matrix_world=world
for o in list(s.objects):
 if o.name.startswith('LED E2 | Front'):
  world=o.matrix_world.copy();o.parent=None;o.matrix_world=world;o.location=(tx,-.96,2.74);o.scale.x=2.02
  n=o.copy();n.data=o.data.copy();col.objects.link(n);n.name='LED E2 | Ribbon - merchandise side';n.location=(tx+1.10,0,2.74);n.scale.x=1.50;n.rotation_euler.z=math.pi/2

# More neutral fabric response prevents the overhead artwork washing out.
for name in ['Empty.009','Empty.006']:
 m=bpy.data.materials.get(name)
 if m and m.use_nodes:
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Roughness'].default_value=.82;bs.inputs['Specular IOR Level'].default_value=.18
def cam(name,loc,target):
 o=bpy.data.objects[name];o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam('CAM 01 | Hero - bar and front',(12,-17,8.2),(-.2,0,3.1))
cam('CAM 02 | Bar and flower',(-15,-8,7.4),(-.8,.3,3.1))
cam('CAM 03 | Merchandise and demos',(12,16,8.2),(-.2,0,3.1))
s.frame_set(181)
# Verify the motion control changes geometry, then restore the still setting.
ctrl=bpy.data.objects['CONTROL | Optional block motion'];ctrl['motion_amount']=0.0;s.frame_set(61);bpy.context.view_layer.update();p0=blocks[0].matrix_world.translation.copy()
ctrl['motion_amount']=1.0;ctrl.update_tag();s.frame_set(62);bpy.context.view_layer.update();p1=blocks[0].matrix_world.translation.copy()
motion=(p1-p0).length
ctrl['motion_amount']=0.0;ctrl.update_tag();s.frame_set(181);bpy.context.view_layer.update()
missing=[]
for image in bpy.data.images:
 if image.source=='MOVIE' and not Path(bpy.path.abspath(image.filepath)).exists():missing.append(image.filepath)
report={'active_scene':s.name,'objects':len(s.objects),'movie_paths_missing':missing,'motion_displacement_m':motion,'cameras':len([o for o in s.objects if o.type=='CAMERA']),'static_motion_amount':ctrl['motion_amount']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
assert not missing and motion>.001,report
guide=bpy.data.texts['START HERE | Scene guide'];body=guide.as_string().replace('Frame 61','Frame 181').replace('branded preview media','branded source media');guide.clear();guide.write(body);(OUT/'README.txt').write_text(body,encoding='utf-8')
s.cycles.samples=64
for cname,fname in [('CAM 01 | Hero - bar and front','01_Hero'),('CAM 02 | Bar and flower','02_Bar'),('CAM 03 | Merchandise and demos','03_Rear')]:
 s.camera=bpy.data.objects[cname];s.render.filepath=str(OUT/(fname+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['CAM 01 | Hero - bar and front'];s.render.filepath=str(OUT/'01_Hero.png')
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_Reconstruction_v1.blend'))
print('REFINEMENT_COMPLETE',report)
