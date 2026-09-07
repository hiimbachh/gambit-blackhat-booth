"""Reopen v4.1, check preservation and clip timing; never save test mutations."""
import bpy,json,sys,math,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from scene_audit import object_state,digest
from media_metadata import video_timing
s=bpy.context.scene;OUT=ROOT/'Deliverables/v4.1'
before=json.loads((OUT/'preservation_baseline.json').read_text())
failures=[n for n,d in before.items() if n not in s.objects or digest(object_state(s.objects[n]))!=d]
assert not failures,failures
roof=[o for o in s.objects if 'roof_block_id' in o];assert len(roof)==10
roof_screens=list(bpy.data.collections['Roof | Replaceable display faces'].objects);assert len(roof_screens)==8
timings=[]
for o in roof_screens:
 n=o.active_material.node_tree.nodes['REPLACE_MEDIA'];p=Path(bpy.path.abspath(n.image.filepath));meta=video_timing(p)
 assert abs(meta['fps']-s.render.fps/s.render.fps_base)<1e-6
 assert n.image_user.frame_duration==meta['frames']==n.image.frame_duration
 assert n.image_user.frame_start==1 and n.image_user.frame_offset==0
 assert n.image_user.use_auto_refresh and n.image_user.use_cyclic
 assert s.frame_end>=meta['frames'] and n.image.filepath.startswith('//')
 assert o.parent in roof
 timings.append({'object':o.name,'clip':p.name,**meta,'configured_frames':n.image_user.frame_duration})
# Existing static choices and movie frame counts are covered by full fingerprints.
for im in bpy.data.images:
 if im.users and im.source=='MOVIE':assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
assert not [m.name for m in bpy.data.materials if m.users==0 and not m.use_fake_user]
ctrl=bpy.data.objects['CONTROL | Upper block motion'];saved=ctrl['motion_amount'];original_frame=s.frame_current
ctrl['motion_amount']=0.;ctrl.update_tag();s.frame_set(1);bpy.context.view_layer.update();base={o.name:o.matrix_world.translation.copy() for o in roof}
ctrl['motion_amount']=1.;ctrl.update_tag();s.frame_set(61);bpy.context.view_layer.update();motion=max((o.matrix_world.translation-base[o.name]).length for o in roof);assert .001<motion<.04
ctrl['motion_amount']=0.;ctrl.update_tag();s.frame_set(1);bpy.context.view_layer.update();assert max((o.matrix_world.translation-base[o.name]).length for o in roof)<1e-5
ctrl['motion_amount']=saved;ctrl.update_tag();s.frame_set(original_frame)
report={'status':'passed','preserved_non_roof_objects':len(before),'non_roof_geometry_transforms_materials_and_playback_unchanged':True,'roof_blocks':len(roof),'new_roof_display_faces':len(roof_screens),'scene_fps':s.render.fps/s.render.fps_base,'scene_timeline':[s.frame_start,s.frame_end],'roof_clip_timing':timings,'relative_media_resolves':True,'unused_materials_remaining':0,'optional_roof_motion_metres':motion,'note':'Validation mutations are not saved. Existing static and shared materials intentionally retained.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print('VALIDATION_PASSED',json.dumps(report))
