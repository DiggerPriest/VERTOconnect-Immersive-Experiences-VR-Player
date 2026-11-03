"""Bake a separate floor AO atlas without changing the source scene or UVs."""
import bpy, sys, json
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
source, dest=map(Path,args[:2])
lighting="--lighting" in args
if dest.exists(): raise RuntimeError('Output directory already exists')
dest.mkdir(parents=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept']
bpy.context.window.scene=s
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
floor=s.objects['ENV_floor_slab']
floor.data=floor.data.copy()
uv=floor.data.uv_layers.new(name='FloorLighting')
floor.data.uv_layers.active=uv
# Give the visible top its own atlas region; the underside and edges must
# never overwrite the top's lighting during baking.
other=[p for p in floor.data.polygons if p.normal.z < 0.9]
for poly in floor.data.polygons:
 for corner,i in enumerate(poly.loop_indices):
  p=floor.matrix_world@floor.data.vertices[floor.data.loops[i].vertex_index].co
  if poly.normal.z >= 0.9:
   uv.data[i].uv=(0.02+0.96*(p.x+20)/40,0.12+0.86*(p.y+22)/44)
  else:
   index=other.index(poly); width=0.96/max(1,len(other))
   corners=[(0,0),(1,0),(1,1),(0,1)]
   a,b=corners[corner%4]
   uv.data[i].uv=(0.02+width*(index+0.1+0.8*a),0.02+0.06*b)
# Keep existing detail maps explicitly tied to their original UV layer.
for slot in floor.material_slots:
 slot.material=slot.material.copy()
 mat=slot.material
 old_uv=mat.node_tree.nodes.new('ShaderNodeUVMap'); old_uv.uv_map=floor.data.uv_layers[0].name
 for n in list(mat.node_tree.nodes):
  if n.type=='TEX_IMAGE': mat.node_tree.links.new(old_uv.outputs['UV'],n.inputs['Vector'])
image=bpy.data.images.new('MiningFloorAO',width=2048,height=2048,alpha=False)
image.colorspace_settings.name='Non-Color'
for mat in floor.data.materials:
 n=mat.node_tree.nodes.new('ShaderNodeTexImage'); n.image=image; mat.node_tree.nodes.active=n
bpy.ops.object.select_all(action='DESELECT'); floor.select_set(True); bpy.context.view_layer.objects.active=floor
s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.device='CPU'
s.render.bake.margin=8
print('BAKE_STARTED',flush=True)
if lighting:
 s.cycles.max_bounces=3
 s.cycles.diffuse_bounces=2
 s.render.bake.use_pass_direct=True
 s.render.bake.use_pass_indirect=True
 s.render.bake.use_pass_color=False
 # Lighting-only atlas: keep the tiled surface colour independent.
 bpy.ops.object.bake(type='DIFFUSE')
else:
 bpy.ops.object.bake(type='AO')
image.filepath_raw=str(dest/'floor_ao.png'); image.file_format='PNG'; image.save(); image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'floor_ao_preview.blend'))
(dest/'status.json').write_text(json.dumps({'status':'complete','source':str(source),'resolution':2048,'samples':32,'kind':'diffuse-lighting' if lighting else 'ambient-occlusion'}))
print('BAKE_COMPLETE',flush=True)
