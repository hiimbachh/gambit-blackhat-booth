"""Decode roof movie textures at their boundary frames in a disposable scene."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Deliverables/v4.1'
screens=list(bpy.data.collections['Roof | Replaceable display faces'].objects)
materials=[o.active_material for o in screens]
# Render tiny swatches to force Blender to evaluate the movie image users.
scene=bpy.data.scenes.new('Temporary movie boundary check');bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.resolution_x=64;scene.render.resolution_y=64;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(0,0,2));scene.camera=bpy.context.object;scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=1
bpy.ops.mesh.primitive_plane_add(size=1);plane=bpy.context.object
records=[];scratch=ROOT/'working/roof_loop_check';scratch.mkdir(parents=True,exist_ok=True)
for mat in materials:
 plane.data.materials.clear();plane.data.materials.append(mat);n=mat.node_tree.nodes['REPLACE_MEDIA'];length=n.image_user.frame_duration
 samples=[];hashes={}
 for label,frame,offset in [('start',1,0),('last',length,0),('restart',length+1,0),('last_reference',1,length-1)]:
  n.image_user.frame_offset=offset;scene.frame_set(frame)
  path=scratch/(mat.name.replace('|','_')+'_'+label+'.png');scene.render.filepath=str(path)
  bpy.ops.render.render(write_still=True,scene=scene.name)
  im=bpy.data.images.load(str(path),check_existing=False);pixel_hash=hashlib.sha256(str(list(im.pixels)).encode()).hexdigest();bpy.data.images.remove(im)
  hashes[label]=pixel_hash;samples.append({'test':label,'timeline_frame':frame,'offset':offset,'decoded_pixel_sha256':pixel_hash})
 n.image_user.frame_offset=0
 assert hashes['start']==hashes['restart'],(mat.name,'Loop did not return to first frame')
 assert hashes['last']==hashes['last_reference'],(mat.name,'Last frame mismatch')
 records.append({'material':mat.name,'clip':n.image.name,'frames':length,'samples':samples})
(OUT/'loop_boundary_check.json').write_text(json.dumps({'status':'passed','checks':records},indent=2));print('LOOP_BOUNDARIES_PASSED')
