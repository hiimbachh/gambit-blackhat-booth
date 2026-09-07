"""Read-only fingerprints for preservation across the v4.1 roof revision."""
import bpy, hashlib, json
def value(v):
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 try:return [value(x) for x in v]
 except TypeError:return str(v)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def material(m):
 if not m:return None
 d={'name':m.name,'diffuse':list(m.diffuse_color),'nodes':[],'links':[]}
 if m.node_tree:
  for n in m.node_tree.nodes:
   row={'name':n.name,'type':n.bl_idname,'inputs':[(i.identifier,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]}
   if n.type=='TEX_IMAGE':
    row.update(image=n.image.name if n.image else None,path=n.image.filepath if n.image else None,source=n.image.source if n.image else None,playback={k:getattr(n.image_user,k) for k in ['frame_start','frame_offset','frame_duration','use_cyclic','use_auto_refresh']})
   d['nodes'].append(row)
  d['links']=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]
 return json.loads(json.dumps(d))
def object_state(o):
 d={'world':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hidden':o.hide_get(),'materials':[material(m) for m in o.data.materials] if hasattr(o.data,'materials') else []}
 if o.type=='MESH':d['geometry']=digest(([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[p.material_index for p in o.data.polygons],[[list(v.uv) for v in uv.data] for uv in o.data.uv_layers]))
 if o.type in ['CURVE','FONT']:d['geometry']=digest([([list(p.co) for p in sp.points],[list(p.co) for p in sp.bezier_points]) for sp in o.data.splines])
 return json.loads(json.dumps(d))
