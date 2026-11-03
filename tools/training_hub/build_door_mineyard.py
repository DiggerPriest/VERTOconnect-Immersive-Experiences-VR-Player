import bpy, math, random
from mathutils import Vector
from datetime import datetime
s=bpy.context.scene
root='/Users/rpriest/Library/CloudStorage/OneDrive-VertoPtyLtd/Documents/ChatGPT/immivio-360-player/build/training-hub/'
bpy.ops.wm.save_as_mainfile(filepath=root+'source-checkpoints/before_door_yard_'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.blend',copy=True)
col=bpy.data.collections.new('ENV_MineYard_Revision');s.collection.children.link(col)
def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.78 if not metal else .43;p.inputs['Metallic'].default_value=metal;return m
earth=mat('YARD_ochre_earth',(.27,.16,.085));rock=mat('YARD_cut_rock',(.34,.25,.17));road=mat('YARD_haul_road',(.42,.32,.22));steel=bpy.data.materials['M_galvanised'];dark=bpy.data.materials['M_steel_charcoal'];yellow=bpy.data.materials['M_safety_yellow']
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);col.objects.link(o);d.materials.append(m);return o
def box(n,c,d,m):
 x,y,z=c;a,b,h=[v/2 for v in d];v=[(x+sx*a,y+sy*b,z+sz*h) for sx,sy,sz in [(-1,-1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]]
 return mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
for o in list(s.objects):
 if o.name=='PRP_cylrack' or o.name.startswith(('PRP_hydcyl','PRP_hydrod')):
  o.location.x-=14
for n in ['ENV_ext_berm','ENV_ext_stockpile','ENV_ext_fence_posts','ENV_ext_fence_rails']:
 o=s.objects[n];o.hide_render=True;o.hide_set(True)
# Mask old cross-opening reveals with an evaluated boolean in the export copy.
cut=box('YARD_reveal_opening_cutter',(1,22.2,3.6),(8.0,1,7.2),dark);cut.hide_render=True;cut.hide_set(True)
o=s.objects['ENV_wall_reveals'];mod=o.modifiers.new('Clear rear doorway only','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
# Continuous profiled steel curtain, 3.6 m lower edge, 7.1 m upper edge.
v=[];f=[]
for j in range(141):
 z=3.6+3.5*j/140;y=21.98+(.035 if j%4 in (1,2) else 0)
 v.extend([(-3.0,y,z),(5.0,y,z)])
 if j:f.append((2*j-2,2*j-1,2*j+1,2*j))
o=mesh('YARD_roller_curtain',v,f,steel);sol=o.modifiers.new('Steel thickness','SOLIDIFY');sol.thickness=.012
box('YARD_door_bottom_rail',(1,21.94,3.6),(8.05,.15,.13),dark)
box('YARD_roller_housing',(1,21.65,7.5),(8.6,.8,.7),steel)
for x in [-3.1,5.1]:
 box('YARD_guide_'+str(x),(x,21.9,3.55),(.18,.24,7.1),dark)
box('YARD_door_control',(5.48,21.65,1.45),(.25,.15,.35),yellow)
# Extend earth under the mine vista; keep the existing approach apron.
box('YARD_ground',(0,83,-.15),(150,124,.28),earth)
mesh('YARD_haul_route',[(-3,22,.012),(5,22,.012),(14,60,.012),(35,112,.012),(23,112,.012),(3,60,.012)],[(0,1,2,5),(5,2,3,4)],road)
random.seed(11)
# Broad stepped cut faces, with irregular continuous rims and wide benches.
for tier in range(4):
 verts=[]
 for i in range(49):
  x=-75+i*3.125;y=53+tier*13+.003*x*x+2*math.sin(i*.55);z=tier*3.0
  verts.extend([(x,y,z),(x,y+4,z+2.7+random.uniform(-.2,.2)),(x,y+13,z+2.7)])
 faces=[]
 for i in range(48):
  a=3*i;faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
 mesh('YARD_quarry_bench_'+str(tier),verts,faces,rock if tier%2==0 else earth)
# Irregular ore piles to either side of the access road.
for k,(cx,cy,r,h) in enumerate([(-11,35,7,3.7),(15,43,8,4.6),(-22,48,10,5)]):
 verts=[(cx+.7,cy-.3,h)]+[(cx+math.cos(i*math.tau/18)*r*(1+random.uniform(-.12,.12)),cy+math.sin(i*math.tau/18)*r*.7,0) for i in range(18)]
 mesh('YARD_ore_stockpile_'+str(k),verts,[(0,1+i,1+(i+1)%18) for i in range(18)],rock)
# Low road-edge safety bunds, with an unobstructed apron.
for side in [-1,1]:
 for i in range(6):
  x=(side*6)+i*.15;y=27+i*3
  box('YARD_edge_marker_'+str(side)+'_'+str(i),(x,y,.45),(.14,.14,.9),yellow)
# Push sky panels beyond new terrain so they cannot cut across it.
s.objects['ENV_ext_sky'].location.y+=110;s.objects['ENV_ext_sky'].scale.x*=2.5
s.objects['ENV_ext_sky_side'].hide_render=True;s.objects['ENV_ext_sky_side'].hide_set(True)
bpy.context.view_layer.update()
result={'created':len(col.objects),'rack_relocated':True,'opening_width':8.0,'clear_height':3.535,'added_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in col.objects if o.type=='MESH')}
