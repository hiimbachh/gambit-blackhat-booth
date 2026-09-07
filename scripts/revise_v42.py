"""Correct individual roof directions from the multi-view onsite references."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from scene_audit import object_state,digest,material
s=bpy.context.scene;OUT=ROOT/'Deliverables/v4.2';OUT.mkdir(parents=True,exist_ok=True)
roof=[o for o in s.objects if 'roof_block_id' in o]
screens=list(bpy.data.collections['Roof | Replaceable display faces'].objects)
excluded={o.name for o in roof+screens}
before={o.name:digest(object_state(o)) for o in s.objects if o.name not in excluded}
media_before={o.name:digest(material(o.active_material)) for o in screens}
(OUT/'preservation_baseline.json').write_text(json.dumps(before,indent=2))
# Each tuple is centre offset from the tower, plus plan rotation relative to its
# original X/Y long axis. Bars stay level; diagonal appearance is not fake tilt.
# Fore/aft ordering is inferred jointly from A-monitor and B-merchandise views.
poses={
 'L1B1':(-.23,-.29,0), 'L1B2':(.06,.28,0),
 'L2B1':(-.30,-.39,20), 'L2B2':(.27,.12,20),
 'L3B1':(.02,-.37,-32), 'L3B2':(.36,.25,-32),
 'L4B1':(-.35,-.24,8), 'L4B2':(.25,.38,8),
 'L5B1':(.44,.34,-5), 'L5B2':(-.45,-.30,8),
}
ctrl=bpy.data.objects['CONTROL | Upper block motion']
for o in roof:
 x,y,angle=poses[o['roof_block_id']]
 if o.animation_data:
  for driver in list(o.animation_data.drivers):o.driver_remove(driver.data_path,driver.array_index)
 o.location.x=-.95+x;o.location.y=y;o.rotation_euler.z=math.radians(angle)
 # Retain the same opt-in, low-amplitude motion and static setting.
 axis=0 if o['tier']%2 else 1;base=o.location[axis];j=int(o['roof_block_id'][-1])-1;phase=j*2.094
 f=o.driver_add('location',axis);v=f.driver.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["motion_amount"]'
 f.driver.expression=f'{base:.9f}+amount*.015*(sin((frame-1)*2*pi/240+{phase})-sin({phase}))'
 o['reference_note']='Individually offset/turned from IMG_2990, IMG_3304, IMG_2989 and user close-up; unseen dimensions inferred.'
# The square red animation is on the projecting merchandise-side end in the
# onsite photo, not the opposite end used by v4.1. Its movie/timing is unchanged.
end=bpy.data.objects['SCREEN_08 | Red block animated return'];end.location.x=.752;end.rotation_euler.z=math.pi/2
bpy.context.view_layer.update()
assert all(digest(object_state(s.objects[n]))==d for n,d in before.items())
assert all(digest(material(s.objects[n].active_material))==d for n,d in media_before.items())
report={'source':'Deliverables/v4.1/Gambit_BlackHat_v4.1.blend','source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'preserved_non_roof_objects':len(before),'non_roof_unchanged':True,'all_roof_materials_and_media_timing_unchanged':True,'roof_media_baseline':media_before,'individual_roof_poses':poses,'note':'Photo-based fit; rotations/offsets are inferred, not measured. Red D2 end moved to +X local face. Existing static/loop choices and scene fps retained.'}
(OUT/'preservation.json').write_text(json.dumps(report,indent=2))
for name in ['assets.json','screens.json']:
 data=json.loads((ROOT/'Deliverables/v4.1'/name).read_text());data['version']='4.2';(OUT/name).write_text(json.dumps(data,indent=2))
s.name='GAMBIT | V4.2 individual roof directions';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_BlackHat_v4.2.blend'))
# Perspective cameras reproduce the low viewing angles that reveal the stagger.
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='PERSP';cam.data.lens=48
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1300;s.render.resolution_percentage=100
for name,loc,target,lens in [('01_Monitor_side_reference',(2.5,-4.2,1.8),(-.95,0,3.7),56),('02_Merchandise_side_reference',(4.2,1.2,1.7),(-.95,0,3.75),46),('03_Flower_side_reference',(-5.6,-.7,1.7),(-.95,0,3.75),42)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('V42_COMPLETE')
