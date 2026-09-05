import bpy
from pathlib import Path
p=Path.cwd()/'scripts/screen_manager.py'
t=bpy.data.texts.get('screen_manager.py')
if t:t.clear();t.write(p.read_text())
else:bpy.data.texts.load(str(p))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
