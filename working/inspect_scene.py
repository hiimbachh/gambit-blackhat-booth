import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
data=[]
for o in s.objects:
 data.append(dict(name=o.name,visible=not o.hide_render,hidden=o.hide_get(),parent=o.parent.name if o.parent else None,materials=[m.name if m else '' for m in getattr(o.data,'materials',[])],bounds=[list(o.matrix_world@Vector(v)) for v in o.bound_box] if o.type=='MESH' else []))
Path('working/scene_details.json').write_text(json.dumps(data,indent=2))
bpy.ops.object.camera_add(location=(1.25,-1.8,1.1))
c=bpy.context.object;c.rotation_euler=(Vector((0,-.1,.38))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=1.3;s.camera=c
s.render.engine='CYCLES';s.cycles.samples=16
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.filepath=str(Path('working/base_preview.png').resolve())
bpy.ops.render.render(write_still=True)
