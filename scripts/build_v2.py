"""Run with Blender from the repository root against the supplied base .blend."""
import bpy,math,json,sys,addon_utils
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'scripts/boothlib.py').read_text(),globals())
tx=0.;ty=0.
current=COL['01 | Architecture']
box('Floor | 20 x 30 feet',(0,0,-.035),(9.144,6.096,.07),carpet,.008)
current=COL['02 | Tower blocks']
box('Tower core | 80 x 60.5 x 95 inches',(0,0,1.2065),(2.032,1.5367,2.413),pink,.004)
for face in ['A','B','C','D']:
 for row in range(5):
  for j in range(3 if face in ['B','D'] else 4):
   isx=face in ['B','D'];n=3 if isx else 4;span=1.5367 if isx else 2.032;u=(j-(n-1)/2)*span/n;z=.244+row*.481
   tint=red if row==0 else (blue if row==3 and j==0 else pink)
   sign=1 if face in ['B','C'] else -1
   loc=(sign*1.02,u,z) if isx else (u,sign*.773,z)
   dims=(.026,span/n-.008,.473) if isx else (span/n-.008,.026,.473)
   box(f'Base {face} | Row {row+1} panel {j+1}',loc,dims,tint,.004)
current=COL['01 | Architecture']
box('Tower | White upper trim',(0,0,2.427),(2.14,1.64,.055),white,.004)
# A is the monitor side (-Y); B merchandise (+X); C service (+Y); D flower (-X).
# Five main tiers derived from the multi-view photographs, with alternating bar axes.
current=COL['02 | Tower blocks'];blocks=[]
layers=[('X',[-.50,0,.50],[.15,-.32,.10]),('Y',[-.50,0,.50],[-.25,.25,-.38]),('X',[-.50,0,.50],[.30,-.36,.05]),('Y',[-.50,0,.50],[-.22,.0,.18]),('X',[-.50,0,.50],[.34,-.08,-.28])]
for level,(axis,lanes,shifts) in enumerate(layers):
 for j,(lane,shift) in enumerate(zip(lanes,shifts)):
  z=2.702+level*.4953;loc=(shift,lane,z) if axis=='X' else (lane,shift,z)
  dim=(1.487,.493,.488) if axis=='X' else (.493,1.487,.488)
  tint=blue if level==4 else (red if level==2 else pink)
  o=box(f'TOWER_L{level+1}_B{j+1} | {axis} axis',loc,dim,tint,.004)
  o['tier']=level+1;o['reference']='IMG_2990 / IMG_3304 / IMG_2989';blocks.append(o)

# Exact supplied SVG geometry, including the wordmark and pink sparkle.
current=COL['05 | Branding'];addon_utils.enable('io_curve_svg',default_set=False)
before=set(bpy.data.objects);bpy.ops.import_curve.svg(filepath=str(ROOT/'Ref Material/Logo/pink star.svg'))
logo_objects=list(set(bpy.data.objects)-before)
bpy.context.view_layer.update();coords=[o.matrix_world@Vector(v) for o in logo_objects for v in o.bound_box]
mn=Vector(tuple(min(p[i] for p in coords) for i in range(3)));mx=Vector(tuple(max(p[i] for p in coords) for i in range(3)));center=(mn+mx)/2
logo_data=[]
for o in logo_objects:
 world=o.matrix_world.copy();logo_data.append((o.data.copy(),world))
 bpy.data.objects.remove(o,do_unlink=True)
def exact_logo(name,loc,width,angle=0):
 root=bpy.data.objects.new(name,None);current.objects.link(root);root.location=loc;root.rotation_euler=(math.pi/2,0,angle)
 scale=width/(mx.x-mn.x)
 for i,(data,world) in enumerate(logo_data):
  cu=data.copy();cu.dimensions='2D';cu.resolution_u=16;cu.extrude=.009/scale;cu.bevel_depth=.0007/scale;cu.bevel_resolution=2
  o=bpy.data.objects.new(name+f' / SVG path {i+1:02}',cu);current.objects.link(o);o.parent=root;o.matrix_basis=Matrix.Scale(scale,4)@Matrix.Translation(-center)@world
 return root
box('A | Blue logo panel',(0,-.804,2.10),(2.04,.04,.49),blue,.005)
exact_logo('BRAND_A | Supplied SVG',(0,-.835,2.11),1.42)
box('D | Pink logo panel',(-1.056,0,1.94),(.042,1.53,.49),pink,.005)
exact_logo('BRAND_D | Supplied SVG',(-1.091,0,1.94),1.34,-math.pi/2)

# Actual supplied flower image on an alpha-traced, physically extruded silhouette.
flower_meta=json.loads((ROOT/'Assets/Brand/flower_contour.json').read_text());uv=flower_meta['contour_uv'];fw=1.40;fh=fw/flower_meta['aspect']
verts=[((u-.5)*fw,(v-.5)*fh,0) for u,v in uv]
from mathutils.geometry import tessellate_polygon
vectors=[Vector(v) for v in verts];tris=tessellate_polygon([vectors]);lookup={tuple(v):i for i,v in enumerate(vectors)};faces=[tuple(v if isinstance(v,int) else lookup[tuple(v)] for v in tri) for tri in tris]
mesh=bpy.data.meshes.new('Flower | Traced supplied alpha');mesh.from_pydata(verts,[],faces);mesh.uv_layers.new(name='Source artwork UV')
for poly in mesh.polygons:
 for loopidx in poly.loop_indices:mesh.uv_layers.active.data[loopidx].uv=uv[mesh.loops[loopidx].vertex_index]
fm=bpy.data.materials.new('Flower | Supplied artwork');fm.use_nodes=True;bs=fm.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.48
im=bpy.data.images.load(str(ROOT/'Assets/Brand/flower_2048.png'));im.pack();node=fm.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;fm.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
mesh.materials.append(fm);flower=bpy.data.objects.new('FLOWER | Exact source silhouette and artwork',mesh);current.objects.link(flower);flower.location=(-1.105,0,.86);flower.rotation_euler=(math.pi/2,0,-math.pi/2)
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
mod=flower.modifiers.new('Fabricated relief depth','SOLIDIFY');mod.thickness=.026;mod.offset=-1
flower['source']='Ref Material/Flower/flower.png';flower['silhouette_method']='Alpha contour; no generated replacement'

current=COL['06 | Screens - linked movies'];screen_records=[]
def media_mat(sid,clip):
 m=bpy.data.materials.new('MEDIA_'+sid);m.use_nodes=True;nd=m.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');out.location=(460,0);em=nd.new('ShaderNodeEmission');em.location=(200,0);em.inputs['Strength'].default_value=1.0
 tex=nd.new('ShaderNodeTexImage');tex.name='REPLACE_MEDIA';tex.label='Replace this image or movie';tex.location=(-160,0);tex.image=bpy.data.images.load(str(clip),check_existing=True)
 tex.image_user.use_auto_refresh=True;tex.image_user.use_cyclic=True;tex.image_user.frame_start=1;tex.image_user.frame_duration=max(1,tex.image.frame_duration)
 m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);return m
def screen(sid,label,loc,w,h,clip,angle=0,parent=None,refs=()):
 o=plane('SCREEN_'+sid+' | '+label,loc,w,h,media_mat(sid,clip),(math.pi/2,0,angle))
 o['screen_id']=sid;o['screen_label']=label;o['loop']=True;o['reference_annotations']=', '.join(refs);o['replace_media']='Shading > MEDIA_'+sid+' > REPLACE_MEDIA, or use Screen Manager'
 if parent:
  bpy.context.view_layer.update()
  world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
 screen_records.append({'id':sid,'object':o.name,'label':label,'width_m':w,'height_m':h,'references':list(refs),'media':str(clip.relative_to(ROOT)).replace('\\','/'),'loop':True})
 return o
def clip(code):return REF/'LED For Booth'/('LED '+code[0])/(code+'.mov')
def face(sid,label,block,normal,code,refs=()):
 x,y,z=block.location;dx,dy,dz=block.dimensions
 if normal=='X+':return screen(sid,label,(x+dx/2+.003,y,z),dy-.006,dz-.006,clip(code),math.pi/2,block,refs)
 if normal=='X-':return screen(sid,label,(x-dx/2-.003,y,z),dy-.006,dz-.006,clip(code),-math.pi/2,block,refs)
 if normal=='Y+':return screen(sid,label,(x,y+dy/2+.003,z),dx-.006,dz-.006,clip(code),math.pi,block,refs)
 return screen(sid,label,(x,y-dy/2-.003,z),dx-.006,dz-.006,clip(code),0,block,refs)
face('01','Top blue end',blocks[12],'X+','A1',['I2.3','I4.8'])
face('02','Top opposite end',blocks[14],'X-','A1')
face('03','Top long media face',blocks[12],'Y-','A2')
face('04','Upper dotted long face - bar',blocks[9],'X-','B2',['I1.1','I2.4'])
face('05','Upper dotted long face - merchandise',blocks[11],'X+','B2',['I3.2','I4.6'])
face('06','Upper dotted return end',blocks[11],'Y+','B1',['I3.3'])
face('07','Red block animated long face',blocks[6],'Y-','C2',['I2.2','I4.7'])
face('08','Red block animated return',blocks[6],'X-','C1',['I1.2'])
face('09','Red block reverse media face',blocks[8],'Y+','C2')
# Broad LED over the merchandise face, including its short return.
box('LED ribbon | Backing',(1.072,0,2.702),(.075,1.55,.49),black,.002)
screen('10','Merchandise LED ribbon',(1.114,0,2.702),1.54,.483,clip('E2'),math.pi/2,refs=['I2.5','I3.1','I4.1'])
screen('11','Merchandise ribbon return',(.86,-.782,2.702),.47,.483,clip('E1'),refs=[])
box('Main monitor | 65 inch bezel',(0,-.841,1.39),(1.455,.065,.835),black,.009)
screen('12','65 inch main monitor',(0,-.879,1.39),1.422,.800,clip('A2'),refs=['I2.1'])

# L-shaped serving station on C/D corner. Its front aligns with the flower wall.
current=COL['03 | Bar and merchandise'];barx=-.29;bary=1.76
box('Bar | Cabinet body',(barx,bary,.476),(1.49,1.98,.952),blue,.006)
box('Bar | Countertop',(barx,bary,1.003),(1.56,2.055,.063),white,.004)
for j in range(4):box('Bar | Front blue panel '+str(j+1),(-1.05,bary+(j-1.5)*.492,.26),(.022,.485,.50),blue,.003)
box('Bar | Canopy',(barx,bary,2.427),(1.56,2.055,.055),white,.004)
# Outer end has shelves; the remainder is open so people and the scene can be seen through it.
box('Bar | Outer end wall',(barx,2.734,1.71),(1.49,.055,1.39),white,.004)
box('Bar | Shelf column backing',(.37,2.40,1.71),(.055,.65,1.39),white,.004)
for z in [1.33,1.72,2.11]:box('Bar | Display shelf',(-.26,2.40,z),(1.25,.63,.025),white,.003)
for y in [2.23,2.42,2.61]:
 for z in [1.46,1.85,2.24]:
  box('Bar | Boxed glass',(-.16,y,z),(.14,.15,.20),gold,.004)
for j in range(7):
 y=.98+j*.19;cyl('Bar | Bottle',(-.38,y,1.155),.034,.245,gold if j%2 else burgundy);cyl('Bar | Bottle neck',(-.38,y,1.30),.016,.06,black)
for j in range(5):cyl('Bar | Tumbler',(-.77,1.01+j*.17,1.107),.043,.13,white)
box('Bar | Inner white cupboard',(.34,1.71,.53),(.20,1.37,.89),white,.004)
for y in [1.40,2.03]:box('Bar | Cupboard door',(.45,y,.54),(.025,.61,.79),white,.004);cyl('Bar | Cupboard knob',(.48,y,.74),.014,.025,chrome)
current=COL['06 | Screens - linked movies']
screen('13','Bar counter LED front',(-1.066,bary,.748),1.94,.46,clip('D2'),-math.pi/2,refs=['I1.3'])
box('Bar canopy | LED backing',(-.29,2.45,2.702),(1.50,.63,.49),black,.002)
screen('14','Bar canopy long LED',(-1.049,2.45,2.702),.63,.48,clip('E1'),-math.pi/2,refs=['I1.4'])
screen('15','Bar canopy outer long LED',(-.29,2.774,2.702),1.49,.48,clip('E2'),math.pi,refs=['I4.2'])
screen('16','Bar canopy return LED',(.469,2.45,2.702),.63,.48,clip('E1'),math.pi/2,refs=['I4.3'])

current=COL['03 | Bar and merchandise']
# Merchandise shelves are on the narrow B face, immediately behind the interaction counter.
box('Merch | Recess backing',(1.06,0,1.31),(.05,1.46,1.52),pink,.004)
for y in [-.75,.75]:box('Merch | Side cheek',(1.26,y,1.31),(.43,.045,1.56),pink,.004)
for z in [.53,.90,1.27,1.64,2.01]:box('Merch | Shelf',(1.26,0,z),(.43,1.52,.032),pink,.004)
for z in [.62,.98]:
 for j in range(3):
  for k in range(3):box('Merch | Folded shirt',(1.25,-.49+j*.49,z+k*.04),(.32,.44,.034),pink if j%2 else lightpink,.010)
for z in [1.38,1.75,2.13]:
 for j in range(5):box('Merch | Branded box',(1.26,-.60+j*.30,z),(.21,.26,.16),gold,.003)
current=COL['05 | Branding']
for z in [1.38,1.75,2.13]:
 for j in range(5):text('Merch | Box label','Gambit',(1.373,-.60+j*.30,z),.040,burgundy,rot=(math.pi/2,0,math.pi/2))
current=COL['01 | Architecture']
box('C | Service door',(.20,.791,1.15),(.87,.024,2.22),pink,.003)
box('C | Door recess border',(.20,.785,1.15),(.91,.010,2.26),burgundy,.002)
box('C | Lever handle',(.51,.817,1.00),(.14,.025,.021),chrome,.005)

current=COL['07 | Furniture']
for row in range(2):
 for j in range(3):box(f'Seating | Ottoman {row*3+j+1}',(-.65+j*.64,-1.53-row*.67,.23),(.51,.51,.46),white,.038)
# One counter contains the two angled tablets and the engraving machine, as in images 3/4.
box('Interaction | Long counter',(1.92,.16,.465),(.78,2.00,.93),white,.006)
box('Interaction | Countertop',(1.92,.16,.97),(.86,2.07,.06),white,.003)
for j,y in enumerate([-.50,.05],1):
 box('Tablet '+str(j)+' | Stem',(1.99,y,1.09),(.11,.06,.23),chrome,.005)
 mount=bpy.data.objects.new('Tablet '+str(j)+' | Tilt mount',None);current.objects.link(mount);mount.location=(2.02,y,1.27);mount.rotation_euler.y=math.radians(-18)
 o=box('Tablet '+str(j)+' | Bezel',(0,0,0),(.026,.31,.44),black,.012);o.parent=mount;o.location=(0,0,0)
 current=COL['06 | Screens - linked movies']
 o=screen('17' if j==1 else '18','Interaction tablet '+str(j),(2.039,y,1.27),.285,.411,REF/'Mesh Screen/Mesh Screen.mov',math.pi/2,refs=['I4.5' if j==1 else 'I4.4'])
 bpy.context.view_layer.update();o.parent=mount;o.matrix_parent_inverse=Matrix.Identity(4);o.location=(.018,0,0);o.rotation_euler=(math.pi/2,0,math.pi/2);o.scale=(.285,.411,1)
 current=COL['07 | Furniture']
amber=mat('Machine | Amber enclosure','C67512',.22,.10)
box('Machine | White lower base',(1.88,.81,1.065),(.59,.57,.16),white,.015)
box('Machine | Amber cover',(1.79,.87,1.47),(.47,.55,.68),amber,.018)
box('Machine | Metal ventilation column',(2.14,.87,1.34),(.22,.43,.72),chrome,.014)
for j in range(12):box('Machine | Vent slat',(2.258,.87,1.16+j*.035),(.004,.34,.008),black,.001)
box('Machine | Control display',(2.261,.87,1.61),(.006,.23,.075),black,.004)

# Two double-sided demo stations occupy the opposite open side of the booth.
current=COL['04 | Demo stations']
for k,(x,y) in enumerate([(3.34,-1.74),(3.34,1.72)],1):
 box(f'Demo {k} | Base',(x,y,.42),(1.07,.92,.84),white,.006)
 box(f'Demo {k} | Worktop',(x,y,.877),(1.16,1.02,.055),white,.004)
 box(f'Demo {k} | Tall frame',(x,y,2.22),(1.03,.10,3.59),white,.004)
 for side in [-1,1]:
  angle=0 if side==-1 else math.pi
  current=COL['06 | Screens - linked movies']
  screen(f'D{k}{"F" if side==-1 else "R"}P',f'Demo {k} portrait panel',(x,y+side*.057,2.69),.927,2.49,REF/'Mesh Screen/Mesh Screen.mov',angle)
  box(f'Demo {k} | Monitor bezel {side}',(x,y+side*.11,1.22),(1.10,.06,.64),black,.010)
  screen(f'D{k}{"F" if side==-1 else "R"}M',f'Demo {k} monitor',(x,y+side*.145,1.22),1.058,.595,clip('A2'),angle)
  current=COL['04 | Demo stations']
  box(f'Demo {k} | Drawer {side}',(x,y+side*.464,.64),(.91,.020,.19),white,.004)

current=COL['08 | Hanging sign - supplied artwork']
# Retain supplied sign artwork, lower it to the photographed relationship with the tower.
origin=Vector((-.01465,-.09073,.6643));factor=5.7912/.503003
T=Matrix.Translation((0,0,4.60))@Matrix.Scale(factor,4)@Matrix.Translation(origin*-1)
for name in ['Plane.003','Empty.007','Empty.008','Empty.010','Empty.011','Empty.012','Empty.014','Empty.015','Empty.016']:
 old=bpy.data.objects.get(name)
 if old:
  o=old.copy();o.data=old.data.copy();current.objects.link(o);o.parent=None;o.matrix_world=T@old.matrix_world;o.name='Sign | '+name;o.hide_render=False;o.hide_set(False)
for x in [-2.76,2.76]:
 for y in [-2.76,2.76]:cyl('Sign | Suspension cable',(x,y,6.6),.004,1.6,chrome)

current=COL['10 | Animation controls']
ctrl=bpy.data.objects.new('CONTROL | Upper block motion',None);current.objects.link(ctrl);ctrl['motion_amount']=0.;ctrl.id_properties_ui('motion_amount').update(min=0,max=1,description='0 locks the photographed assembly. 1 enables subtle optional movement.')
for i,o in enumerate(blocks):
 axis=0 if i//3%2==0 else 1;f=o.driver_add('location',axis);v=f.driver.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["motion_amount"]';f.driver.expression=f'{o.location[axis]:.6f}+amount*.015*(sin((frame-1)*2*pi/240+{i%3*2.094:.4f})-sin({i%3*2.094:.4f}))'
s.frame_start=1;s.frame_end=240;s.render.fps=30

current=COL['09 | Cameras and lighting']
def camera(name,loc,target,lens=48,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=move(bpy.context.object,name);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
hero=camera('CAM_01 | Monitor and merchandise',(11,-14,7.8),(.65,0,2.7),48)
barcam=camera('CAM_02 | Flower and serving station',(-12,-8,6.0),(.1,.4,2.6),48)
rear=camera('CAM_03 | Merchandise and service',(12,11,6.4),(.7,.3,2.5),48)
plan=camera('CAM_04 | Orthographic floor plan',(0,0,15),(0,0,0),ortho=10.2)
photoa=camera('CAM_05 | Photo A comparison',(4.2,-6.6,1.7),(0,0,2.55),30)
photod=camera('CAM_06 | Photo D comparison',(-6,-.3,1.65),(0,.4,2.55),30)
walk=camera('CAM_07 | Walkthrough',(7,-8,1.7),(0,0,2.3),30)
for frame,loc in [(1,(7,-8,1.7)),(240,(3,-5,1.7))]:walk.location=loc;walk.rotation_euler=(Vector((0,0,2.2))-walk.location).to_track_quat('-Z','Y').to_euler();walk.keyframe_insert(data_path='location',frame=frame);walk.keyframe_insert(data_path='rotation_euler',frame=frame)
def area(name,loc,power,size,target):
 bpy.ops.object.light_add(type='AREA',location=loc);o=move(bpy.context.object,name);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Light | Key',(0,-6,9),2100,7,(0,0,2));area('Light | Bar',(-5,1,7),1800,5,(0,1,2));area('Light | Rear',(2,6,8),2100,6,(0,0,2));area('Light | Below sign',(0,0,4.55),90,2,(0,0,1))
for y in [1.16,1.86,2.48]:area('Light | Bar downlight',(-.5,y,2.389),8,.13,(-.5,y,1))
s.world=bpy.data.worlds.new('World | Neutral');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.21,.23,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.view_settings.view_transform='AgX';s.render.resolution_x=1500;s.render.resolution_y=1350;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.camera=hero;s.frame_set(181)
for screen_ui in bpy.data.screens:
 for a in screen_ui.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
manifest={'version':2,'primary_reference':'Four on-site photos; user annotations supersede video','screens':screen_records}
(OUT/'screens.json').write_text(json.dumps(manifest,indent=2))
for im in bpy.data.images:
 if im.source!='MOVIE' and im.has_data and not im.packed_file:
  try:im.pack()
  except:pass
for f in bpy.data.fonts:
 try:f.pack()
 except:pass
# Original source stays in Ref Material, rather than bloating the active production scene.
bpy.data.scenes.remove(source)
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
guide=bpy.data.texts.new('START HERE');guide.write('PHOTO RECONSTRUCTION V2\nSee HANDOFF.md at project root.\nScreen objects are named SCREEN_<ID>. All have a material MEDIA_<ID> with REPLACE_MEDIA texture. Movie looping is enabled.\nTo use the convenient screen picker: open SCREEN_MANAGER.py in the Text Editor and Run Script; then use N sidebar > Booth Screens.\nBlock movement defaults to zero. Primary references are the four photos, not the LinkedIn video.\n')
if (ROOT/'scripts/screen_manager.py').exists():bpy.data.texts.load(str(ROOT/'scripts/screen_manager.py'))
# Centre the overall installation across the 30-foot footprint.
for o in s.objects:
 if o.parent is None and o.type!='LIGHT' and not o.name.startswith('Floor |'):
  o.location.x-=.95
  if o.animation_data:
   for f in o.animation_data.drivers:
    if f.data_path=='location' and f.array_index==0:f.driver.expression='('+f.driver.expression+')-.95'
s.render.filepath=str(OUT/'01_Hero.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v2.blend'));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v2.blend'))
for cam,name in [(hero,'01_Hero'),(barcam,'02_Flower_Bar'),(rear,'03_Merchandise'),(plan,'04_Plan')]:
 s.camera=cam;s.render.filepath=str(OUT/(name+'.png'))
 hidden=[]
 if cam==plan:
  for o in s.objects:
   if o.name.startswith(('Sign |','TOWER_L','SCREEN_0','CONTROL |')) or o.get('screen_id','') in ['10','11']:
    hidden.append((o,o.hide_render));o.hide_render=True
 bpy.ops.render.render(write_still=True)
 for o,state in hidden:o.hide_render=state
s.camera=hero;s.render.filepath=str(OUT/'01_Hero.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v2.blend'))
print('V2_BUILD_COMPLETE',len(screen_records),'screen surfaces')
