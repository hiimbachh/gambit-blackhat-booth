"""Run once in Blender's Text Editor; N sidebar > Booth Screens. No auto-execution."""
import bpy
from bpy.props import StringProperty,EnumProperty
from bpy_extras.io_utils import ImportHelper

def entries(self,context):
 return [(o.name,o.get('screen_id','')+' - '+o.get('screen_label',o.name),'') for o in context.scene.objects if 'screen_id' in o] or [('NONE','No screens','')]
def selected(context):return bpy.data.objects.get(context.scene.booth_screen)
def texture(o):
 return o.active_material.node_tree.nodes.get('REPLACE_MEDIA') if o and o.active_material else None
class BOOTH_OT_select(bpy.types.Operator):
 bl_idname='booth.select_screen';bl_label='Select screen'
 def execute(self,context):
  o=selected(context)
  if not o:return {'CANCELLED'}
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);context.view_layer.objects.active=o;return {'FINISHED'}
class BOOTH_OT_media(bpy.types.Operator,ImportHelper):
 bl_idname='booth.replace_media';bl_label='Choose image or looping video';bl_options={'REGISTER','UNDO'}
 filter_glob:StringProperty(default='*.mp4;*.mov;*.webm;*.avi;*.png;*.jpg;*.jpeg',options={'HIDDEN'})
 def execute(self,context):
  o=selected(context);n=texture(o)
  if not n:self.report({'ERROR'},'Select a screen first');return {'CANCELLED'}
  try:im=bpy.data.images.load(self.filepath,check_existing=False)
  except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
  im.filepath=bpy.path.relpath(im.filepath);n.image=im;n.image_user.frame_start=1;n.image_user.frame_duration=max(1,im.frame_duration);n.image_user.use_cyclic=True;n.image_user.use_auto_refresh=True
  if im.source!='MOVIE':im.pack()
  self.report({'INFO'},'Media replaced. Use Material Preview or Rendered view and play the timeline.');return {'FINISHED'}
class BOOTH_PT_screens(bpy.types.Panel):
 bl_label='Booth Screens';bl_idname='BOOTH_PT_screens';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Booth Screens'
 def draw(self,context):
  layout=self.layout;layout.prop(context.scene,'booth_screen',text='Display');layout.operator('booth.select_screen');layout.operator('booth.replace_media')
  n=texture(selected(context))
  if n and n.image:
   layout.label(text=n.image.name)
   if n.image.source=='MOVIE':layout.prop(n.image_user,'use_cyclic',text='Loop');layout.prop(n.image_user,'frame_start',text='Start frame');layout.prop(n.image_user,'frame_duration',text='Clip frames')
  layout.label(text='GIF: convert to MP4 or a PNG sequence first.')
classes=(BOOTH_OT_select,BOOTH_OT_media,BOOTH_PT_screens)
def register():
 for old in bpy.app.driver_namespace.get('GAMBIT_SCREEN_CLASSES',()):
  try:bpy.utils.unregister_class(old)
  except RuntimeError:pass
 for cls in classes:bpy.utils.register_class(cls)
 bpy.app.driver_namespace['GAMBIT_SCREEN_CLASSES']=classes
 bpy.types.Scene.booth_screen=EnumProperty(name='Screen',items=entries)
if __name__=='__main__':register()
