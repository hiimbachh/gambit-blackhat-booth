"""Join completed shots and verify encoded frame counts; run with regular Python."""
import sys,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from media_metadata import video_timing
out=root/'Deliverables/presentation';ffmpeg=Path(sys.argv[1])
manifest=json.loads((out/'render_manifest.json').read_text());paths=[];reports={}
for shot in manifest['shots']:
 name=shot['name'];assert (out/(name+'.done')).exists(),name+' unfinished'
 candidates=list(out.glob(name+'*.mp4'));assert len(candidates)==1,candidates
 path=candidates[0];timing=video_timing(path)
 assert timing['frames']==780 and timing['fps']==60 and timing['duration_seconds']==13,timing
 reports[name]=timing;paths.append(path)
listing=out/'concat.txt';listing.write_text(''.join("file '"+p.name+"'\n" for p in paths))
final=out/'Gambit_Booth_Overview_1080p60.mp4'
subprocess.run([str(ffmpeg),'-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(final)],check=True)
timing=video_timing(final);assert timing['frames']==3120 and timing['fps']==60 and timing['duration_seconds']==52,timing
subprocess.run([str(ffmpeg),'-v','error','-i',str(final),'-f','null','-'],check=True)
reports['final']=timing;reports['full_decode']='passed'
(out/'video_validation.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
