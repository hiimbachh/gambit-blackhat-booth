"""Presentation cameras and render-only settings; preserve the approved model."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from scene_audit import object_state,digest
s=bpy.context.scene;OUT=ROOT/'Deliverables/presentation';OUT.mkdir(parents=True,exist_ok=True)
source=Path(bpy.data.filepath);before={o.name:digest(object_state(o)) for o in s.objects}
collection=bpy.data.collections.new('Presentation | Cameras');s.collection.children.link(collection)
shots=[('01_Monitor_and_stations',(10,-13,5.3),(.35,.2,2.75),32),('02_Flower_and_bar',(-11,-8,4.5),(-.65,.5,2.8),30),('03_Merchandise_and_service',(10,12,4.8),(.7,.6,2.75),32),('04_Roof_detail',(4.5,-6.2,1.85),(-.95,0,3.7),49)]
for i,(name,loc,target,lens) in enumerate(shots):
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name='PRESENTATION | '+name;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=200
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o)
 marker=s.timeline_markers.new(name,frame=1+i*780);marker.camera=o
s.camera=bpy.data.objects['PRESENTATION | '+shots[0][0]]
s.render.fps=60;s.render.fps_base=1;s.frame_start=1;s.frame_end=3120
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.denoiser='OPTIX';s.cycles.denoising_use_gpu=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
assert all(digest(object_state(s.objects[n]))==v for n,v in before.items())
report={'source':'Deliverables/v4.2/'+source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'all_original_objects_unchanged':True,'original_objects':len(before),'fps':60,'seconds_per_shot':13,'shot_frames':780,'shots':[dict(name=n,location=l,target=t,lens_mm=f) for n,l,t,f in shots],'note':'Only presentation cameras and render settings added. Existing material/geometry/movie timing preserved.'}
(OUT/'render_manifest.json').write_text(json.dumps(report,indent=2));(OUT/'source_fingerprints.json').write_text(json.dumps(before,indent=2))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Gambit_Presentation.blend'))
# Trial stills at video quality to inspect framing and estimate animation speed.
s.frame_set(147)
for i,(name,_,_,_) in enumerate(shots):
 s.frame_set(147+i*780);s.camera=bpy.data.objects['PRESENTATION | '+name];s.render.filepath=str(OUT/(name+'_preview.png'));bpy.ops.render.render(write_still=True)
print('PRESENTATION_PREPARED')


