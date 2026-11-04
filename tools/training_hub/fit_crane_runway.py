"""Fit the bridge crane inside the hall's interior column rows, with real brackets."""
import bpy
from mathutils import Vector

def fit_crane(scene):
    scene.frame_set(1)
    for name in ['CRANE_bridge_girder','CRANE_bridge_girder.001']:
        obj=scene.objects[name]
        factor=17.6/obj.dimensions.x
        if obj.data.users>1:obj.data=obj.data.copy()
        for vertex in obj.data.vertices:vertex.co.x*=factor
        obj.data.update()
    for name in ['CRANE_runway','CRANE_runway.001','CRANE_end_truck','CRANE_end_truck.001']:
        obj=scene.objects[name]
        matrix=obj.matrix_world.copy();matrix.translation.x=8.8 if matrix.translation.x>0 else -8.8;obj.matrix_world=matrix
    for obj in scene.objects:
        if obj.name.startswith('CRANE_runway_bracket'):
            obj.hide_render=True;obj.hide_set(True)
    collection=bpy.data.collections.new('FIT_Crane_RunwaySupports');scene.collection.children.link(collection)
    material=bpy.data.materials['EXP_Graphite']
    def beam(name,a,b,width):
        a,b=Vector(a),Vector(b)
        bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)/2)
        obj=bpy.context.object;obj.name=name
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
        for vertex in obj.data.vertices:
            vertex.co.x*=width;vertex.co.y*=width;vertex.co.z*=(b-a).length
        obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();obj.data.materials.append(material)
    for sign in [-1,1]:
        for i,y in enumerate([-19.25,-13.75,-8.25,-2.75,2.75,8.25,13.75,19.25]):
            beam(f'FIT_CraneBracket_{sign}_{i}',(sign*9.5,y,7.55),(sign*8.8,y,7.55),.18)
            beam(f'FIT_CraneBrace_{sign}_{i}',(sign*9.5,y,6.8),(sign*8.8,y,7.5),.09)

if __name__=='__main__':
    import sys
    from pathlib import Path
    source,target=sys.argv[sys.argv.index('--')+1:];assert not Path(target).exists();assert source!=target
    bpy.ops.wm.open_mainfile(filepath=source)
    scene=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=scene
    fit_crane(scene);scene.camera=scene.objects['CAM_main'];scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
    print('CRANE_FITTED',target)
