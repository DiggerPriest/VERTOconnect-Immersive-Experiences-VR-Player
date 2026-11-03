"""Blender intake gate for a selected underground truck root (metres).
Run after import, before placing/rotating the asset in the workshop.
Never resize or delete the source automatically.
"""
import json

def assess_bounds(minimum, maximum):
    size=[maximum[i]-minimum[i] for i in range(3)]
    length,width=sorted(size[:2],reverse=True)
    height=size[2]
    errors=[]
    # Deliberately broad AD45-class intake envelope, not a certification test.
    if not 9.0 <= length <= 13.0: errors.append('length outside 9-13 m intake envelope')
    if not 2.5 <= width <= 3.8: errors.append('width outside 2.5-3.8 m intake envelope')
    if not 2.4 <= height <= 3.8: errors.append('height outside 2.4-3.8 m low-profile envelope')
    return {'length_m':length,'width_m':width,'height_m':height,'passed':not errors,'errors':errors,
            'limits':'Geometry bounds only; silhouette, mechanical accuracy and panel configuration require visual review.'}

def inspect_root(root):
    from mathutils import Vector
    # Remove placement rotation and translation, but retain world scale.
    _,rotation,_=root.matrix_world.decompose()
    basis=rotation.to_matrix().inverted()
    origin=root.matrix_world.translation
    objects=[root]+list(root.children_recursive)
    points=[basis @ ((o.matrix_world @ Vector(c))-origin)
            for o in objects if o.type=='MESH' for c in o.bound_box]
    if not points: raise ValueError('Truck root contains no meshes')
    return assess_bounds([min(p[i] for p in points) for i in range(3)],
                         [max(p[i] for p in points) for i in range(3)])

if __name__=='__main__':
    import bpy,sys
    name=sys.argv[sys.argv.index('--')+1]
    result=inspect_root(bpy.data.objects[name])
    print('UNDERGROUND_TRUCK_INTAKE '+json.dumps(result))
    if not result['passed']: raise RuntimeError('Truck dimensions failed intake gate')
