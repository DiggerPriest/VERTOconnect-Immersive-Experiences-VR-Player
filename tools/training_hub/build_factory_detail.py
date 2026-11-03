"""Reuse reviewed tunnel and authored service props in the factory layout.
Run after layout/fans. Source construction executes in a separate temporary scene.
"""
import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
factory=bpy.data.scenes['VERTO_MiningFactory']
temp=bpy.data.scenes.new('Factory_detail_staging');bpy.context.window.scene=temp
source=(root/'tools/training_hub/build_mining_prototype.py').read_text().split('# Collapse static geometry')[0]
source=source.replace("concrete=mat('Workshop concrete'", "for obj in bpy.context.scene.objects:obj['factory_tunnel_part']=True\nconcrete=mat('Workshop concrete'")
oldargv=sys.argv;sys.argv=['blender','--','--output',str(root/'build/training-hub/mining-prototype')]
namespace={};exec(compile(source,'build_mining_prototype.py','exec'),namespace);sys.argv=oldargv
collection=bpy.data.collections.new('PRP_mining_detail');factory.collection.children.link(collection)
# Explicit asset groups, never geometry-coordinate selection.
exclude=('Factory','Side wall','Front wall','Building column','Fixed roof beam','Ceiling','Rear wall','Fan','Fresh','FRESH','Central')
keep=[]
for obj in list(temp.objects):
 if obj.name.startswith(exclude):continue
 collection.objects.link(obj);keep.append(obj)
 for parent in list(obj.users_collection):
  if parent!=collection:parent.objects.unlink(obj)
# Source tunnel's original entrance is y15; align with factory portal at y22.
for obj in keep:
 if obj.get('factory_tunnel_part',False):obj.location.y+=7
bpy.context.window.scene=factory
for name in ['PROXY_haul_truck','PROXY_mechanical_workshop','PROXY_rear_service_stores','ENV_tunnel_floor','ENV_tunnel_side_-5','ENV_tunnel_side_5','ENV_tunnel_roof']:
 obj=factory.objects.get(name)
 if obj:obj.hide_render=True;obj.hide_set(True)
bpy.context.window.scene=factory
bpy.data.scenes.remove(temp)
factory.render.filepath='/tmp/verto-factory-detail.png';bpy.ops.render.render(write_still=True)
print('FACTORY_DETAIL',len(keep))
