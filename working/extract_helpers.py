from pathlib import Path
p=Path('working/build_booth.py').read_text().split('# Carpet uses')[0]
p=p.replace("OUT=ROOT/'Deliverables'","OUT=ROOT/'Deliverables'/'v2'").replace('OUT.mkdir(exist_ok=True)','OUT.mkdir(parents=True,exist_ok=True)')
p=p.replace("s=bpy.data.scenes.new('GAMBIT | Final booth reconstruction')","s=bpy.data.scenes.new('GAMBIT | Photo reconstruction v2')")
Path('scripts/boothlib.py').write_text(p)
