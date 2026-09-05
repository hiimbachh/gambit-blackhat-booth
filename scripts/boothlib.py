import bpy, math, json, random
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path.cwd(); OUT=ROOT/'Deliverables'/'v2'; OUT.mkdir(parents=True,exist_ok=True)
REF=ROOT/'Ref Material'/'LED For Booth + Mesh Screen (BlackHat USA 2026)'
source=bpy.context.scene; source.name='SOURCE | Original supplied scene'
s=bpy.data.scenes.new('GAMBIT | Photo reconstruction v2'); bpy.context.window.scene=s
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
font=bpy.data.fonts.load('C:/Windows/Fonts/arial.ttf') if Path('C:/Windows/Fonts/arial.ttf').exists() else bpy.data.fonts.get('Bfont')
italic=bpy.data.fonts.load('C:/Windows/Fonts/ariali.ttf') if Path('C:/Windows/Fonts/ariali.ttf').exists() else font
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

