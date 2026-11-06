"""Prepare a reversible material/floor polish candidate from an editable scene.
Run with Blender --background --python this.py -- input.blend output.blend.
The original file and live Blender session are never modified.
"""
import bpy,json,sys
from pathlib import Path
source,target=map(Path,sys.argv[sys.argv.index('--')+1:])
assert source.is_file() and not target.exists()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=scene
changes=[]
# These are coated steel surfaces. Paint/enamel is dielectric even when the
# substrate is steel. Bare galvanised steel, tools and shafts retain metalness.
coated={'M_steel_charcoal','CV_CharcoalSteel','DENS_Graphite','EXP_MotorPaint',
 'EXP_SafetyYellow','CV_SafetyYellow','M_safety_yellow','DENS_EnamelIvory',
 'DENS_EnamelTeal','DENS_SafetyYellow','DENS_AirMainBlue','DENS_InstrumentBlue',
 'DENS_VentIdentification','M_safety_stripe'}
for mat in bpy.data.materials:
    base=mat.name.removeprefix('AO_')
    if base not in coated or not mat.use_nodes:continue
    shader=mat.node_tree.nodes.get('Principled BSDF')
    if not shader:continue
    before=shader.inputs['Metallic'].default_value
    shader.inputs['Metallic'].default_value=0.0
    shader.inputs['Roughness'].default_value=max(.48,shader.inputs['Roughness'].default_value)
    changes.append({'material':mat.name,'old_metallic':before,'new_metallic':0.0})
mat=bpy.data.materials['M_skylight'];shader=mat.node_tree.nodes['Principled BSDF']
shader.inputs['Base Color'].default_value=(.64,.69,.72,1)
shader.inputs['Roughness'].default_value=.6
shader.inputs['Emission Strength'].default_value=.12
# Keep the floor safety markings; hide only the obsolete metal seat marker.
for name in ['PRP_seat_inlay_hub','PRP_seat_inlay_ring']:
    obj=bpy.data.objects.get(name)
    if obj:obj.hide_render=True;obj.hide_set(True);obj['premium_hidden_reason']='Obsolete viewer marker; keep immediate floor clear'
# The old merged bollard mesh also contains an orphan plate at the viewer
# origin. Remove only its disconnected central component, retaining all real bases.
import bmesh
obj=bpy.data.objects['PRP_bollard_baseplates']
bm=bmesh.new();bm.from_mesh(obj.data)
central=[v for v in bm.verts if abs((obj.matrix_world@v.co).x)<.4 and abs((obj.matrix_world@v.co).y)<.4]
assert central, 'Expected the audited orphan plate at the viewer origin'
assert all(all(e.other_vert(v) in central for e in v.link_edges) for v in central), 'Central plate is not isolated'
removed=len(central);bmesh.ops.delete(bm,geom=central,context='VERTS');bm.to_mesh(obj.data);bm.free()
changes.append({'object':obj.name,'orphan_plate_vertices_removed':removed})
# Portable packed textures; relative paths also make later unpacking predictable.
for image in bpy.data.images:
    if image.source=='FILE' and image.packed_file:
        image.filepath='//textures/'+(Path(image.filepath).name or image.name+'.png')
scene['premium_material_pass']='dielectric coatings, softened skylights, cleared viewer marker'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'source':str(source),'output':str(target),'material_changes':changes,'packed_file_images':sum(bool(i.packed_file) for i in bpy.data.images if i.source=='FILE')}
target.with_suffix('.polish.json').write_text(json.dumps(report,indent=2))
print('PREMIUM_MATERIAL_PASS',json.dumps(report))
