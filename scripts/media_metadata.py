"""Read video sample timing from MOV/MP4 headers without decoding or modifying media."""
import struct
from pathlib import Path
def video_timing(path):
 with Path(path).open('rb') as f:
  def atoms(start,end):
   p=start
   while p+8<=end:
    f.seek(p);size,kind=struct.unpack('>I4s',f.read(8));header=8
    if size==1:size=struct.unpack('>Q',f.read(8))[0];header=16
    elif size==0:size=end-p
    if size<header or p+size>end:raise ValueError('Invalid MOV atom')
    yield kind,p+header,p+size
    p+=size
  def children(parent,kind):return [a for a in atoms(parent[1],parent[2]) if a[0]==kind]
  root=(b'root',0,Path(path).stat().st_size)
  for moov in children(root,b'moov'):
   for trak in children(moov,b'trak'):
    for mdia in children(trak,b'mdia'):
     handler=children(mdia,b'hdlr')[0];f.seek(handler[1]+8)
     if f.read(4)!=b'vide':continue
     mdhd=children(mdia,b'mdhd')[0];f.seek(mdhd[1]);version=f.read(1)[0]
     f.seek(mdhd[1]+(20 if version else 12));timescale=struct.unpack('>I',f.read(4))[0]
     stbl=children(children(mdia,b'minf')[0],b'stbl')[0];stts=children(stbl,b'stts')[0]
     f.seek(stts[1]+4);entries=struct.unpack('>I',f.read(4))[0];table=[struct.unpack('>II',f.read(8)) for _ in range(entries)]
     count=sum(n for n,d in table);ticks=sum(n*d for n,d in table)
     return {'frames':count,'fps':count*timescale/ticks,'duration_seconds':ticks/timescale,'constant_frame_rate':len({d for n,d in table})==1,'timescale':timescale,'sample_ticks':table}
 raise ValueError('No video track '+str(path))
if __name__=='__main__':
 import sys,json
 for arg in sys.argv[1:]:print(arg,json.dumps(video_timing(arg)))
