"""Attach the floor AO atlas using the glTF exporter's occlusion socket."""
import bpy, sys
from pathlib import Path
source,dest=map(Path,sys.argv[sys.argv.index('--')+1:])
if dest.exists(): raise RuntimeError('Refusing to overwrite checkpoint')
bpy.ops.wm.open_mainfile(filepath=str(source))
floor=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'].objects['ENV_floor_slab']
group=bpy.data.node_groups.get('glTF Material Output')
if group is None:
 group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
 group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
for mat in floor.data.materials:
 nodes=mat.node_tree.nodes
 ao=next(n for n in nodes if n.type=='TEX_IMAGE' and n.image and n.image.name=='MiningFloorAO')
 uv=nodes.new('ShaderNodeUVMap'); uv.uv_map='FloorLighting'
 mat.node_tree.links.new(uv.outputs['UV'],ao.inputs['Vector'])
 output=nodes.new('ShaderNodeGroup'); output.node_tree=group
 mat.node_tree.links.new(ao.outputs['Color'],output.inputs['Occlusion'])
# Detail UV stays primary; AO explicitly uses the second channel.
floor.data.uv_layers.active_index=0
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
print('AO_EXPORT_READY',flush=True)
