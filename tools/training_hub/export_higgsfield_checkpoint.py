"""Export a saved checkpoint in a separate factory-startup Blender process.

Never changes the live plugin scene or overwrites the source .blend.
Usage: blender --background --factory-startup --python this.py -- input.blend output.glb
"""
import bpy
import argparse
import json
import struct
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('destination', type=Path)
parser.add_argument('--batch-static', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, destination = args.source, args.destination
if destination.exists():
    raise FileExistsError(destination)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.data.scenes['VERTO_Higgsfield_Mining_Concept']
bpy.context.window.scene = scene
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
        groups.setdefault(tuple(m.name if m else '' for m in obj.data.materials), []).append(obj)
    for index, objects in enumerate(groups.values()):
        if len(objects) < 2:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()
        objects[0].name = f'STATIC_MaterialBatch_{index:03d}'
    static_after = sum(1 for obj in scene.objects if static_leaf(obj))
destination.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=str(destination), export_format='GLB',
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
channels = [channel for animation in document.get('animations', []) for channel in animation['channels']]
names = document.get('nodes', [])
moving = {names[c['target']['node']].get('name', '') for c in channels}
for node in names:
    if node.get('name') in {'WKS_Generated_Maintenance_Bay_Review', 'CV_CUTTER_service_opening'}:
        raise RuntimeError('Non-rendering review/cutter object leaked into export')
rocks = sorted(n for n in moving if n.startswith('CV_ORE_'))
rollers = sorted(n for n in moving if 'idler' in n.lower() or 'drum' in n.lower())
report = {'source': str(source), 'destination': str(destination),
          'static_before': static_before, 'static_after': static_after,
          'source_active_actions': len(animated), 'exported_clips': len(document.get('animations', [])),
          'animated_nodes': len(moving), 'rock_nodes': rocks, 'roller_nodes': rollers}
destination.with_suffix('.audit.json').write_text(json.dumps(report, indent=2))
print('CHECKPOINT_EXPORT', json.dumps(report))
if not rocks or not rollers:
    raise RuntimeError('Export omitted required conveyor rock or roller channels')
