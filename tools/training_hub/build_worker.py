"""Create a clothed MPFB worker and baked 20-second inspection animation.

Blender 4.5.3, MPFB 2.0.18 in the user_default extension repository.
blender --background --offline-mode --python-exit-code 1 --python build_worker.py -- --mpfb PATH/src --output DIR
The output is a free-standing, human-scale worker facing Blender -Y.
"""
import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

parser = argparse.ArgumentParser()
parser.add_argument('--mpfb', required=True, help='Pinned MPFB src directory; must match the installed extension byte-for-byte')
parser.add_argument('--output', required=True)
parser.add_argument('--trade', choices=['electrical','plumbing','carpentry','mechanical'], default='electrical')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
import addon_utils
addon_utils.enable('bl_ext.user_default.mpfb', default_set=True, persistent=False)
import bl_ext.user_default.mpfb as mpfb_extension
from bl_ext.user_default.mpfb import VERSION as MPFB_VERSION
assert MPFB_VERSION == (2,0,18), 'Pin MPFB 2.0.18 for reproducible geometry'
assert bpy.app.version == (4,5,3), 'Pin Blender 4.5.3 for reproducible export'
def source_digest(root):
    assert root.is_dir(), f'MPFB source directory not found: {root}'
    digest=hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name=='.DS_Store':continue
        digest.update(path.relative_to(root).as_posix().encode()+b'\0')
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()
mpfb_source_digest=source_digest(Path(args.mpfb).resolve()/'mpfb')
assert mpfb_source_digest==source_digest(Path(mpfb_extension.__file__).resolve().parent), 'Installed MPFB differs from the supplied pinned source'

from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.targetservice import TargetService

out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
durations={'electrical':20,'plumbing':24,'carpentry':18,'mechanical':26}
duration=durations[args.trade]
scene.frame_end = duration*30+1
asset_name=args.trade+'_worker'
clip_names={'electrical':'Electrical_inspection_20s','plumbing':'Plumbing_adjust_fitting_24s','carpentry':'Carpentry_measure_mark_18s','mechanical':'Mechanical_tablet_inspection_26s'}
macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, muscle=.52, weight=.54, age=.43)
body = HumanService.create_human(macro_detail_dict=macro)
body.name = 'Worker_body'
rig = HumanService.add_builtin_rig(body, 'game_engine')
rig.name = asset_name
# Obtain eye centres before the MakeHuman construction helpers are removed.
def group_centre(name):
    group=body.vertex_groups.get(name)
    indices=[v.index for v in body.data.vertices if any(g.group==group.index for g in v.groups)]
    return sum((body.data.vertices[i].co for i in indices), Vector())/len(indices)
eye_centres=[group_centre('joint-l-eye'),group_centre('joint-r-eye')]
bpy.context.view_layer.objects.active = body
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
if body.data.shape_keys:
    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
for mod in list(body.modifiers):
    if mod.type == 'MASK':
        bpy.ops.object.modifier_apply(modifier=mod.name)


def material(name, rgb, roughness=.7, fabric=False):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=roughness
    if fabric:
        # Original deterministic micro-weave texture, exported as actual pixels.
        size=256
        yy,xx=np.mgrid[0:size,0:size]
        weave=.96+.025*np.sin(xx*math.pi/2)*np.sin(yy*math.pi/2)
        rng=np.random.default_rng(213)
        weave+=rng.normal(0,.009,(size,size))
        pixels=np.ones((size,size,4),dtype=np.float32)
        pixels[:,:,:3]=np.array(rgb)[None,None,:]*weave[:,:,None]
        img=bpy.data.images.new(name+'_weave',width=size,height=size)
        img.pixels.foreach_set(pixels.ravel())
        img.pack()
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
        m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    return m

skin=material('Skin',{'electrical':(.34,.19,.105),'plumbing':(.49,.29,.18),'carpentry':(.23,.115,.060),'mechanical':(.60,.38,.25)}[args.trade])
navy=material('Navy cotton drill',(.022,.045,.07),fabric=True)
hi_vis=material('Hi-vis cotton',{'electrical':(.94,.57,.018),'plumbing':(.79,.89,.025),'carpentry':(.93,.32,.035),'mechanical':(.93,.66,.025)}[args.trade],fabric=True)
reflective=material('Reflective safety tape',(.68,.73,.71),.4)
bootmat=material('Leather safety boots',(.04,.035,.028),.65)
black=material('Dark plastic',(.012,.018,.022),.4)
white=material('Eye white',(.72,.69,.62))
iris=material('Brown iris',(.075,.038,.014))
body.data.materials.clear();body.data.materials.append(skin)
for p in body.data.polygons:
    p.material_index=0;p.use_smooth=True

# Clothing is independent, expanded geometry with its own silhouette and rig
# weights, rather than colouring the exposed skin. Hidden body faces are removed.
rig_names={b.name for b in rig.data.bones}
def dominant(v):
    candidates=[(g.weight,body.vertex_groups[g.group].name) for g in v.groups if body.vertex_groups[g.group].name in rig_names]
    return max(candidates)[1] if candidates else 'pelvis'
def in_hands(v):
    n=dominant(v)
    return n.startswith(('hand','index','middle','pinky','ring','thumb'))

def jacket_face(p):
    vs=[body.data.vertices[i] for i in p.vertices]
    centre=sum((v.co for v in vs),Vector())/len(vs)
    return .86<centre.z<1.42 and not any(in_hands(v) for v in vs) and not (centre.z>1.32 and abs(centre.x)<.085 and abs(centre.y)<.10)

def trousers_face(p):
    centre=sum((body.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    return .15<centre.z<.91 and not any(in_hands(body.data.vertices[i]) for i in p.vertices)

def boots_face(p):
    return max(body.data.vertices[i].co.z for i in p.vertices)<.18

covered=set()
def clothing(name,predicate,mat,amount):
    chosen={p.index for p in body.data.polygons if predicate(p)}
    covered.update(chosen)
    o=body.copy();o.data=body.data.copy();scene.collection.objects.link(o);o.name=name
    bm=bmesh.new();bm.from_mesh(o.data);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[p for p in bm.faces if p.index not in chosen],context='FACES')
    if name=='Work_trousers':
        for vertex in bm.verts:
            if vertex.is_boundary and vertex.co.z<.3:vertex.co.z=.225
    bm.to_mesh(o.data);bm.free()
    o.data.materials.clear();o.data.materials.append(mat)
    o.data.materials.append(reflective)
    for v in o.data.vertices:
        # Radial expansion gives cotton trousers/jacket a looser manufactured fit.
        n=v.normal.copy()
        v.co += n*amount
    for p in o.data.polygons:
        p.material_index=0;p.use_smooth=True
        c=sum((o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
        if name=='Hi_vis_jacket' and ((.985<c.z<1.035) or (1.085<c.z<1.13)):
            p.material_index=1
    # A small inward thickness closes the cuffs, collar, waist, and ankle hems.
    mod=o.modifiers.new('Garment thickness','SOLIDIFY');mod.thickness=.003;mod.offset=-1
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return o
# Tailor regular rings rather than slicing the anatomical mesh into ragged edges.
covered.update(p.index for p in body.data.polygons if jacket_face(p))
verts=[];faces=[];weights=[];face_materials=[]
def add_rings(rings, segments=24, cap_start=False):
    start=len(verts)
    for centre,axis1,axis2,rx,ry,boneweights,mat in rings:
        for i in range(segments):
            angle=math.tau*i/segments
            verts.append(tuple(Vector(centre)+Vector(axis1)*rx*math.cos(angle)+Vector(axis2)*ry*math.sin(angle)))
            weights.append(boneweights)
    for j in range(len(rings)-1):
        for i in range(segments):
            faces.append((start+j*segments+i,start+j*segments+(i+1)%segments,start+(j+1)*segments+(i+1)%segments,start+(j+1)*segments+i))
            face_materials.append(rings[j][-1])
    if cap_start:
        centre_index=len(verts);verts.append(tuple(rings[0][0]));weights.append(rings[0][5])
        for i in range(segments):
            faces.append((centre_index,start+(i+1)%segments,start+i));face_materials.append(0)
# Circumferences include two precise horizontal tape bands and a fitted collar.
torso=[]
for z,rx,ry,mat in [(.86,.205,.151,0),(.97,.19,.142,0),(.985,.172,.13,1),(1.025,.175,.135,0),(1.08,.184,.14,0),(1.095,.187,.14,1),(1.135,.192,.145,0),(1.25,.205,.145,0),(1.34,.205,.145,0),(1.39,.10,.095,0),(1.41,.095,.09,0)]:
    torso.append(((0,.005,z),(1,0,0),(0,1,0),rx,ry,{'spine_03':1},mat))
add_rings(torso)
for side in ['l','r']:
    shoulder=rig.data.bones['upperarm_'+side].head_local
    elbow=rig.data.bones['lowerarm_'+side].head_local
    wrist=rig.data.bones['hand_'+side].head_local
    rings=[]
    for t in [0,.18,.55,.88,1,1.12,1.40,1.58,1.75,1.88,2.02]:
        if t<=1:
            c=shoulder.lerp(elbow,t)+Vector((0,0,.020*(1-t)));axis=(elbow-shoulder).normalized();radius=.069-.006*t
        else:
            c=elbow.lerp(wrist,t-1);axis=(wrist-elbow).normalized();radius=.063-.022*(t-1)
        u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u).normalized()
        blend=max(0,min(1,(t-.8)/.4))
        w={'upperarm_'+side:1-blend,'lowerarm_'+side:blend}
        if t<.55:
            upper=max(0,t/.55);w={'spine_03':1-upper,'upperarm_'+side:upper}
        rings.append((c,u,v,radius,radius,w,1 if 1.58<=t<1.75 else 0))
    add_rings(rings,16,cap_start=True)
mesh=bpy.data.meshes.new('Tailored jacket');mesh.from_pydata(verts,[],faces);mesh.update()
jacket=bpy.data.objects.new('Hi_vis_jacket',mesh);scene.collection.objects.link(jacket)
mesh.materials.append(hi_vis);mesh.materials.append(reflective)
for p,mat in zip(mesh.polygons,face_materials):p.material_index=mat;p.use_smooth=True
for name in rig_names:jacket.vertex_groups.new(name=name)
for i,boneweights in enumerate(weights):
    for name,weight in boneweights.items():
        if weight>0:jacket.vertex_groups[name].add([i],weight,'REPLACE')
jacket.parent=rig
mod=jacket.modifiers.new('Worker rig','ARMATURE');mod.object=rig

trousers=clothing('Work_trousers',trousers_face,navy,.022)
boot_shell=clothing('Boot_uppers',boots_face,bootmat,.013)
# Skin hidden inside the garments adds no visible detail and costs skinning.
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[p for p in bm.faces if p.index in covered],context='FACES')
bm.to_mesh(body.data);bm.free()


def attach(obj, bone):
    bpy.context.view_layer.update()
    world=obj.matrix_world.copy()
    obj.parent=rig;obj.parent_type='BONE';obj.parent_bone=bone
    bpy.context.view_layer.update();obj.matrix_world=world


def cube(name, loc, scale, mat, bone=None, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Rounded edge','BEVEL');m.width=bevel;m.segments=2
        bpy.ops.object.modifier_apply(modifier=m.name)
    if bone:attach(o,bone)
    return o

# Opaque rounded shoulder gussets overlap torso and sleeve throughout the reach.
# Their two-bone blend follows the arm without exposing the open tube seam.
for side in ['l','r']:
    centre=rig.data.bones['upperarm_'+side].head_local+Vector((0,0,.012))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=centre)
    o=bpy.context.object;o.name='Jacket_shoulder_gusset_'+side
    o.scale=(.068,.080,.069);o.data.materials.append(hi_vis)
    bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    for name in ['spine_03','upperarm_'+side]:
        group=o.vertex_groups.new(name=name);group.add(list(range(len(o.data.vertices))),.5,'REPLACE')
    o.parent=rig;mod=o.modifiers.new('Shoulder rig','ARMATURE');mod.object=rig

# Weld sleeve caps, shoulder transition and torso into one cloth surface.
# Preserve authored skinning by spatially interpolating weights onto the remesh.
from mathutils.kdtree import KDTree
# Retain clean, regularly edged safety tape as a separate weighted surface.
tape=jacket.copy();tape.data=jacket.data.copy();scene.collection.objects.link(tape);tape.name='Sewn_reflective_tape'
bm=bmesh.new();bm.from_mesh(tape.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=1],context='FACES')
bm.to_mesh(tape.data);bm.free()
for v in tape.data.vertices:v.co+=v.normal*.024
parts=[jacket]+[o for o in scene.objects if o.name.startswith('Jacket_shoulder_gusset_')]
points=[]
material_points=[]
for o in parts:
    for face in o.data.polygons:
        material_points.append((o.matrix_world@face.center,1 if o.data.materials[face.material_index].name.startswith('Reflective') else 0))
    for v in o.data.vertices:
        points.append((o.matrix_world@v.co,{o.vertex_groups[g.group].name:g.weight for g in v.groups}, o))
tree=KDTree(len(points))
for i,(point,_,_) in enumerate(points):tree.insert(point,i)
tree.balance()
material_tree=KDTree(len(material_points))
for i,(point,_) in enumerate(material_points):material_tree.insert(point,i)
material_tree.balance()
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=jacket;bpy.ops.object.join()
for mod in list(jacket.modifiers):jacket.modifiers.remove(mod)
thickness=jacket.modifiers.new('Closed cloth volume','SOLIDIFY');thickness.thickness=.028;thickness.offset=0
bpy.ops.object.modifier_apply(modifier=thickness.name)
remesh=jacket.modifiers.new('Continuous sewn shell','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.011;remesh.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=jacket.modifiers.new('Relax shoulder seam','SMOOTH');smooth.factor=.9;smooth.iterations=5
bpy.ops.object.modifier_apply(modifier=smooth.name)
jacket.data.calc_loop_triangles()
dec=jacket.modifiers.new('Cloth mobile topology','DECIMATE');dec.ratio=min(1,4600/len(jacket.data.loop_triangles))
bpy.ops.object.modifier_apply(modifier=dec.name)
for group in list(jacket.vertex_groups):jacket.vertex_groups.remove(group)
for name in rig_names:jacket.vertex_groups.new(name=name)
for v in jacket.data.vertices:
    weighted={}
    nearby=tree.find_n(jacket.matrix_world@v.co,4)
    for _,index,distance in nearby:
        for name,value in points[index][1].items():weighted[name]=weighted.get(name,0)+value/max(distance,.001)**2
    strongest=sorted(weighted.items(),key=lambda item:item[1],reverse=True)[:4]
    total=sum(value for _,value in strongest)
    for name,value in strongest:jacket.vertex_groups[name].add([v.index],value/total,'REPLACE')
jacket.data.materials.clear();jacket.data.materials.append(hi_vis);jacket.data.materials.append(reflective)
for face in jacket.data.polygons:
    face.use_smooth=True
    _,index,_=material_tree.find(jacket.matrix_world@face.center)
    face.material_index=0
mod=jacket.modifiers.new('Worker rig','ARMATURE');mod.object=rig
# Straight trouser leg hems replace jagged polygon selection boundaries.
bm=bmesh.new();bm.from_mesh(trousers.data)
for vert in bm.verts:
    if vert.is_boundary and vert.co.z<.3:vert.co.z=.225
bm.to_mesh(trousers.data);bm.free()

# Actual pocket flaps, zipper and belt give the worker a dressed silhouette.
for x in [-.095,.095]:
    cube('Chest pocket',(x,-.17,1.22),(.075,.014,.065),navy,'spine_03',.006)
    cube('Pocket flap',(x,-.18,1.25),(.081,.012,.018),hi_vis,'spine_03',.004)
cube('Jacket zipper',(0,-.17,1.12),(.009,.008,.31),black,'spine_03')
cube('Belt buckle',(0,-.13,.87),(.042,.025,.027),black,'pelvis',.004)
for side in ['l','r']:
    foot=rig.data.bones['foot_'+side]
    cube('Boot sole_'+side,(foot.head_local.x,-.075,.025),(.135,.27,.044),black,'foot_'+side,.015)
    cube('Leather toe box_'+side,(foot.head_local.x,-.09,.083),(.129,.23,.105),bootmat,'foot_'+side,.035)
    cube('Toe reinforcement_'+side,(foot.head_local.x,-.17,.085),(.129,.068,.095),black,'foot_'+side,.025)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=1,depth=1,location=(foot.head_local.x,-.002,.145))
    ankle=bpy.context.object;ankle.name='Leather ankle cuff_'+side;ankle.scale=(.065,.069,.18)
    ankle.data.materials.append(bootmat)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in ankle.data.polygons:p.use_smooth=True
    attach(ankle,'foot_'+side)
    for row in range(3):
        cube('Boot lace_'+side,(foot.head_local.x,-.045-row*.018,.141),(.065,.006,.007),black,'foot_'+side,.002)

# Helmet dome, brim and top ridge, all attached to the head bone.
head=rig.data.bones['head'];top=max(v.co.z for v in body.data.vertices)
verts=[];faces=[];segments=24;rings=8
for j in range(rings+1):
    phi=(math.pi/2)*j/rings
    for i in range(segments):
        theta=math.tau*i/segments
        verts.append((.103*math.cos(phi)*math.cos(theta),head.head_local.y+.131*math.cos(phi)*math.sin(theta),top-.055+.105*math.sin(phi)))
for j in range(rings):
    for i in range(segments):
        faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
mesh=bpy.data.meshes.new('Helmet_shell');mesh.from_pydata(verts,[],faces);mesh.update()
helmet=bpy.data.objects.new('Hard_hat_shell',mesh);scene.collection.objects.link(helmet);mesh.materials.append(hi_vis)
for p in mesh.polygons:p.use_smooth=True
attach(helmet,'head')
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=8,radius=1,location=(0,head.head_local.y-.025,top-.055))
brim=bpy.context.object;brim.name='Hard_hat_brim';brim.scale=(.124,.165,.009);brim.data.materials.append(hi_vis)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);attach(brim,'head')
cube('Helmet crown rib',(0,head.head_local.y,top+.045),(.025,.11,.014),hi_vis,'head',.005)
# Eyes remain small and naturally seated in the actual MakeHuman sockets.
for i,c in enumerate(eye_centres):
    for label,offset,scale,mat in [('Eye',Vector(),(.012,.012,.012),white),('Iris',Vector((0,-.014,-.008)),(.0045,.003,.0035),iris)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=c+offset)
        o=bpy.context.object;o.name=label+str(i);o.scale=scale;o.data.materials.append(mat)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);attach(o,'head')

# Clamp skin weights before export, avoiding implicit exporter changes.
for o in [body,jacket,trousers,boot_shell]:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    # Remove helper groups so only real deform bones enter the reduction.
    for group in list(o.vertex_groups):
        if group.name not in rig_names:o.vertex_groups.remove(group)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)

# Keep the single worker within the mobile prototype geometry budget.
# Skin weights interpolate through collapse; all simplification happens in rest pose.
for o,ratio in [(body,.45),(trousers,.45),(boot_shell,.18)]:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Mobile topology','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)

# Author a repeatable inspection: glance at meter, raise test probe to terminal,
# hold the contact, return to meter. Feet, pelvis, and root never translate.
targets={}
for side in ['l','r']:
    target=bpy.data.objects.new('Hand_target_'+side,None);scene.collection.objects.link(target);targets[side]=target
    ik=rig.pose.bones['lowerarm_'+side].constraints.new('IK');ik.name='Tool contact';ik.target=target;ik.chain_count=2
    hand=rig.pose.bones['hand_'+side];hand.rotation_mode='XYZ';hand.rotation_euler.x=-.25
    for finger in ['index','middle','ring','pinky']:
        for segment,angle in [('01',.25),('02',.45),('03',.25)]:
            bone=rig.pose.bones[f'{finger}_{segment}_{side}'];bone.rotation_mode='XYZ';bone.rotation_euler.x=angle
            if args.trade=='plumbing' or (side=='l' and args.trade=='electrical'):
                bone.rotation_euler.x={'01':.65,'02':1.0,'03':.55}[segment]
            elif finger!='index':
                bone.rotation_euler.x={'01':.55,'02':.9,'03':.5}[segment]
            if args.trade=='mechanical' and side=='r' and finger=='index':bone.rotation_euler.x=.03
# Each trade has deliberately different task timing and hand trajectories.
# Positions are worker-local; the integration rotates the worker toward its bay.
poses={
'electrical':[(0,(.24,-.36,1.06),(-.24,-.27,1.07)),(.2,(.24,-.36,1.06),(-.24,-.27,1.07)),(.4,(.24,-.36,1.06),(-.24,-.40,1.20)),(.6,(.24,-.36,1.06),(-.24,-.40,1.20)),(.8,(.24,-.36,1.06),(-.24,-.27,1.07)),(1,(.24,-.36,1.06),(-.24,-.27,1.07))],
'plumbing':[(0,(.18,-.30,1.12),(-.24,-.27,1.10)),(.15,(.18,-.30,1.12),(-.24,-.40,1.17)),(.27,(.18,-.38,1.14),(-.24,-.40,1.17)),(.38,(.18,-.38,1.14),(-.20,-.40,1.19)),(.49,(.18,-.38,1.14),(-.24,-.40,1.17)),(.60,(.18,-.38,1.14),(-.20,-.40,1.19)),(.71,(.18,-.38,1.14),(-.24,-.40,1.17)),(.85,(.18,-.30,1.12),(-.24,-.27,1.10)),(1,(.18,-.30,1.12),(-.24,-.27,1.10))],
'carpentry':[(0,(.24,-.32,1.02),(-.24,-.27,1.07)),(.16,(.24,-.40,1.07),(-.24,-.40,1.115)),(.32,(.24,-.40,1.07),(-.24,-.40,1.115)),(.44,(.24,-.40,1.07),(-.24,-.38,1.115)),(.50,(.24,-.40,1.07),(-.24,-.42,1.115)),(.56,(.24,-.40,1.07),(-.24,-.38,1.115)),(.62,(.24,-.40,1.07),(-.24,-.42,1.115)),(.74,(.24,-.32,1.02),(-.24,-.27,1.07)),(1,(.24,-.32,1.02),(-.24,-.27,1.07))],
'mechanical':[(0,(.14,-.33,1.14),(-.12,-.34,1.17)),(.14,(.14,-.33,1.14),(-.10,-.36,1.18)),(.20,(.14,-.33,1.14),(-.12,-.34,1.17)),(.35,(.14,-.33,1.14),(-.24,-.40,1.20)),(.53,(.14,-.33,1.14),(-.24,-.40,1.20)),(.68,(.14,-.33,1.14),(-.12,-.34,1.17)),(.74,(.14,-.33,1.14),(-.10,-.36,1.18)),(.80,(.14,-.33,1.14),(-.12,-.34,1.17)),(1,(.14,-.33,1.14),(-.12,-.34,1.17))]
}[args.trade]
keys=[(round(t*duration*30)+1,left,right) for t,left,right in poses]
for frame,left,right in keys:
    for side,position in [('l',left),('r',right)]:
        targets[side].location=position;targets[side].keyframe_insert('location',frame=frame)
    pose=rig.pose.bones['head'];pose.rotation_mode='XYZ'
    progress=(frame-1)/(duration*30)
    pose.rotation_euler.x=.12 if progress<.30 or progress>.70 else -.06
    if args.trade=='carpentry':pose.rotation_euler.x=.18
    pose.keyframe_insert('rotation_euler',frame=frame)
    if args.trade=='plumbing':
        hand=rig.pose.bones['hand_r']
        hand.rotation_euler.y=.45*math.sin(progress*math.tau*3) if .27<=progress<=.71 else 0
        hand.keyframe_insert('rotation_euler',frame=frame)
# Lock actual tool contact, not merely a guessed wrist coordinate. The local
# tip/throat is defined in the same initial pose used to construct the tool.
scene.frame_set(1);bpy.context.view_layer.update()
initial_right=rig.pose.bones['hand_r'].matrix.copy()
anchor=(rig.pose.bones['index_02_r'].head+rig.pose.bones['thumb_03_r'].head)/2
contact_checks=[]
if args.trade in ['electrical','plumbing']:
    local_tip=initial_right.inverted() @ (anchor+Vector((0,-.0855,.025) if args.trade=='electrical' else (0,-.018,.145)))
    contact_start,contact_end=(.4,.6) if args.trade=='electrical' else (.27,.71)
    contact_first=round(contact_start*duration*30)+1
    contact_last=round(contact_end*duration*30)+1
    # Station authoritative targets, converted through worker placement/yaw.
    target=Vector((-.24,-.375,1.20-.0305) if args.trade=='electrical' else (-.16,-.50,1.38))
    rotation_target=bpy.data.objects.new('Tool_orientation',None);scene.collection.objects.link(rotation_target)
    rotation_target.rotation_mode='QUATERNION'
    rotation_constraint=rig.pose.bones['hand_r'].constraints.new('COPY_ROTATION')
    rotation_constraint.target=rotation_target;rotation_constraint.owner_space='WORLD';rotation_constraint.target_space='WORLD'
    original_targets=[]
    for frame in range(1,scene.frame_end+1):
        scene.frame_set(frame);original_targets.append(targets['r'].location.copy())
    for frame in range(1,scene.frame_end+1):
        progress=(frame-1)/(duration*30)
        angle=0
        if args.trade=='plumbing' and contact_first<=frame<=contact_last:
            angle=.25*math.sin((frame-contact_first)/(contact_last-contact_first)*math.tau*2)
        rotation=Matrix.Rotation(angle,4,'Y')@initial_right.to_quaternion().to_matrix().to_4x4()
        rotation_target.rotation_quaternion=rotation.to_quaternion();rotation_target.keyframe_insert('rotation_quaternion',frame=frame)
        if contact_first<=frame<=contact_last:
            position=target-rotation.to_3x3()@local_tip
            targets['r'].location=position;targets['r'].keyframe_insert('location',frame=frame)
            contact_checks.append((frame,target.copy(),local_tip.copy()))
    targets['orientation']=rotation_target
elif args.trade=='mechanical':
    # A true index-finger touch on the worker-facing tablet screen at both taps.
    local_tip=initial_right.inverted()@rig.pose.bones['index_03_r'].tail
    left_matrix=rig.pose.bones['hand_l'].matrix.copy()
    left_palm=left_matrix@Vector((0,.065,0))
    target=left_palm+Vector((-.045,-.004,.025))
    rotation_target=bpy.data.objects.new('Tablet_touch_orientation',None);scene.collection.objects.link(rotation_target)
    rotation_target.rotation_mode='QUATERNION';rotation_target.rotation_quaternion=initial_right.to_quaternion()
    constraint=rig.pose.bones['hand_r'].constraints.new('COPY_ROTATION');constraint.target=rotation_target
    constraint.owner_space='WORLD';constraint.target_space='WORLD'
    for low,high in [(.13,.15),(.73,.75)]:
        for frame in range(round(low*duration*30)+1,round(high*duration*30)+2):
            targets['r'].location=target-initial_right.to_3x3()@local_tip
            targets['r'].keyframe_insert('location',frame=frame)
            contact_checks.append((frame,target.copy(),local_tip.copy()))
    targets['orientation']=rotation_target
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.nla.bake(frame_start=1,frame_end=scene.frame_end,step=1,only_selected=False,
    visual_keying=True,clear_constraints=True,use_current_action=True,bake_types={'POSE'})
rig.animation_data.action.name=clip_names[args.trade]
for target in targets.values():bpy.data.objects.remove(target,do_unlink=True)
scene.frame_set(1);bpy.context.view_layer.update()

# Tool attachments are evaluated against posed hand bones and keep their grasp.
left=rig.matrix_world @ rig.pose.bones['hand_l'].matrix
left.translation = left @ Vector((0,.065,0))
right=rig.matrix_world @ rig.pose.bones['hand_r'].matrix
right.translation = rig.matrix_world @ ((rig.pose.bones['index_02_r'].head+rig.pose.bones['thumb_03_r'].head)/2)
if args.trade=='electrical':
    cube('Handheld_meter',left.translation+Vector((0,-.025,.0)),(.07,.042,.13),hi_vis,'hand_l',.006)
    cube('Meter_screen',left.translation+Vector((0,-.048,.025)),(.045,.006,.04),black,'hand_l',.002)
    cube('Meter_selector',left.translation+Vector((0,-.049,-.025)),(.022,.009,.022),navy,'hand_l',.003)
    cube('Insulated_probe',right.translation+Vector((0,-.025,.025)),(.014,.085,.014),black,'hand_r',.003)
    cube('Probe_tip',right.translation+Vector((0,-.073,.025)),(.004,.025,.004),reflective,'hand_r')
elif args.trade=='plumbing':
    cube('Wrench handle',right.translation+Vector((0,-.018,.025)),(.018,.019,.16),bootmat,'hand_r',.005)
    cube('Wrench head',right.translation+Vector((0,-.018,.095)),(.115,.025,.03),reflective,'hand_r',.005)
    for x in [-.05,.05]:cube('Wrench jaw',right.translation+Vector((x,-.018,.145)),(.017,.025,.09),reflective,'hand_r',.003)
elif args.trade=='carpentry':
    cube('Tape measure housing',left.translation+Vector((0,-.025,0)),(.06,.045,.055),hi_vis,'hand_l',.009)
    # The measurement spans the timber while the right hand marks it.
    cube('Carpenter pencil',right.translation+Vector((0,-.025,.018)),(.008,.008,.105),hi_vis,'hand_r',.002)
    cube('Graphite point',right.translation+Vector((0,-.025,-.039)),(.004,.004,.009),black,'hand_r')
else:
    cube('Inspection tablet',left.translation+Vector((-.045,-.025,.025)),(.19,.022,.14),black,'hand_l',.01)
    cube('Tablet glass',left.translation+Vector((-.045,-.011,.025)),(.17,.005,.12),navy,'hand_l',.006)
    for row in range(4):cube('Tablet checklist',left.translation+Vector((-.045,-.007,.060-row*.023)),(.12,.002,.005),reflective,'hand_l')

# Consolidate accessories sharing a bone: many shoelaces need not be many draws.
# Different materials remain distinct glTF primitives inside the merged mesh.
for bone_name in ['head','spine_03','foot_l','foot_r','hand_l','hand_r']:
    pieces=[o for o in scene.objects if o.type=='MESH' and o.parent==rig and o.parent_type=='BONE' and o.parent_bone==bone_name]
    if len(pieces)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in pieces:o.select_set(True)
        bpy.context.view_layer.objects.active=pieces[0]
        bpy.ops.object.join();bpy.context.object.name='Accessories_'+bone_name

# Validate the authored loop before writing an asset. Bone heads at endpoints
# must match and planted feet must not move throughout the cycle.
endpoints=[];foot_samples=[]
for frame in [1]+[round(duration*30*t)+1 for t in [.2,.4,.6,.8,1]]:
    scene.frame_set(frame);bpy.context.view_layer.update()
    for bone in rig.pose.bones:
        assert all(math.isfinite(v) for row in bone.matrix for v in row), f'Nonfinite pose {bone.name}'
    foot_samples.append([tuple(rig.pose.bones[n].head) for n in ['foot_l','foot_r']])
    if frame in [1,scene.frame_end]:endpoints.append([tuple(b.matrix) for b in rig.pose.bones])
assert all((Vector(foot_samples[0][i])-Vector(s[i])).length<1e-5 for s in foot_samples for i in range(2))
for a,b in zip(endpoints[0],endpoints[1]):
    assert all(abs(x-y)<1e-4 for ar,br in zip(a,b) for x,y in zip(ar,br)), 'Loop endpoint mismatch'
contact_errors=[]
for frame,target,local_tip in contact_checks:
    scene.frame_set(frame);bpy.context.view_layer.update()
    actual=rig.pose.bones['hand_r'].matrix@local_tip
    contact_errors.append((actual-target).length)
assert not contact_errors or max(contact_errors)<.003, f'Tool contact exceeds 3 mm: {max(contact_errors)}'
scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/(asset_name+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(out/(asset_name+'.glb')),export_format='GLB',
    export_cameras=False,export_lights=False,export_animations=True,
    export_anim_single_armature=True,export_force_sampling=True)

# Validate every exported floating-point accessor, including animation data and
# inverse bind matrices. A clean Blender scene is not sufficient proof of GLB.
raw=(out/(asset_name+'.glb')).read_bytes();jl=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+jl]);bin_offset=20+jl+8
components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
for index,accessor in enumerate(doc.get('accessors',[])):
    if accessor['componentType']!=5126 or 'bufferView' not in accessor:continue
    view=doc['bufferViews'][accessor['bufferView']];count=components[accessor['type']]
    offset=bin_offset+view.get('byteOffset',0)+accessor.get('byteOffset',0)
    stride=view.get('byteStride',count*4)
    for i in range(accessor['count']):
        assert all(math.isfinite(x) for x in struct.unpack_from('<'+'f'*count,raw,offset+i*stride)), f'Nonfinite accessor {index}'
triangles=0
for o in scene.objects:
    if o.type=='MESH':o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
report={'stage':'four-trade worker prototype','trade':args.trade,'clip':clip_names[args.trade],'generator':'MPFB 2.0.18 / Blender 4.5.3',
    'duration_seconds':duration,'bones':len(rig.data.bones),'triangles':triangles,
    'mpfb_source_sha256':mpfb_source_digest,
    'mesh_objects':sum(o.type=='MESH' for o in scene.objects),
    'validation':{'finite_export_accessors':True,'stationary_feet':True,'matching_loop_endpoints':True},
    'contact_validation':{'sampled_frames':len(contact_errors),'max_error_metres':max(contact_errors) if contact_errors else None,'scope':'Electrical probe tip / plumbing wrench throat / mechanical fingertip to authoritative contact target'},
    'limitations':['Custom workwear is prototype tailoring, not a scanned garment','Facial texture detail and headset performance validation pending'],
    'licence':'MakeHuman core assets CC0; original clothing, accessories, textures and animation'}
(out/(asset_name+'-report.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
