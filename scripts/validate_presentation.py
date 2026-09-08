import bpy,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from scene_audit import object_state,digest
out=Path(bpy.data.filepath).parent;s=bpy.context.scene
baseline=json.loads((out/'source_fingerprints.json').read_text())
changed=[n for n,v in baseline.items() if n not in s.objects or digest(object_state(s.objects[n]))!=v]
missing=[i.filepath for i in bpy.data.images if i.source in {'FILE','MOVIE'} and i.filepath and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()]
markers=[{'frame':m.frame,'camera':m.camera.name} for m in s.timeline_markers if m.camera]
report={'original_objects':len(baseline),'changed_original_objects':changed,'missing_media':missing,'fps':s.render.fps/s.render.fps_base,'frames':s.frame_end-s.frame_start+1,'camera_cuts':markers}
assert not changed and not missing
assert report['fps']==60 and report['frames']==3120
(out/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
