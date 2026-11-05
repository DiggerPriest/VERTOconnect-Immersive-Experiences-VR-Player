"""Export a saved checkpoint in a separate factory-startup Blender process.

Never changes the live plugin scene or overwrites the source .blend.
Usage: blender --background --factory-startup --python this.py -- input.blend output.glb
"""
import bpy
import argparse
import json
import struct
import sys
import math
from mathutils import Vector
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('destination', type=Path)
parser.add_argument('--batch-static', action='store_true')
parser.add_argument('--pack-solid-colors', action='store_true')
parser.add_argument('--deduplicate-animated-meshes', action='store_true')
parser.add_argument('--static-cell-size', type=float, default=0.0, help='Optional XY batching cell size in metres; 0 retains material-only batching')
parser.add_argument('--static-cell-min-triangles', type=int, default=0, help='Only spatially partition material groups at or above this triangle count')
parser.add_argument('--stable-static-batches', action='store_true', help='Preserve authored corner normals and join into world-identity mesh objects')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, destination = args.source, args.destination
if not math.isfinite(args.static_cell_size) or args.static_cell_size < 0: parser.error("static cell size must be finite and nonnegative")
if args.static_cell_min_triangles < 0: parser.error("triangle threshold cannot be negative")
if destination.exists():
    raise FileExistsError(destination)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.data.scenes['VERTO_Higgsfield_Mining_Concept']
bpy.context.window.scene = scene
# Keep equipment labels editable as FONT in the authored checkpoint; convert
# only this disposable export process so they survive into the game scene.
for obj in list(scene.objects):
    if obj.type != 'FONT' or obj.hide_render:
        continue
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph), depsgraph=depsgraph)
    label = bpy.data.objects.new(obj.name + '_Export', mesh)
    for collection in obj.users_collection:
        collection.objects.link(label)
    label.matrix_world = obj.matrix_world.copy()
    old_name = obj.name
    bpy.data.objects.remove(obj, do_unlink=True)
    label.name = old_name
# glTF carries the AO multiplier in COLOR_0. Restore the authored plain
# colour factor in this disposable export graph, so unsupported MixRGB graph
# extraction cannot replace painted equipment with a white material.
for material in bpy.data.materials:
    if not material.name.startswith('AO_') or not material.use_nodes:
        continue
    principled = material.node_tree.nodes.get('Principled BSDF')
    if not principled or not principled.inputs['Base Color'].is_linked:
        continue
    link = principled.inputs['Base Color'].links[0]
    mix = link.from_node
    if mix.type == 'MIX_RGB' and mix.blend_type == 'MULTIPLY':
        base_color = tuple(mix.inputs[1].default_value)
        material.node_tree.links.remove(link)
        principled.inputs['Base Color'].default_value = base_color
# Optional export-only consolidation. Only plain, opaque, untextured PBR
# graphs qualify; exact shader inputs other than base tint remain distinct.
packed_materials = 0
if args.pack_solid_colors:
    import math
    candidates = {}
    shared = {}
    for mat in list(bpy.data.materials):
        if not mat.use_nodes: continue
        p = mat.node_tree.nodes.get('Principled BSDF')
        if not p or any(n.type == 'TEX_IMAGE' for n in mat.node_tree.nodes): continue
        if any(socket.is_linked for socket in p.inputs): continue
        if p.inputs['Alpha'].default_value != 1.0: continue
        if p.inputs['Emission Strength'].default_value != 0.0: continue
        color = tuple(p.inputs['Base Color'].default_value)
        if color[3] != 1.0: continue
        values = []
        for socket in p.inputs:
            if socket.name == 'Base Color' or not hasattr(socket, 'default_value'): continue
            value = socket.default_value
            try: value = tuple(value)
            except TypeError: pass
            values.append((socket.name, str(value)))
        key = (tuple(values), mat.use_backface_culling)
        if key not in shared:
            merged = mat.copy(); merged.name = 'PACKED_PBR_%03d' % len(shared)
            merged.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (1,1,1,1)
            shared[key] = merged
        candidates[mat.name] = (color, shared[key])
    visited = set()
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.hide_render or obj.data.as_pointer() in visited: continue
        visited.add(obj.data.as_pointer())
        mesh = obj.data
        slots = [candidates.get(m.name) if m else None for m in mesh.materials]
        if not any(slots): continue
        attr = mesh.color_attributes.active_color
        if attr is None:
            attr = mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
            for datum in attr.data: datum.color = (1,1,1,1)
        if attr.domain != 'CORNER': continue
        color_index = list(mesh.color_attributes).index(attr)
        mesh.color_attributes.active_color_index = color_index
        mesh.color_attributes.render_color_index = color_index
        for polygon in mesh.polygons:
            entry = slots[polygon.material_index] if polygon.material_index < len(slots) else None
            if not entry: continue
            color, merged = entry
            for loop_index in polygon.loop_indices:
                old = attr.data[loop_index].color
                attr.data[loop_index].color = (old[0]*color[0],old[1]*color[1],old[2]*color[2],old[3])
        for index,entry in enumerate(slots):
            if entry: mesh.materials[index] = entry[1]
    # Joining meshes merges colour layers by NAME. Normalize the sole exported
    # layer so AO-colored originals and newly tinted parts keep their colours.
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.hide_render: continue
        attr = obj.data.color_attributes.active_color
        if attr is not None:
            attr.name = 'ExportColor'
            index = list(obj.data.color_attributes).index(attr)
            obj.data.color_attributes.active_color_index = index
            obj.data.color_attributes.render_color_index = index
    packed_materials = len(candidates)

# Reuse only EXACT geometry/normal/UV/colour/material matches. Object-local
# animation transforms remain distinct, and the editable Blender source is not
# touched. This enables runtime MultiMesh groups for repeated conveyor parts.
shared_animated_meshes = 0
if args.deduplicate_animated_meshes:
    import hashlib
    pool = {}
    for obj in scene.objects:
        if obj.type != 'MESH' or not obj.animation_data or obj.modifiers or obj.data.shape_keys:
            continue
        if not obj.name.startswith(('CV_CarryIdler_', 'CV_ReturnIdler_', 'CV_BeltSeam_', 'CV2_COAL_')):
            continue
        mesh = obj.data
        payload = {
            'positions': [tuple(v.co) for v in mesh.vertices],
            'polygons': [(tuple(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
            'normals': [tuple(n.vector) for n in mesh.corner_normals],
            'materials': [(slot.material.name if slot.material else '', slot.link) for slot in obj.material_slots],
            'uv': [(layer.name, [tuple(d.uv) for d in layer.data]) for layer in mesh.uv_layers],
            'colors': [(a.name, a.domain, a.data_type, [tuple(d.color) for d in a.data]) for a in mesh.color_attributes],
            'active_color': mesh.color_attributes.active_color_index,
            'render_color': mesh.color_attributes.render_color_index,
        }
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if fingerprint in pool:
            if obj.data != pool[fingerprint]:
                obj.data = pool[fingerprint]
                shared_animated_meshes += 1
        else:
            pool[fingerprint] = mesh

animated = [o for o in scene.objects if o.animation_data and o.animation_data.action]
if not animated:
    raise RuntimeError('Checkpoint contains no active object actions')
static_before = static_after = 0
if args.batch_static:
    # Work only on leaf meshes with no animated/constraint-driven ancestor.
    # Evaluating modifiers before joining preserves portal booleans and bevels.
    def static_leaf(obj):
        if obj.type != 'MESH' or obj.children or obj.hide_render:
            return False
        current = obj
        while current:
            if current.animation_data or current.constraints:
                return False
            current = current.parent
        return True
    candidates = [obj for obj in scene.objects if static_leaf(obj)]
    static_before = len(candidates)
    groups = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in candidates:
        if obj.modifiers:
            evaluated = obj.evaluated_get(depsgraph)
            obj.data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            obj.modifiers.clear()
    if args.stable_static_batches:
        for obj in candidates:
            # Explicit authored normals survive changing batch membership and
            # non-uniform source transforms; recalculation can change shading.
            obj.data.normals_split_custom_set([tuple(n.vector) for n in obj.data.corner_normals])
    material_triangles = {}
    for obj in candidates:
        key = tuple(m.name if m else '' for m in obj.data.materials)
        material_triangles[key] = material_triangles.get(key, 0) + sum(max(0,len(p.vertices)-2) for p in obj.data.polygons)
    for obj in candidates:
        materials_key = tuple(m.name if m else '' for m in obj.data.materials)
        cell = None
        if args.static_cell_size > 0 and material_triangles[materials_key] >= args.static_cell_min_triangles:
            corners = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
            low = [min(v[i] for v in corners) for i in range(2)]
            high = [max(v[i] for v in corners) for i in range(2)]
            # Keep authored building-spanning pieces separate: their bounds
            # must not inflate every small fitting sharing their material.
            if any(high[i] - low[i] > args.static_cell_size for i in range(2)):
                cell = ('spanning', obj.name)
            else:
                cell = tuple(math.floor((low[i]+high[i])*.5/args.static_cell_size) for i in range(2))
        groups.setdefault((materials_key, cell), []).append(obj)
    for index, objects in enumerate(groups.values()):
        # Singletons need the same coordinate/normal conversion as larger
        # batches, otherwise cell membership changes their exported shading.
        if len(objects) < 2 and not args.stable_static_batches:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.hide_set(False)
            obj.select_set(True)
        if args.stable_static_batches:
            anchor = bpy.data.objects.new(f'STATIC_MaterialBatch_{index:03d}', bpy.data.meshes.new(f'STATIC_BatchMesh_{index:03d}'))
            scene.collection.objects.link(anchor)
            anchor.select_set(True)
            bpy.context.view_layer.objects.active = anchor
        else:
            anchor = objects[0]
            # The join mutates its active mesh datablock. Static and animated
            # coal can share that datablock: isolate it before appending parts.
            if anchor.data.users > 1:
                anchor.data = anchor.data.copy()
            bpy.context.view_layer.objects.active = anchor
        bpy.ops.object.join()
        anchor.name = f'STATIC_MaterialBatch_{index:03d}'
        if args.stable_static_batches and 'ExportColor' in anchor.data.color_attributes:
            # Joining into an empty anchor retains the data but not its active
            # render selection. Explicitly keep baked AO and packed PBR colours.
            color_index = list(anchor.data.color_attributes).index(anchor.data.color_attributes['ExportColor'])
            anchor.data.color_attributes.active_color_index = color_index
            anchor.data.color_attributes.render_color_index = color_index
    static_after = sum(1 for obj in scene.objects if static_leaf(obj))
# New procedural machines retain editable panels in the .blend. Collapse rigid
# siblings per material under the SAME animated parent for the game export.
# Never join moving children, constraint owners, or unrelated parent spaces.
rigid_batches = 0
if args.batch_static:
    groups = {}
    for obj in scene.objects:
        if (obj.type != 'MESH' or obj.children or obj.hide_render or obj.animation_data
                or obj.constraints or not obj.parent
                or not obj.name.startswith(('EXP_', 'FIT_'))):
            continue
        parent = obj.parent
        if not parent.animation_data:
            continue
        key = (parent.name, tuple(m.name if m else '' for m in obj.data.materials))
        groups.setdefault(key, []).append(obj)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for key, objects in groups.items():
        if len(objects) < 2:
            continue
        objects.sort(key=lambda obj: obj.name)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            if obj.modifiers:
                obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph),
                    preserve_all_data_layers=True, depsgraph=depsgraph)
                obj.modifiers.clear()
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        objects[0].name = 'RIGID_' + key[0] + '_' + str(rigid_batches)
        rigid_batches += 1

destination.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(destination), export_format='GLB',
    export_vertex_color='ACTIVE',
    use_active_scene=True, use_selection=False,
    # Rejected review assets and boolean cutters must never ship.
    use_renderable=True,
    export_animations=True, export_animation_mode='ACTIONS',
    export_force_sampling=True, export_frame_range=False,
    export_anim_slide_to_zero=True,
    export_optimize_animation_keep_anim_object=True,
    export_cameras=True, export_lights=True,
    # Current Godot project uses unitless, non-physical lighting. SPEC applies
    # a 683x watts-to-lumens factor and overwhelms this renderer setup.
    export_import_convert_lighting_mode='COMPAT',
)
data = destination.read_bytes()
length = struct.unpack_from('<I', data, 12)[0]
document = json.loads(data[20:20 + length])
# Baked AO and packed solid colours are part of the visible material, not
# optional export metadata. Fail before recording a successful audit if lost.
for mesh in document.get('meshes', []):
    for primitive in mesh.get('primitives', []):
        material_index = primitive.get('material')
        if material_index is None:
            continue
        material_name = document['materials'][material_index].get('name', '')
        if material_name.startswith(('AO_', 'PACKED_PBR')) and ('COLOR_0' not in primitive.get('attributes', {}) or 'COLOR_1' in primitive.get('attributes', {})):
            raise RuntimeError(f'Baked vertex colour channel missing or ambiguous in {mesh.get("name", "mesh")}: {material_name}')
channels = [channel for animation in document.get('animations', []) for channel in animation['channels']]
names = document.get('nodes', [])
moving = {names[c['target']['node']].get('name', '') for c in channels}
for node in names:
    if node.get('name') in {'WKS_Generated_Maintenance_Bay_Review', 'CV_CUTTER_service_opening'}:
        raise RuntimeError('Non-rendering review/cutter object leaked into export')
rocks = sorted(n for n in moving if n.startswith('CV_ORE_'))
rollers = sorted(n for n in moving if 'idler' in n.lower() or 'drum' in n.lower())
report = {'source': str(source), 'destination': str(destination),
          'stable_static_batches': args.stable_static_batches, 'static_cell_size_m': args.static_cell_size, 'static_cell_min_triangles': args.static_cell_min_triangles, 'static_before': static_before, 'static_after': static_after, 'rigid_batches': rigid_batches,
          'packed_candidate_materials': packed_materials, 'shared_animated_meshes': shared_animated_meshes, 'source_active_actions': len(animated), 'exported_clips': len(document.get('animations', [])),
          'animated_nodes': len(moving), 'rock_nodes': rocks, 'roller_nodes': rollers}
destination.with_suffix('.audit.json').write_text(json.dumps(report, indent=2))
print('CHECKPOINT_EXPORT', json.dumps(report))
if not rocks or not rollers:
    raise RuntimeError('Export omitted required conveyor rock or roller channels')
