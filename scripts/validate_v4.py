import bpy,json,hashlib,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
s=bpy.context.scene
for k in [1,2]:
 tops=[o for o in s.objects if o.name.startswith(f'Demo {k} |') and 'counter worktop' in o.name]
 assert len(tops)==2
 center=bpy.data.objects[f'Demo {k} | Frame top crossbar'].matrix_world.translation
 axis=tops[0].matrix_world.to_quaternion().to_matrix()@Vector((0,1,0))
 sides=[(o.matrix_world.translation-center).dot(axis) for o in tops]
 assert min(sides)<-.3 and max(sides)>.3,sides
 assert not any(o.name==f'Demo {k} | Base' for o in s.objects)
 for label in ['Front','Back']:
  assert sum(o.name.startswith(f'Demo {k} | {label} side support') for o in s.objects)==2
  apron=bpy.data.objects[f'Demo {k} | {label} upper apron']
  assert apron.location.z-apron.dimensions.z/2>.65
pres=json.loads((ROOT/'Deliverables/v4/preservation.json').read_text())
assert hashlib.sha256((ROOT/pres['source']).read_bytes()).hexdigest()==pres['source_sha256']
# Run the existing meaningful media and movement checks against this version.
code=(ROOT/'scripts/validate_v3.py').read_text().replace('Deliverables/v3/','Deliverables/v4/')
exec(compile(code,'validate_v4_media','exec'))
p=ROOT/'Deliverables/v4/validation.json';r=json.loads(p.read_text());r.update({'two_opposing_counters_per_station':True,'open_leg_space_checked':True,'source_v3_unchanged':True,'preserved_non_station_objects':pres['preserved_non_station_objects']});p.write_text(json.dumps(r,indent=2))
