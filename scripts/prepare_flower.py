"""Trace the supplied alpha silhouette; preserve its RGB artwork for the model."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'Ref Material/Flower/flower.png'; out=ROOT/'Assets/Brand';out.mkdir(parents=True,exist_ok=True)
im=Image.open(src).convert('RGBA')
preview=im.copy();preview.thumbnail((2048,2048),Image.Resampling.LANCZOS);preview.save(out/'flower_2048.png')
w=1280;h=round(w*im.height/im.width)
alpha=im.getchannel('A').resize((w,h),Image.Resampling.LANCZOS).filter(ImageFilter.MedianFilter(5))
a=np.array(alpha)>=128
pad=np.pad(a,1); edges={}
for dy,dx,offset1,offset2 in [(-1,0,(0,0),(1,0)),(0,1,(1,0),(1,1)),(1,0,(1,1),(0,1)),(0,-1,(0,1),(0,0))]:
 neighbor=pad[1+dy:1+dy+h,1+dx:1+dx+w]
 for y,x in zip(*np.where(a & ~neighbor)):
  p=(int(x)+offset1[0],int(y)+offset1[1]);q=(int(x)+offset2[0],int(y)+offset2[1]);edges[p]=q
loops=[]
while edges:
 start=next(iter(edges));p=start;loop=[]
 while p in edges:
  loop.append(p);p=edges.pop(p)
  if p==start:break
 loops.append(loop)
loop=max(loops,key=len)
def rdp(p,eps):
 if len(p)<3:return p
 q=np.array(p,float);v=q[-1]-q[0];norm=np.linalg.norm(v)
 d=np.linalg.norm(q-q[0],axis=1) if norm==0 else np.abs(v[0]*(q[:,1]-q[0,1])-v[1]*(q[:,0]-q[0,0]))/norm
 i=int(np.argmax(d))
 if d[i]<=eps:return [p[0],p[-1]]
 return rdp(p[:i+1],eps)[:-1]+rdp(p[i:],eps)
middle=len(loop)//2;poly=rdp(loop[:middle+1],1.2)[:-1]+rdp(loop[middle:]+[loop[0]],1.2)[:-1]
data={'source':'Ref Material/Flower/flower.png','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'contour_uv':[[x/w,1-y/h] for x,y in poly],'aspect':im.width/im.height,'trace_resolution':[w,h],'vertices':len(poly)}
(out/'flower_contour.json').write_text(json.dumps(data,indent=2));print('Flower contour:',len(poly),'vertices')
