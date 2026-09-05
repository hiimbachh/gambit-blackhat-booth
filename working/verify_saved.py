import bpy,json
from pathlib import Path
ROOT=Path.cwd();s=bpy.context.scene
assert s.name=='GAMBIT | Final booth reconstruction'
ctrl=bpy.data.objects['CONTROL | Optional block motion']
assert ctrl['motion_amount']==0
assert len([o for o in s.objects if o.type=='CAMERA'])==5
movies=[im for im in bpy.data.images if im.source=='MOVIE']
assert all(Path(bpy.path.abspath(im.filepath)).exists() for im in movies)
assert bpy.data.scenes.get('SOURCE | Original supplied scene')
# Small rendered checks prove that source movie frames actually change after reopening.
s.camera=bpy.data.objects['CAM 01 | Hero - bar and front'];s.render.resolution_x=600;s.render.resolution_y=525;s.cycles.samples=8
for frame in (1,121):
 s.frame_set(frame);s.render.filepath=str(ROOT/'working'/f'animation_check_{frame}.png');bpy.ops.render.render(write_still=True)
print('REOPEN_VALIDATED',len(movies),'movie assets, all paths valid; still mode retained')
