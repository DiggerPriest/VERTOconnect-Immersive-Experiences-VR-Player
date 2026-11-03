"""Render an isolated generated GLB without touching the live Blender scene."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
source,destination=map(Path,sys.argv[sys.argv.index('--')+1:])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
centre=(lo+hi)/2; span=max(hi-lo)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
world=bpy.data.worlds.new('Review world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.15,1);s.world=world
bpy.ops.object.camera_add(location=centre+Vector((1.7,-2.3,1.4))*span)
c=bpy.context.object;c.rotation_euler=(centre-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=span*1.6;s.camera=c
for offset,power in [((1,-2,3),650),((-2,-1,1),350),((0,2,3),500)]:
 bpy.ops.object.light_add(type='AREA',location=centre+Vector(offset)*span)
 light=bpy.context.object;light.data.energy=power*span*span;light.data.shape='DISK';light.data.size=span*2;light.rotation_euler=(centre-light.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(destination.resolve());bpy.ops.render.render(write_still=True)
