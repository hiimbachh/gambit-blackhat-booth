"""Add a photo-based roof to the user-edited v4; preserve the accepted booth."""
import bpy, json, math, hashlib, sys, os
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from scene_audit import object_state, material, digest
OUT=ROOT/'Deliverables/v4.1';OUT.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;source=Path(bpy.data.filepath)
ROOF_OLD={'SCREEN_02 | Top opposite end','SCREEN_04 | Upper dotted long face - bar','SCREEN_06 | Upper dotted return end','SCREEN_08 | Red block animated return'}
baseline={o.name:object_state(o) for o in s.objects if o.name not in ROOF_OLD}
(OUT/'preservation_baseline.json').write_text(json.dumps({name:digest(state) for name,state in baseline.items()},indent=2))
original_frame=s.frame_current
collection=bpy.data.collections.new('Roof | Photo-based stacked blocks');s.collection.children.link(collection)
screens_col=bpy.data.collections.new('Roof | Replaceable display faces');collection.children.link(screens_col)
def relink(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o)
def block(name,loc,dims,finish):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;relink(o,collection);o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(bpy.data.materials[finish]);bevel=o.modifiers.new('Fabricated edge','BEVEL');bevel.width=.004;bevel.segments=3
 o['reference']='IMG_3343, IMG_2990, IMG_3304, IMG_2989';return o
# Five alternating courses with separated/offset bars visible in all four photos.
# Two visible bars per course; hidden dimensions are inferred, not fabrication data.
roof_z=2.4545;height=.488;pitch=.491;blocks=[]
specs=[('X',[-.48,.48],[.15,-.20],'Gambit | Warm pink'),('Y',[-.48,.48],[-.27,.10],'Gambit | Warm pink'),('X',[-.48,.48],[.28,-.24],'Gambit | Coral red'),('Y',[-.48,.48],[-.16,.20],'Gambit | Warm pink'),('X',[-.48,.48],[.23,-.28],'Gambit | Powder blue')]
for tier,(axis,lanes,shifts,finish) in enumerate(specs,1):
 row=[]
 for j,(lane,shift) in enumerate(zip(lanes,shifts),1):
  x,y=(shift,lane) if axis=='X' else (lane,shift)
  dims=(1.50,.50,height) if axis=='X' else (.50,1.50,height)
  o=block(f'ROOF_L{tier}_B{j} | {axis} bar',(-.95+x,y,roof_z+height/2+(tier-1)*pitch),dims,finish)
  o['tier']=tier;o['roof_block_id']=f'L{tier}B{j}';row.append(o)
 blocks.append(row)
def film(code):return ROOT/'Ref Material/LED For Booth + Mesh Screen (BlackHat USA 2026)'/'LED For Booth'/('LED '+code[0])/(code+'.mov')
def screen(sid,label,parent,normal,code,existing=None):
 if existing:o=bpy.data.objects[existing];relink(o,screens_col)
 else:
  bpy.ops.mesh.primitive_plane_add(size=1);o=bpy.context.object;o.name=f'SCREEN_{sid} | {label}';relink(o,screens_col)
 m=bpy.data.materials.new('Roof media | '+sid+' | '+code);m.use_nodes=True;nd=m.node_tree.nodes;nd.clear()
 out=nd.new('ShaderNodeOutputMaterial');em=nd.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1
 tex=nd.new('ShaderNodeTexImage');tex.name='REPLACE_MEDIA';tex.label=label
 tex.image=bpy.data.images.load(str(film(code)),check_existing=False);tex.image.filepath='//../../'+str(film(code).relative_to(ROOT)).replace('\\','/')
 tex.image_user.frame_start=1;tex.image_user.frame_duration=max(1,tex.image.frame_duration);tex.image_user.use_cyclic=True;tex.image_user.use_auto_refresh=True
 m.node_tree.links.new(tex.outputs['Color'],em.inputs[0]);m.node_tree.links.new(em.outputs[0],out.inputs[0]);o.data.materials.clear();o.data.materials.append(m)
 dx,dy,dz=parent.dimensions
 if normal=='X+':p=(dx/2+.002,0,0);w,h=dy-.004,dz-.004;angle=math.pi/2
 elif normal=='X-':p=(-dx/2-.002,0,0);w,h=dy-.004,dz-.004;angle=-math.pi/2
 elif normal=='Y+':p=(0,dy/2+.002,0);w,h=dx-.004,dz-.004;angle=math.pi
 else:p=(0,-dy/2-.002,0);w,h=dx-.004,dz-.004;angle=0
 o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.location=p;o.rotation_euler=(math.pi/2,0,angle);o.scale=(w,h,1)
 o['screen_id']=sid;o['screen_label']=label;o['loop']=True;o['replace_media']='Roof media / REPLACE_MEDIA';return o
# Roof-only assignments follow supplied guides: A logo, D nested red, E dots.
# B grid media on the user's two lower roof ribbons remains untouched.
screen('02','Top blue opposite logo',blocks[4][1],'X-','A1','SCREEN_02 | Top opposite end')
screen('R01','Top blue logo end',blocks[4][0],'X+','A1')
screen('04','Upper dotted bar-side long face',blocks[3][0],'X-','E2','SCREEN_04 | Upper dotted long face - bar')
screen('06','Upper dotted return end',blocks[3][1],'Y+','E1','SCREEN_06 | Upper dotted return end')
screen('R05','Upper dotted merchandise long face',blocks[3][1],'X+','E2')
screen('R06','Upper dotted bar-side return',blocks[3][0],'Y-','E1')
screen('08','Red animated end',blocks[2][0],'X-','D2','SCREEN_08 | Red block animated return')
screen('R07','Red animated long face',blocks[2][0],'Y-','D1')
# Reuse the existing opt-in motion control without changing its saved value.
ctrl=bpy.data.objects.get('CONTROL | Upper block motion')
for row in blocks:
 for j,o in enumerate(row):
  axis=0 if o['tier']%2 else 1;base=o.location[axis]
  if ctrl:
   f=o.driver_add('location',axis);v=f.driver.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["motion_amount"]'
   phase=j*2.094;f.driver.expression=f'{base:.9f}+amount*.015*(sin((frame-1)*2*pi/240+{phase})-sin({phase}))'
bpy.context.view_layer.update()
assert all(object_state(s.objects[n])==d for n,d in baseline.items()),'Accepted scene changed'
# Only zero-user datablocks are removed. Used materials are not merged or renamed.
removed={}
for kind in ['meshes','curves','materials','images','node_groups']:
 data=getattr(bpy.data,kind);names=[]
 for item in list(data):
  if item.users==0 and not item.use_fake_user:names.append(item.name);data.remove(item)
 removed[kind]=names
report={'source':'Deliverables/v4/'+source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'preserved_objects':len(baseline),'all_non_roof_objects_unchanged':True,'roof_objects_repositioned':sorted(ROOF_OLD),'roof_blocks':10,'roof_media_faces':8,'removed_zero_user_data':removed,'note':'Photo-inferred roof spacing. Used non-roof materials and all existing non-roof media/static choices preserved.'}
(OUT/'preservation.json').write_text(json.dumps(report,indent=2))
catalog={'version':'4.1','screens':[],'materials':[]}
for o in s.objects:
 if 'screen_id' not in o:continue
 m=o.active_material;n=m.node_tree.nodes.get('REPLACE_MEDIA') if m and m.node_tree else None
 catalog['screens'].append({'id':o['screen_id'],'object':o.name,'label':o.get('screen_label',o.name),'material':m.name if m else None,'mode':n.image.source.lower() if n and n.image else 'static','media':n.image.filepath if n and n.image else None,'material_shared':m.users>1 if m else False})
for m in bpy.data.materials:catalog['materials'].append({'name':m.name,'objects':[o.name for o in s.objects if hasattr(o.data,'materials') and m.name in o.data.materials]})
(OUT/'assets.json').write_text(json.dumps(catalog,indent=2));(OUT/'screens.json').write_text(json.dumps({'version':'4.1','screens':catalog['screens'],'note':'Current object names are authoritative; user-created duplicate legacy IDs are retained.'},indent=2))
s.name='GAMBIT | V4.1 roof addition'
guide=bpy.data.texts.get('START HERE')
if guide:guide.write('\nV4.1: photo-based central roof added. User v4 materials and static/looping screen choices preserved below roof. See assets.json and HANDOFF.md.\n')
assert all(Path(bpy.path.abspath(i.filepath)).exists() for i in bpy.data.images if i.source=='MOVIE' and i.users)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v4.1.blend'))
# Cameras and render settings below are preview-only, never saved over user setup.
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1300;s.render.resolution_y=1400;s.render.resolution_percentage=100
for name,loc,target,scale in [('01_Roof_merchandise',(4,5,1.7),(-.95,0,3.65),3.5),('02_Roof_flower',(-6,-5,1.7),(-.95,0,3.65),3.5),('03_Overall',(9,10,4.0),(.35,.4,2.7),10.6)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
 s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('V41_COMPLETE',json.dumps(report))
