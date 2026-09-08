"""Render four native 60 fps shots and high-resolution stills from the presentation copy."""
import bpy,sys,json,time
from pathlib import Path
s=bpy.context.scene;out=Path(bpy.data.filepath).parent
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.use_persistent_data=True
s.cycles.denoiser='OPTIX';s.cycles.denoising_use_gpu=True
manifest=json.loads((out/'render_manifest.json').read_text())
for i,shot in enumerate(manifest['shots']):
 name=shot['name'];s.frame_set(147+i*780)
 s.render.resolution_percentage=200;s.cycles.samples=64
 s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=str(out/(name+'.png'))
 if not Path(s.render.filepath).exists():bpy.ops.render.render(write_still=True)
 s.render.resolution_percentage=100;s.cycles.samples=24
 s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
 s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE'
 s.frame_start=1+i*780;s.frame_end=(i+1)*780
 s.render.filepath=str(out/(name+'.mp4'));s.render.use_file_extension=True
 if not (out/(name+'.done')).exists():
  bpy.ops.render.render(animation=True)
  (out/(name+'.done')).write_text('Complete: 780 native frames at 60 fps\n')
 print('SHOT_COMPLETE',name,flush=True)
print('ALL_RENDERING_COMPLETE',flush=True)


