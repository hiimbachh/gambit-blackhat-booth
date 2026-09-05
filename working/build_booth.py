import bpy, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path.cwd(); OUT=ROOT/'Deliverables'; OUT.mkdir(exist_ok=True)
REF=ROOT/'Ref Material'/'LED For Booth + Mesh Screen (BlackHat USA 2026)'
source=bpy.context.scene; source.name='SOURCE | Original supplied scene'
s=bpy.data.scenes.new('GAMBIT | Final booth reconstruction'); bpy.context.window.scene=s
s.unit_settings.system='METRIC'; s.unit_settings.length_unit='METERS'
COL={}
def collection(name):
 c=bpy.data.collections.new(name); s.collection.children.link(c);COL[name]=c;return c
for name in ['01 | Architecture','02 | Tower blocks','03 | Bar and merchandise','04 | Demo stations','05 | Branding','06 | Screens - linked movies','07 | Furniture','08 | Hanging sign - supplied artwork','09 | Cameras and lighting','10 | Animation controls']:
 collection(name)
current=COL['01 | Architecture']
def move(o,name):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 current.objects.link(o);return o
def mat(name,hex,rough=.45,metal=0):
 rgb=[int(hex[i:i+2],16)/255 for i in (0,2,4)]; rgb=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
pink=mat('Gambit | Warm pink','F48EA9'); lightpink=mat('Gambit | Light pink','FFB0C4');red=mat('Gambit | Coral red','EC435D');blue=mat('Gambit | Powder blue','AFCFFD');burgundy=mat('Gambit | Aubergine','2B061B');white=mat('Finish | Warm white','F6F4EF');black=mat('Finish | Screen bezel','12131A',.3);chrome=mat('Finish | Brushed aluminium','C8CBD1',.3,.7);gold=mat('Props | Brass','BFA063',.3,.6)
carpet=mat('Floor | Charcoal carpet','25232A',.94)
n=carpet.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=170
b=carpet.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.008;carpet.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);carpet.node_tree.links.new(b.outputs['Normal'],carpet.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
def box(name,loc,dim,m,bevel=.012):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object,name);o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if m:o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Soft fabrication edges','BEVEL');mod.width=bevel;mod.segments=3
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=move(bpy.context.object,name);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 return o
font=bpy.data.fonts.load('C:/Windows/Fonts/arial.ttf')
italic=bpy.data.fonts.load('C:/Windows/Fonts/ariali.ttf')
def text(name,body,loc,size,m,rot=(math.pi/2,0,0),width=None,ital=False):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.font=italic if ital else font;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=size;cu.extrude=.0025;cu.bevel_depth=.0008
 o=bpy.data.objects.new(name,cu);current.objects.link(o);o.location=loc;o.rotation_euler=rot;cu.materials.append(m);bpy.context.view_layer.update()
 if width and o.dimensions.x>width:o.scale*=width/o.dimensions.x
 return o
def plane(name,loc,w,h,m,rot=(math.pi/2,0,0)):
 bpy.ops.mesh.primitive_plane_add(size=1,location=loc);o=move(bpy.context.object,name);o.scale=(w,h,1);o.rotation_euler=rot;o.data.materials.append(m);return o
def logo(name,loc,size=.45,angle=0):
 # Editable raised emblem: elliptical ring, underline, and four-point sparkle.
 root=bpy.data.objects.new(name,None);current.objects.link(root);root.location=loc;root.rotation_euler.z=angle
 verts=[];faces=[];N=96
 for depth in (0,.045*size):
  for inside in (False,True):
   for i in range(N):
    a=2*math.pi*i/N;u=(.42 if not inside else .22)*math.cos(a);v=(.31 if not inside else .225)*math.sin(a)
    tilt=.57;x=u*math.cos(tilt)-v*math.sin(tilt);z=u*math.sin(tilt)+v*math.cos(tilt)
    verts.append((x*size,-depth,z*size))
 for i in range(N):
  j=(i+1)%N
  faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(white);o=bpy.data.objects.new(name+' / ring',me);current.objects.link(o);o.parent=root
 o=box(name+' / underline',(0,0,0),(.78*size,.032*size,.12*size),white,.002);o.parent=root;o.location=(0,-.009,-.49*size);o.rotation_euler.y=-.17
 pts=[(.48,.52),(.55,.35),(.72,.28),(.55,.21),(.48,.04),(.41,.21),(.24,.28),(.41,.35)]
 me=bpy.data.meshes.new(name+' sparkle');me.from_pydata([(x*size,-.01,z*size) for x,z in pts],[],[tuple(range(8))]);me.materials.append(lightpink);o=bpy.data.objects.new(name+' / sparkle',me);current.objects.link(o);o.parent=root;mod=o.modifiers.new('Raised sparkle','SOLIDIFY');mod.thickness=.025*size
 return root
def brand(loc,width=1.6,angle=0):
 root=logo('Raised Gambit emblem',loc,.42,angle)
 # Text and emblem are separate editable pieces.
 direction=Vector((math.cos(angle),math.sin(angle),0));p=Vector(loc)+direction*(width*.48)
 o=text('Raised Gambit wordmark','Gambit',p,.36,white,width=width*.75);o.rotation_euler.z=angle
 return root

# Carpet uses the workbook's 20 x 30 foot footprint.
box('20 x 30 ft | Carpet footprint',(0,0,-.035),(9.144,6.096,.07),carpet,.01)
tx=-1.05;ty=0
current=COL['02 | Tower blocks']
box('Tower | Interior structural core',(tx,ty,1.25),(1.96,1.46,2.50),pink,.005)
for row in range(5):
 z=.255+row*.49
 if row%2==0:
  for i in range(3):box(f'Tower base | Row {row+1} block {i+1}',(tx,ty+(i-1)*.51,z),(2.035,.503,.482),red if row==0 else (pink if i!=2 else lightpink))
 else:
  for i in range(4):box(f'Tower base | Row {row+1} block {i+1}',(tx+(i-1.5)*.505,ty,z),(.498,1.53,.482),blue if row==3 and i==0 else pink)
# Irregular upper stack follows observed alternation and projected ends.
upper=[]
rows=[(2.74,'x',[-.55,0,.55],[-.32,.18,.45]),(3.24,'y',[-.53,0,.53],[.22,-.18,.38]),(3.74,'x',[-.52,0,.52],[-.28,.38,.12]),(4.24,'y',[-.51,0,.51],[.24,-.18,.4]),(4.74,'x',[-.52,0,.52],[-.4,.15,.32]),(5.24,'y',[-.5,0,.5],[.16,-.2,.4]),(5.74,'x',[-.5,0,.5],[-.22,.18,.33])]
for ri,(z,axis,across,offsets) in enumerate(rows):
 for j,(a,off) in enumerate(zip(across,offsets)):
  loc=(tx+off,ty+a,z) if axis=='x' else (tx+a,ty+off,z)
  dims=(1.51,.492,.482) if axis=='x' else (.492,1.51,.482)
  m=blue if ri==6 else (red if ri in (3,4) and j!=1 else (lightpink if j==1 else pink))
  o=box(f'Upper stack | Level {ri+1} block {j+1}',loc,dims,m);upper.append(o)

current=COL['05 | Branding']
box('Front | Blue logo fascia',(tx,-.789,2.02),(2.08,.065,.48),blue)
brand((tx-.64,-.836,2.07),1.48)
box('Bar side | Pink logo fascia',(tx-1.05,0,1.88),(.065,1.57,.48),pink)
brand((tx-1.095,.5,1.94),1.3,-math.pi/2)
box('Rear | Resilience fascia',(tx,.797,2.7),(1.94,.065,.49),burgundy)
text('Rear fascia | Resilience','Resilience',(tx,.839,2.82),.16,white,rot=(math.pi/2,0,math.pi))
text('Rear fascia | Served Neat','Served Neat',(tx,.839,2.61),.22,lightpink,rot=(math.pi/2,0,math.pi),ital=True)

# Sculpted flower with a domed face, asymmetric petals, and a blue-to-pink finish.
flower=bpy.data.materials.new('Brand flower | Pink centre / blue rim');flower.use_nodes=True
ns=flower.node_tree.nodes;lk=flower.node_tree.links;bs=ns.get('Principled BSDF');bs.inputs['Roughness'].default_value=.32;bs.inputs['Metallic'].default_value=.16
attr=ns.new('ShaderNodeVertexColor');attr.layer_name='Petal gradient';lk.new(attr.outputs['Color'],bs.inputs['Base Color'])
def flower_obj(name,loc,scale,angle=0):
 verts=[(0,-.11,0)];cols=[(.8,.06,.18,1)];N=192;R=16
 lengths=[.58,.92,.77,.62,.88,.7]
 for r in range(1,R+1):
  f=r/R
  for i in range(N):
   a=2*math.pi*i/N;v=(a/(2*math.pi)*6);idx=int(v)%6;t=v-int(v);rad=.21+lengths[idx]*math.sin(math.pi*t)**1.8
   verts.append((math.cos(a)*rad*f,-.105*math.sqrt(max(0,1-f*f)),math.sin(a)*rad*f));q=max(0,min(1,(f-.42)/.58));cols.append((.8*(1-q)+.3*q,.065*(1-q)+.55*q,.19*(1-q)+.95*q,1))
 faces=[]
 for i in range(N):faces.append((0,1+i,1+(i+1)%N))
 for r in range(R-1):
  for i in range(N):a=1+r*N+i;b=1+r*N+(i+1)%N;faces.append((a,a+N,b+N,b))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(flower);co=me.color_attributes.new(name='Petal gradient',type='FLOAT_COLOR',domain='POINT')
 for i,c in enumerate(cols):co.data[i].color=c
 o=bpy.data.objects.new(name,me);current.objects.link(o);o.location=loc;o.scale=(scale,scale,scale);o.rotation_euler.z=angle
 for p in me.polygons:p.use_smooth=True
 sol=o.modifiers.new('Dimensional emblem thickness','SOLIDIFY');sol.thickness=.035
 return o
flower_obj('Bar side | Raised flower',(tx-1.096,-.03,.85),.77,-math.pi/2)

current=COL['06 | Screens - linked movies']
movies={}
def movie(key,path):
 m=bpy.data.materials.new('SCREEN | '+key);m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();out=ns.new('ShaderNodeOutputMaterial');e=ns.new('ShaderNodeEmission');e.inputs['Strength'].default_value=1.0;t=ns.new('ShaderNodeTexImage');im=bpy.data.images.load(str(path),check_existing=True);t.image=im;t.image_user.use_auto_refresh=True;t.image_user.use_cyclic=True;t.image_user.frame_duration=max(1,im.frame_duration);t.image_user.frame_start=1
 m.node_tree.links.new(t.outputs['Color'],e.inputs['Color']);m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);movies[key]=dict(path=str(path),duration=im.frame_duration);return m
def led(name,loc,w,h,key,path,angle=0):
 m=movie(key,path);return plane(name,loc,w,h,m,(math.pi/2,0,angle))
for level,key in [(0,'E'),(4,'B'),(5,'C'),(6,'A')]:
 obs=upper[level*3:(level+1)*3]
 for j,o in enumerate(obs):
  if j==1 or level==6:
   x,y,z=o.location;dx,dy,dz=o.dimensions
   # LED faces mounted flush on corresponding visible block surfaces.
   part='2' if j==1 else '1';p=REF/'LED For Booth'/('LED '+key)/(key+part+'.mov')
   led(f'LED {key}{part} | Front block face',(x,y-dy/2-.003,z),dx-.006,dz-.006,key+part,p)
   if level==6:led('LED A1 | End cap',(x+dx/2+.004,y,z),dy-.006,dz-.006,'A1',REF/'LED For Booth/LED A/A1.mov',math.pi/2)
# Main 65-inch display, with supplied branded moving content.
box('65 inch | Display bezel',(tx,-.833,1.43),(1.466,.073,.84),black,.022)
led('65 inch | Animated display',(tx,-.876,1.43),1.426,.802,'Main display - Preview A',REF/'LED For Booth/LED A/Preview A.mp4')

current=COL['03 | Bar and merchandise']
bx=tx-2.02
box('Bar | Lower blue cabinet',(bx,0,.45),(1.98,1.02,.90),blue)
for i in range(4):box('Bar | Blue panel '+str(i+1),(bx+(i-1.5)*.49,-.527,.25),(.483,.028,.49),blue)
box('Bar | White countertop',(bx,-.01,1.005),(2.08,1.13,.065),white)
box('Bar | Upper canopy',(bx,.0,2.5),(2.08,1.10,.07),white)
box('Bar | Outer support',(bx-.96,.04,1.73),(.065,1.01,1.49),white)
box('Bar | Back shelving wall',(bx,.47,1.69),(1.92,.06,1.55),white)
for z in [1.25,1.66,2.06]:box('Bar | Shelf',(bx,.30,z),(1.9,.37,.038),white)
for x in [bx-.72,bx-.15,bx+.43]:
 for z in [1.38,1.79,2.19]:
  for j in range(3):box('Bar prop | Boxed tumbler',(x+j*.12,.3,z),(.10,.13,.20),gold,.003)
for i in range(8):
 x=bx-.76+i*.21;cyl('Bar prop | Bottle body',(x,-.03,1.15),.036,.23,gold if i%2 else burgundy);cyl('Bar prop | Bottle neck',(x,-.03,1.29),.017,.07,black)
for i in range(5):cyl('Bar prop | Cup',(bx-.2+i*.17,-.34,1.105),.044,.13,white)
current=COL['06 | Screens - linked movies']
led('LED D | Bar fascia',(bx,-.55,.745),1.94,.46,'D2',REF/'LED For Booth/LED D/D2.mov')
led('LED E | Bar canopy',(bx,-.54,2.77),1.93,.46,'E2',REF/'LED For Booth/LED E/E2.mov')

current=COL['03 | Bar and merchandise']
box('Merchandise | Pink shelving back',(tx,.82,1.42),(1.92,.075,1.72),pink)
for x in [tx-.96,tx+.96]:box('Merchandise | Side cheek',(x,1.01,1.39),(.045,.43,1.8),pink)
for z in [.52,.91,1.30,1.69,2.08]:box('Merchandise | Shelf',(tx,1.02,z),(1.94,.45,.038),pink)
random.seed(8)
for z in [.63,1.02]:
 for i in range(4):
  for j in range(3):box('Merchandise | Folded shirt',(tx-.71+i*.46,1.03,z+j*.035),(.41,.30,.03),pink if i%2 else lightpink,.012)
for z in [1.42,1.81,2.20]:
 for i in range(7):box('Merchandise | Gift box',(tx-.80+i*.265,1.02,z),(.23,.20,.19),gold,.004)
# Tower service door on opposite side.
box('Tower | Service door',(tx+1.032,0,1.14),(.018,.79,2.20),pink,.002)
o=box('Tower | Door handle',(tx+1.06,-.29,1.11),(.045,.12,.025),chrome,.006)

current=COL['04 | Demo stations']
for k,(x,y) in enumerate([(3.12,-1.85),(3.12,1.8)],1):
 box(f'Demo {k} | White base',(x,y,.43),(1.10,.91,.86),white)
 box(f'Demo {k} | Worktop',(x,y,.90),(1.21,1.03,.055),white)
 box(f'Demo {k} | Tall frame',(x,y,2.32),(1.045,.115,3.72),white)
 for side in [-1,1]:
  angle=0 if side==-1 else math.pi
  current=COL['06 | Screens - linked movies']
  led(f'Demo {k} | Mesh animated panel {side}',(x,y+side*.065,2.85),.923,2.53,'Mesh screen',REF/'Mesh Screen/Mesh Screen.mov',angle)
  box(f'Demo {k} | Monitor bezel {side}',(x,y+side*.115,1.26),(1.10,.065,.64),black,.016)
  led(f'Demo {k} | 50 inch screen {side}',(x,y+side*.153,1.26),1.057,.594,'Demo display',REF/'LED For Booth/LED A/Preview A.mp4',angle)
  current=COL['04 | Demo stations']
  box(f'Demo {k} | Drawer {side}',(x,y+side*.467,.70),(.94,.022,.16),white,.003)
  box(f'Demo {k} | Drawer pull {side}',(x,y+side*.483,.72),(.20,.012,.014),chrome,.004)

current=COL['07 | Furniture']
for row in range(2):
 for i in range(3):
  x=tx-.65+i*.66;y=-1.68-row*.67
  box(f'Audience | Ottoman {row*3+i+1}',(x,y,.23),(.51,.51,.46),white,.045)
  box('Ottoman | Seat piping',(x,y,.435),(.514,.514,.012),white,.005)
box('Welcome | Cabinet',(1.03,.35,.45),(1.18,.69,.90),white)
box('Welcome | Countertop',(1.03,.35,.94),(1.28,.78,.06),white)
for x in [.79,1.25]:
 box('Welcome | Tablet stand',(x,.22,1.06),(.045,.10,.19),chrome)
 o=box('Welcome | Tablet',(x,.18,1.25),(.26,.028,.36),black,.018);o.rotation_euler.x=math.radians(15)
 current=COL['05 | Branding'];text('Tablet | Gambit','Gambit',(x,.154,1.25),.045,white);current=COL['07 | Furniture']
# Compact machine cabinet seen beside merchandise; simplified secondary prop.
box('Activation | White pedestal',(tx+1.61,.65,.47),(.77,.72,.94),white)
amber=mat('Props | Amber machine enclosure','D5841A',.24,.15)
box('Activation | Machine enclosure',(tx+1.61,.68,1.29),(.54,.46,.67),amber,.035)
box('Activation | Machine control panel',(tx+1.61,.438,1.30),(.27,.018,.32),black,.01)

# Reuse original packed hanging-sign artwork and geometry at real-world dimensions.
current=COL['08 | Hanging sign - supplied artwork']
names=['Plane.003','Empty.007','Empty.008','Empty.010','Empty.011','Empty.012','Empty.014','Empty.015','Empty.016']
factor=5.7912/.503003
origin=Vector((-.01465,-.09073,.73054));target=Vector((tx,0,6.05))
T=Matrix.Translation(target)@Matrix.Scale(factor,4)@Matrix.Translation(-origin)
for name in names:
 old=bpy.data.objects.get(name)
 if old:
  o=old.copy();o.data=old.data.copy();current.objects.link(o);o.parent=None;o.matrix_world=T@old.matrix_world;o.name='Hanging sign | '+name;o.hide_render=False;o.hide_set(False)
for x in [tx-2.76,tx+2.76]:
 for y in [-2.76,2.76]:cyl('Rigging | Suspension cable',(x,y,7.72),.006,1.8,chrome)

current=COL['10 | Animation controls']
ctrl=bpy.data.objects.new('CONTROL | Optional block motion',None);current.objects.link(ctrl);ctrl['motion_amount']=0.0;ctrl.id_properties_ui('motion_amount').update(min=0,max=1,description='0 = still / built position. 1 = subtle looping motion on upper blocks only. Screens play independently.')
for i,o in enumerate(upper):
 axis=0 if i//3%2==0 else 1;f=o.driver_add('location',axis);d=f.driver;v=d.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["motion_amount"]';base=o.location[axis];phase=(i%3)*2.094
 d.expression=f'{base:.6f}+amount*0.025*(sin((frame-1)*2*pi/240+{phase:.6f})-sin({phase:.6f}))'
s.frame_start=1;s.frame_end=240;s.render.fps=30
for f,label in [(1,'STILL | Built position'),(61,'Screen motion | 2 seconds'),(121,'Screen motion | 4 seconds'),(240,'8 second loop end')]:s.timeline_markers.new(label,frame=f)

current=COL['09 | Cameras and lighting']
def camera(name,loc,target,lens=45,ortho=None):
 bpy.ops.object.camera_add(location=loc);o=move(bpy.context.object,name);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
 if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
 return o
hero=camera('CAM 01 | Hero - bar and front',(12,-17,11),(-.25,0,3.2),48)
barcam=camera('CAM 02 | Bar and flower',(-12,-14,7),(-1.15,0,2.9),48)
rear=camera('CAM 03 | Merchandise and demos',(11,16,9),(-.25,0,3.1),48)
plan=camera('CAM 04 | Plan',(0,0,17),(0,0,0),ortho=10.3)
walk=camera('CAM 05 | Optional slow walkthrough',(9,-11,2.0),(-.5,0,2.0),35)
for frame,loc,targ in [(1,(9,-11,2),(-.5,0,2)),(120,(6,-8,2),(-1,0,2.4)),(240,(2,-6,2),(-1,0,2.6))]:
 walk.location=loc;walk.rotation_euler=(Vector(targ)-walk.location).to_track_quat('-Z','Y').to_euler();walk.keyframe_insert(data_path='location',frame=frame);walk.keyframe_insert(data_path='rotation_euler',frame=frame)
def area(name,loc,power,size,color,target):
 bpy.ops.object.light_add(type='AREA',location=loc);o=move(bpy.context.object,name);o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Light | Key',(0,-6,10),2300,7,(1,.9,.88),(0,0,2))
area('Light | Fill',(-6,-1,6),1700,6,(.85,.91,1),(-1,0,2))
area('Light | Rear',(1,5,10),2600,6,(1,.94,.9),(0,0,3))
area('Light | Tower',(-1,0,5.9),180,2,(1,1,1),(-1,0,2))
area('Light | Bar under canopy',(bx,0,2.44),35,1.2,(1,.81,.54),(bx,0,1))
s.world=bpy.data.worlds.new('World | Neutral studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.23,.25,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True
s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.camera=hero;s.frame_set(61)
# Set a useful opening viewport.
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.clip_end=1000
README='''GAMBIT BLACK HAT | RECONSTRUCTION V1
Editable presentation reconstruction from the supplied Blender file, LinkedIn final-booth video, on-site photographs, and preliminary graphics workbook.

OPEN: GAMBIT | Final booth reconstruction. The untouched supplied objects remain in the separate SOURCE scene for comparison.
STILLS: CAM 01-04. Frame 61 is the opening hero setup. Cycles, AgX, 48 samples; use 128+ for final close-ups.
SCREENS: movie textures use Auto Refresh and Cyclic playback. Scrub the timeline in Material Preview or Rendered view. Movie assets remain linked to ../Ref Material; keep that folder beside Deliverables when moving this project. Static source images and fonts are packed.
BLOCK MOTION: Select CONTROL | Optional block motion in collection 10; set custom property motion_amount from 0 to 1. Default 0 preserves the built position. Upper blocks only move subtly in an eight-second loop. The hanging sign and architecture remain fixed.
WALKTHROUGH: Choose CAM 05 for a keyed eight-second slow approach. It is optional; hero cameras are static.
SCALE: meters; floor 9.144 x 6.096m; hanging sign approximately 5.791 x 5.791 x 1.524m. Other measurements use preliminary workbook sizes and photo estimates.
LIMITS: This is a visual reconstruction, not fabrication documentation. Fine offsets, unseen details, props, flower silhouette and raised wordmark are reconstructed approximations. Demo and 65-inch monitors use supplied branded preview media as stand-ins for unavailable actual demo screen recordings. LED face assignment is inferred from supplied labels and observed views and should be checked against a final LED map. No hypothetical Figma notes override the final on-site references.
'''
t=bpy.data.texts.new('START HERE | Scene guide');t.write(README);(OUT/'README.txt').write_text(README,encoding='utf-8')
for im in bpy.data.images:
 if im.source!='MOVIE' and im.has_data and not im.packed_file:
  try:im.pack()
  except:pass
for f in bpy.data.fonts:
 if f.filepath:
  try:f.pack()
  except:pass
dest=OUT/'Gambit_BlackHat_Reconstruction_v1.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(dest))
(OUT/'screen_manifest.json').write_text(json.dumps(movies,indent=2))
for cam,name in [(hero,'01_Hero'),(barcam,'02_Bar'),(rear,'03_Rear')]:
 s.camera=cam;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=hero;s.render.filepath=str(OUT/'01_Hero.png');bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print('BUILD_AND_RENDERS_COMPLETE')
