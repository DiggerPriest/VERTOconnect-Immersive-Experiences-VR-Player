"""Export an isolated GLB preview; does not replace app scenery."""
import bpy,json
from pathlib import Path
s=bpy.data.scenes['VERTO_MiningFactory'];bpy.context.window.scene=s
out=Path(__file__).resolve().parents[2]/'build/training-hub/factory-preview';out.mkdir(parents=True,exist_ok=True)
# Workbench object colours are not glTF materials. Assign explicit PBR roles.
mats={}
for o in s.objects:
 if o.type!='MESH':continue
 if len(o.data.materials)>0:continue # Preserve authored PBR textures and material roles.
 key=tuple(round(v,3) for v in o.color)
 if key not in mats:
  m=bpy.data.materials.new('Factory_'+str(len(mats)));m.use_nodes=True
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=key;p.inputs['Roughness'].default_value=.65
  m.diffuse_color=key;mats[key]=m
 o.data.materials.clear();o.data.materials.append(mats[key])
# This runs in a disposable build process: retain authored source scripts, join
# only static meshes with identical material bindings. Rotating children remain separate.
groups={}
for o in list(s.objects):
 if o.type=='MESH' and not o.hide_render and not o.parent and not o.animation_data:
  groups.setdefault(tuple(m.name if m else '' for m in o.data.materials),[]).append(o)
for index,objects in enumerate(groups.values()):
 if len(objects)<2:continue
 for o in bpy.context.view_layer.objects:o.select_set(False)
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.join()
 objects[0].name='STATIC_material_batch_'+str(index)
for obj in bpy.data.objects:
 obj.select_set(False)
# Export only the intended scene, including across Blender scene contexts.
for o in s.objects:
 if o.type in {'MESH','EMPTY'} and not o.hide_render:o.select_set(True)
s.frame_set(1)
bpy.ops.export_scene.gltf(filepath=str(out/'factory.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_frame_range=True,export_force_sampling=True,export_apply=True)
(out/'project.godot').write_text('[application]\nconfig/name="Factory export verification"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
print('FACTORY_GLB',out/'factory.glb')
