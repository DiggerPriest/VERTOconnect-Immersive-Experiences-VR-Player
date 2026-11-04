"""Bake short-range static ambient occlusion into vertex colour, with no new textures.
This is offline geometric shading, not a simulation of direct or moving shadows.
"""
import bpy,sys,math,json,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
source,target=sys.argv[sys.argv.index('--')+1:];assert not Path(target).exists();assert source!=target
bpy.ops.wm.open_mainfile(filepath=source);s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s;s.frame_set(1)
deps=bpy.context.evaluated_depsgraph_get()
def static(o):
 current=o
 while current:
  if current.animation_data or current.constraints:return False
  current=current.parent
 return True
occluders=[o for o in s.objects if o.type=='MESH' and not o.hide_render and static(o) and not o.name.startswith('YARD_sky')]
vertices=[];polygons=[]
for o in occluders:
 obj=o.evaluated_get(deps);me=obj.to_mesh();base=len(vertices)
 vertices.extend(obj.matrix_world@v.co for v in me.vertices);polygons.extend(tuple(base+i for i in p.vertices) for p in me.polygons);obj.to_mesh_clear()
tree=BVHTree.FromPolygons(vertices,polygons)
targets=[o for o in occluders if o.name.startswith(('FIT_','EXP_','STR_','ENV_wall','WKS_gallery')) and o.data.vertices]
materials={};report={'method':'16 cosine hemisphere rays, 1.5m radius, distance-weighted; static occluders only','meshes':[]};n=16;total=0
for o in targets:
 if o.data.users>1:o.data=o.data.copy()
 me=o.data;attr=me.color_attributes.get('WorkshopAO') or me.color_attributes.new(name='WorkshopAO',type='FLOAT_COLOR',domain='POINT')
 me.color_attributes.active_color=attr;me.color_attributes.render_color_index=list(me.color_attributes).index(attr)
 normal_matrix=o.matrix_world.to_3x3().inverted().transposed();values=[]
 for v in me.vertices:
  normal=(normal_matrix@v.normal).normalized();origin=o.matrix_world@v.co+normal*.015
  tangent=normal.cross(Vector((0,0,1)) if abs(normal.z)<.9 else Vector((1,0,0))).normalized();bitangent=normal.cross(tangent)
  occlusion=0
  for k in range(n):
   radius=math.sqrt((k+.5)/n);angle=k*2.39996323
   direction=tangent*(radius*math.cos(angle))+bitangent*(radius*math.sin(angle))+normal*math.sqrt(1-radius*radius)
   hit,_,_,distance=tree.ray_cast(origin,direction,1.5)
   if hit is not None:occlusion+=(1-distance/1.5)**2
  value=1-.38*occlusion/n;attr.data[v.index].color=(value,value,value,1);values.append(value)
 total+=len(values)
 for i,mat in enumerate(list(me.materials)):
  if not mat or not mat.use_nodes:continue
  principled=mat.node_tree.nodes.get('Principled BSDF')
  if not principled or principled.inputs['Base Color'].is_linked:continue
  if mat.name not in materials:
   copied=mat.copy();copied.name='AO_'+mat.name;p=copied.node_tree.nodes.get('Principled BSDF');color=tuple(p.inputs['Base Color'].default_value)
   vertex=copied.node_tree.nodes.new('ShaderNodeVertexColor');vertex.layer_name='WorkshopAO'
   mix=copied.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=color
   copied.node_tree.links.new(vertex.outputs['Color'],mix.inputs[2]);copied.node_tree.links.new(mix.outputs['Color'],p.inputs['Base Color']);materials[mat.name]=copied
  me.materials[i]=materials[mat.name]
 report['meshes'].append({'name':o.name,'vertices':len(values),'min':min(values),'mean':sum(values)/len(values)})
report['total_vertices']=total;report['materials']=len(materials)
s.camera=s.objects['CAM_main'];bpy.ops.wm.save_as_mainfile(filepath=target,copy=True);Path(target).with_suffix('.ao.json').write_text(json.dumps(report,indent=2));print('VERTEX_AO',len(targets),'meshes',total,'vertices',len(materials),'materials')
