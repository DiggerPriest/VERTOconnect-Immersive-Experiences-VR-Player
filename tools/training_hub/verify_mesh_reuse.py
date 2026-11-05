"""Prove a GLB mesh-sharing optimisation preserves rendered and animated data."""
import argparse
import json, struct, hashlib
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('before',type=Path)
parser.add_argument('after',type=Path)
parser.add_argument('--report',type=Path)
args=parser.parse_args()
def read(name):
 data=Path(name).read_bytes(); n=struct.unpack_from('<I',data,12)[0]
 doc=json.loads(data[20:20+n]); off=20+n; size=struct.unpack_from('<I',data,off)[0]
 blob=data[off+8:off+8+size]
 def accessor(i):
  a=doc['accessors'][i]; assert 'sparse' not in a
  v=doc['bufferViews'][a['bufferView']]
  width={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
  start=v.get('byteOffset',0)+a.get('byteOffset',0); stride=v.get('byteStride',width)
  raw=b''.join(blob[start+j*stride:start+j*stride+width] for j in range(a['count']))
  return (a['componentType'],a['type'],a['count'],a.get('normalized',False),hashlib.sha256(raw).hexdigest())
 nodes={n['name']:n for n in doc['nodes']}
 geometry={}
 for name,n in nodes.items():
  if 'mesh' not in n:continue
  primitives=[]
  for p in doc['meshes'][n['mesh']]['primitives']:
   primitives.append({'attributes':{k:accessor(v) for k,v in p['attributes'].items()},'indices':accessor(p['indices']) if 'indices'in p else None,'material':doc['materials'][p['material']] if 'material'in p else None,'mode':p.get('mode',4)})
  geometry[name]=primitives
 transforms={name:{k:v for k,v in n.items() if k not in ('mesh','children','camera','extensions')} for name,n in nodes.items()}
 hierarchy={name:[doc['nodes'][i]['name'] for i in n.get('children',[])] for name,n in nodes.items()}
 animations={}
 for a in doc.get('animations',[]):
  tracks=[]
  for c in a['channels']:
   s=a['samplers'][c['sampler']]
   tracks.append((doc['nodes'][c['target']['node']]['name'],c['target']['path'],s.get('interpolation','LINEAR'),accessor(s['input']),accessor(s['output'])))
  animations[a['name']]=sorted(tracks)
 return doc,geometry,transforms,hierarchy,animations
before=read(args.before);after=read(args.after)
for i,label in enumerate(['geometry/materials','transforms','hierarchy','animation samples'],1):
 assert before[i]==after[i],label+' changed: '+str([k for k in before[i] if before[i][k]!=after[i].get(k)][:12])
report={'result':'PASS','mesh_nodes':len(after[1]),'animation_clips':len(after[4]),'meshes_before':len(before[0]['meshes']),'meshes_after':len(after[0]['meshes']),'checks':['all primitive attributes and indices byte identical','materials identical','node transforms and hierarchy identical','all animation inputs outputs targets interpolation identical']}
if args.report: args.report.write_text(json.dumps(report,indent=2))
print(json.dumps(report))
