"""Apply licensed local texture maps using exportable Principled materials.

Run in the connected Blender or a saved checkpoint. Does not export or save.
"""
import bpy
from pathlib import Path

ROOT = Path('/Users/rpriest/Library/CloudStorage/OneDrive-VertoPtyLtd/Documents/ChatGPT/immivio-360-player')
TEXTURES = ROOT / 'build/training-hub/material-sources'
scene = bpy.data.scenes['VERTO_Higgsfield_Mining_Concept']
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
roles = {
    'M_concrete_floor': ('concrete_floor', 4.0, 0.35),
    'M_rock_decline': ('worn_rock_natural_01', 2.0, 0.75),
    'M_rock_rubble': ('worn_rock_natural_01', 2.0, 0.75),
}
materials = {}
for original, (asset, metres, strength) in roles.items():
    name = 'VERTO_PBR_' + original
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    for channel, socket in [('diff', 'Base Color'), ('rough', 'Roughness'), ('nor_gl', 'Normal')]:
        image = bpy.data.images.load(str(TEXTURES / f'{asset}_{channel}_2k.jpg'), check_existing=True)
        image.colorspace_settings.name = 'sRGB' if channel == 'diff' else 'Non-Color'
        image.pack()
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = image
        texture.extension = 'REPEAT'
        if channel == 'nor_gl':
            normal = nodes.new('ShaderNodeNormalMap')
            normal.inputs['Strength'].default_value = strength
            links.new(texture.outputs['Color'], normal.inputs['Color'])
            links.new(normal.outputs['Normal'], principled.inputs[socket])
        else:
            links.new(texture.outputs['Color'], principled.inputs[socket])
    material['source'] = f'https://polyhaven.com/a/{asset}'
    material['license'] = 'CC0'
    materials[original] = material

changed = []
for obj in scene.objects:
    if obj.type != 'MESH':
        continue
    assignments = {i: slot.material.name for i, slot in enumerate(obj.material_slots)
                   if slot.material and slot.material.name in roles}
    if not assignments:
        continue
    obj.data = obj.data.copy()
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='SurfaceUV')
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    for polygon in obj.data.polygons:
        original = assignments.get(polygon.material_index)
        if not original:
            continue
        metres = roles[original][1]
        normal = normal_matrix @ polygon.normal
        axis = max(range(3), key=lambda n: abs(normal[n]))
        axes = (1, 2) if axis == 0 else ((0, 2) if axis == 1 else (0, 1))
        for index in polygon.loop_indices:
            position = obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co
            uv.data[index].uv = (position[axes[0]] / metres, position[axes[1]] / metres)
    for index, original in assignments.items():
        obj.data.materials[index] = materials[original]
    changed.append(obj.name)

result = {'textured_objects': changed, 'materials': [m.name for m in materials.values()],
          'images': [{'name': i.name, 'size': list(i.size)} for i in bpy.data.images
                     if any(i.name.startswith(a) for a in ('concrete_floor', 'worn_rock_natural_01'))]}
print(result)
