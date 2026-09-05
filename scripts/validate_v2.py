import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
root=Path.cwd();s=bpy.context.scene
screens=[o for o in s.objects if 'screen_id' in o]
assert len(screens)==26,len(screens)
manifest=json.loads((root/'Deliverables/v2/screens.json').read_text())
expected={f'I{i}.{j}' for i,n in [(1,4),(2,5),(3,3),(4,8)] for j in range(1,n+1)}
actual={ref for item in manifest['screens'] for ref in item['references']}
assert actual==expected,(actual,expected)
assert len({o.active_material.name for o in screens})==26
for o in screens:
 n=o.active_material.node_tree.nodes['REPLACE_MEDIA']
 assert n.image_user.use_cyclic and n.image_user.use_auto_refresh
 assert Path(bpy.path.abspath(n.image.filepath)).exists(),n.image.filepath
 assert n.image.filepath.startswith('//'),n.image.filepath
 normal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
 assert abs(normal.z)<.4,(o.name,tuple(normal))
blocks=[o for o in s.objects if o.name.startswith('TOWER_L')]
assert len(blocks)==15
ctrl=bpy.data.objects['CONTROL | Upper block motion']
base={o.name:o.matrix_world.translation.copy() for o in blocks}
ctrl['motion_amount']=1.;ctrl.update_tag();s.frame_set(61);bpy.context.view_layer.update()
motion=max((o.matrix_world.translation-base[o.name]).length for o in blocks)
assert 0.001<motion<.04,motion
ctrl['motion_amount']=0.;ctrl.update_tag();s.frame_set(181);bpy.context.view_layer.update()
assert max((o.matrix_world.translation-base[o.name]).length for o in blocks)<1e-5
helper=runpy.run_path(str(root/'scripts/screen_manager.py'));helper['register']()
s.booth_screen=screens[0].name
assert bpy.ops.booth.select_screen()=={'FINISHED'}
assert bpy.context.view_layer.objects.active==screens[0]
before={o.name:o.active_material.node_tree.nodes['REPLACE_MEDIA'].image for o in screens}
assert bpy.ops.booth.replace_media(filepath=str(root/'Assets/Brand/flower_2048.png'))=={'FINISHED'}
assert screens[0].active_material.node_tree.nodes['REPLACE_MEDIA'].image!=before[screens[0].name]
assert all(o.active_material.node_tree.nodes['REPLACE_MEDIA'].image==before[o.name] for o in screens[1:])
helper['register']()
report={'status':'passed','screen_surfaces':26,'photo_annotations_covered':20,'upper_blocks':15,'movie_files_resolve':True,'movie_paths_relative':True,'independent_screen_replacement':True,'screen_helper_repeat_registration':True,'screen_orientation_checked':True,'optional_motion_metres_at_test_frame':motion,'objects':len(s.objects),'mesh_faces':sum(len(o.data.polygons) for o in s.objects if o.type=='MESH'),'blender':bpy.app.version_string,'note':'Validation changes are intentionally not saved into the production blend.'}
(root/'Deliverables/v2/validation.json').write_text(json.dumps(report,indent=2))
print('VALIDATION_PASSED',json.dumps(report))
