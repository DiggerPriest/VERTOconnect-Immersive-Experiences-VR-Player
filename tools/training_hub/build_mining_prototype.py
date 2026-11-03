"""Isolated mining composition study. Blender4.5; no live-app files modified.
Run with --output build/training-hub/mining-prototype. Requires reviewed PolyHaven
rock_boulder_dry {diff,nor_gl,rough}4K JPGs in output/textures (see provenance.json).
"""
import argparse, json, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
rng=random.Random(46)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,col,metal=0,rough=.65,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 if emit:b.inputs['Emission Color'].default_value=(*col,1);b.inputs['Emission Strength'].default_value=emit
 return m
rock=mat('CC0_Rock_Boulder_Dry',(.36,.32,.27));nodes=rock.node_tree.nodes;links=rock.node_tree.links;bsdf=nodes.get('Principled BSDF')
for role,input in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
 image=bpy.data.images.load(str(out/'textures'/f'rock_boulder_dry_{role}_4k.jpg'));image.scale(2048,2048)
 if role!='diff':image.colorspace_settings.name='Non-Color'
 tex=nodes.new('ShaderNodeTexImage');tex.image=image
 if role=='nor_gl':
  normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.85;links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs[input])
 else:links.new(tex.outputs['Color'],bsdf.inputs[input])
steel=mat('Galvanised support steel',(.19,.23,.25),.7,.4);rust=mat('Oxidised rail web',(.22,.12,.075),.5,.65)
rail=mat('Polished rail crown',(.38,.39,.38),.82,.27);timber=mat('Creosote sleeper',(.10,.075,.045),0,.95)
gold=mat('Safety ochre',(.95,.48,.035),.15,.45);black=mat('Graphite fixtures',(.025,.035,.04),.3,.45)
blue=mat('Water line blue',(.035,.18,.27),.2,.4);red=mat('Rescue red',(.55,.035,.022),.2,.5)
white=mat('Cool work light',(.64,.83,1),0,.3,4);amber=mat('Amber practical', (1,.48,.12),0,.3,4);green=mat('System healthy',(.1,.8,.4),0,.3,3)
def cube(name,loc,scale,material,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Manufactured edge','BEVEL');mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def tube(name,a,b,r,material,verts=12):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');o.data.materials.append(material);return o
def label(text,loc,size,material):
 curve=bpy.data.curves.new(text,'FONT');curve.body=text;curve.size=size;curve.align_x='CENTER';curve.extrude=.001
 o=bpy.data.objects.new(text,curve);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(material)
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def offset(y):return .018*max(0,y-8)**1.5
# Open-bottom irregular horseshoe tunnel, deliberately modelled through real depth.
profile=[(3,0),(3,1.3)]+[(3*math.cos(t),1.3+3*math.sin(t)) for t in [i*math.pi/32 for i in range(1,33)]]+[(-3,0)]
profile_distance=[0.0]
for i in range(1,len(profile)):
 profile_distance.append(profile_distance[-1]+math.dist(profile[i-1],profile[i]))
vertices=[];uvs=[];rings=49
for j in range(rings):
 y=j*.6
 for i,(x,z) in enumerate(profile):
  disturbance=.10*math.sin(i*1.74+j*.78)+rng.uniform(-.075,.075)
  vertices.append((x*(1+disturbance*.15)+offset(y),y,z+disturbance if z>.1 else z))
  uvs.append((profile_distance[i]/1.8,y/1.8))
faces=[];n=len(profile)
for j in range(rings-1):
 for i in range(n-1):faces.append((j*n+i,(j+1)*n+i,(j+1)*n+i+1,j*n+i+1))
mesh=bpy.data.meshes.new('Excavated rock shell');mesh.from_pydata(vertices,[],faces);mesh.update();ob=bpy.data.objects.new('Continuous excavated tunnel',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(rock)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 for loop in poly.loop_indices:uv.data[loop].uv=uvs[mesh.loops[loop].vertex_index]
# Continuous rock portal surrounds the opening; no disconnected floating boulders.
verts=[];faces=[]
for y in [-.20,1.2]:
 for radius in [1.0,1.60]:
  for i,(x,z) in enumerate(profile):
   perturb=.08*math.sin(i*2.1)
   verts.append((x*radius,y+perturb,z*radius))
n=len(profile)
for i in range(n-1):
 faces.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
mesh=bpy.data.meshes.new('Rock portal');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Rock excavation portal',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(rock)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 for loop in poly.loop_indices:
  vertex=mesh.vertices[mesh.loops[loop].vertex_index].co;uv.data[loop].uv=(vertex.x/1.8,vertex.z/1.8)
# Ground uses same natural granular material with explicit physical UV scale.
floor=cube('Cut rock floor',(0,11,-.12),(11,37,.22),rock,0)
for poly in floor.data.polygons:
 for loop in poly.loop_indices:
  vertex=floor.matrix_world @ floor.data.vertices[floor.data.loops[loop].vertex_index].co;floor.data.uv_layers.active.data[loop].uv=(vertex.x/1.8,vertex.y/1.8)
for i in range(90):
 x=rng.choice([-1,1])*rng.uniform(1.4,2.8);y=rng.uniform(-1,25)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.05,.16),location=(x+offset(y),y,.03));o=bpy.context.object;o.name='Small ballast';o.scale=(1.6,1,.7);o.data.materials.append(rock)
# Steel arch ribs with baseplates and longitudinal reinforcement.
for y in [.15,4,8,12,16,20,24,28]:
 rib=[(x*.96+offset(y),y,z*.96) for x,z in profile]
 for index in range(len(rib)-1):tube('Tunnel steel arch',rib[index],rib[index+1],.065,steel,8)
 for side in [-1,1]:cube('Arch foot plate',(side*2.87+offset(y),y,.04),(.38,.42,.08),steel)
 for x in [-2.1,0,2.1]:
  z=1.3+math.sqrt(9-x*x)-.12
  if y<28:tube('Arch longitudinal tie',(x+offset(y),y,z),(x+offset(y+4),y+4,z),.028,steel)
# Services on each wall: water lines, cables, ventilating duct with flange collars.
for y in range(0,28,2):
 for x,z,r,m in [(2.62,2.1,.07,blue),(2.60,2.5,.045,gold),(-1.75,3.52,.23,steel)]:
  tube('Tunnel service',(x+offset(y),y,z),(x+offset(y+2),y+2,z),r,m,16)
  tube('Service coupling',(x+offset(y),y-.04,z),(x+offset(y),y+.04,z),r*1.16,black,16)
 for z in [1.85,1.93,2.01,2.09]:tube('Power cable',(-2.65+offset(y),y,z),(-2.65+offset(y+2),y+2,z),.018,black,8)
 cube('Cable support',(-2.7+offset(y),y,1.95),(.15,.055,.44),steel,.006)
# Practical luminaires recede through the tunnel; emission is visible in glTF.
for index,y in enumerate([.8,4.8,8.8,12.8,16.8,20.8,24.8]):
 for side in [-1,1]:
  x=side*2.48+offset(y);cube('Lamp bracket',(x,y,2.83),(.24,.30,.10),black)
  cube('Receding practical',(x,y-.05,2.77),(.19,.32,.055),amber if side>0 else white,.008)
# Accessible entrance details.
for side in [-1,1]:
 for y in [-2.2,-.7]:
  tube('Safety post',(side*2.22,y,0),(side*2.22,y,1.0),.055,gold)
  cube('Post base',(side*2.22,y,.035),(.25,.25,.07),black)
 tube('Safety handrail',(side*2.22,-2.2,.9),(side*2.22,-.7,.9),.035,gold)
cube('Ventilation control cabinet',(-3.5,-.6,1.16),(.72,.32,1.22),steel,.04)
cube('Control face',(-3.5,-.775,1.16),(.61,.035,1.08),black,.02)
label('VENTILATION',(-3.5,-.804,1.55),.085,white)
for x in [-3.68,-3.5,-3.32]:tube('Healthy status indicator',(x,-.81,1.31),(x,-.83,1.31),.026,green)
for z in [.78,.85,.92]:cube('Louvre',(-3.5,-.81,z),(.45,.02,.014),steel,.002)
cube('Mine entrance sign',(0,-.55,4.65),(5.4,.18,.57),black,.035)
label('VERTOconnect',(0,-.66,4.64),.30,gold)
label('UNDERGROUND  /  TRAINING GALLERY',(0,-.661,4.45),.10,white)
cube('Rescue equipment cabinet',(3.7,-.6,.9),(.72,.46,1.5),red,.04)
label('RESCUE',(3.7,-.845,1.25),.13,white)
label('+',(3.7,-.845,.84),.42,white)
# Existing tunnel becomes one zone at the back of a full factory.
for o in bpy.context.scene.objects:o.location.y+=15
concrete=mat('Workshop concrete',(.28,.31,.33),0,.92)
wall=mat('Pale workshop panels',(.53,.58,.60),.12,.8)
rubber=mat('Heavy duty tyres',(.025,.028,.03),0,.98)
glass=mat('Cab dark glazing',(.035,.10,.14),.35,.22)
cube('Factory slab',(0,-2.5,-.20),(42,37,.3),concrete,.02)
# Back wall leaves a full opening around mine portal; no cranes or gantries.
for x in [-13,13]:cube('Factory rear wall',(x,15,5),(16,.25,10),wall)
cube('Rear wall above mine',(0,15,8),(10,.25,4),wall)
for x in [-21,21]:cube('Side wall',(x,-2.5,5),(.25,35,10),wall)
cube('Front wall',(0,-20,5),(42,.25,10),wall)
for y in [-19,-12,-5,2,9,15]:
 for x in [-20.5,20.5]:cube('Building column',(x,y,5),(.35,.42,10),steel)
 cube('Fixed roof beam',(0,y,9.8),(41,.28,.4),steel)
for x in [-16,-8,0,8,16]:
 cube('Ceiling roof panel',(x,-2.5,10.1),(7.5,35,.12),wall)
 for y in [-14,-5,4,12]:cube('Ceiling luminaire',(x,y,9.6),(.18,3,.08),white)
# Two large axial fans flanking the portal; rotors remain separate for animation.
for side in [-1,1]:
 x=side*6.4;y=13.1;z=3.0
 for i in range(48):
  a=i*math.tau/48;b=(i+1)*math.tau/48
  tube('Fan outer ring',(x+1.5*math.cos(a),y,z+1.5*math.sin(a)),(x+1.5*math.cos(b),y,z+1.5*math.sin(b)),.13,steel)
 tube('Fan motor hub',(x,y-.2,z),(x,y+.6,z),.27,black,24)
 for i in range(6):
  a=i*math.tau/6
  blade=cube('Fan rotor blade',(x+.8*math.cos(a),y,z+.8*math.sin(a)),(1.2,.12,.32),gold,.06);blade.rotation_euler.y=-a
 for dx in [-1.05,1.05]:cube('Fan support',(x+dx,y,1),(.18,.35,2),steel)
 tube('Fan duct',(x,y+.2,z),(x,16,z),1.40,steel,40)
 label('FRESH AIR',(x,y-.3,4.85),.25,gold)
# Parked haul-truck maintenance zone: six massive wheels, raised bonnet and exposed engine.
x=10;y=1
cube('Truck chassis',(x,y,1.5),(3.8,8,.38),black,.12)
for yy in [-2,2.6,4.2]:
 for side in [-1,1]:
  xx=x+side*2.05
  tube('Mining truck tyre',(xx-side*.42,yy,1.25),(xx+side*.42,yy,1.25),1.25,rubber,32)
  tube('Wheel rim',(xx+side*.43,yy,1.25),(xx+side*.46,yy,1.25),.62,steel,24)
  for i in range(10):
   a=i*math.tau/10
   tube('Wheel stud',(xx+side*.47,yy+.4*math.cos(a),1.25+.4*math.sin(a)),(xx+side*.50,yy+.4*math.cos(a),1.25+.4*math.sin(a)),.045,gold,8)
# Elevated dump body open at top, reinforced sides and floor.
cube('Dump bed floor',(x,3,3.1),(4.5,5,.25),gold,.08)
for side in [-1,1]:
 cube('Dump body side',(x+side*2.25,3,4),(.18,5.2,1.8),gold,.08)
 for yy in [1,2.2,3.4,4.6]:cube('Dump body stiffener',(x+side*2.4,yy,4),(.14,.14,1.8),steel)
cube('Dump tailgate',(x,5.6,4),(4.5,.18,1.8),gold)
cube('Dump front wall',(x,.5,4.2),(4.5,.18,2.2),gold)
cube('Cab frame',(x-1.35,-1.6,3.35),(1.5,1.8,2.0),gold,.10)
cube('Cab windshield',(x-1.35,-2.52,3.55),(1.3,.04,1.25),glass,.02)
cube('Cab side glazing',(x-2.12,-1.6,3.55),(.04,1.5,1.25),glass,.02)
cube('Cab roof',(x-1.35,-1.6,4.4),(1.8,2.1,.16),gold)
cube('Front bumper',(x,-3.1,1.55),(4.7,.32,.30),gold)
for xx in [x-1.8,x+1.8]:cube('Truck headlamp',(xx,-3.28,1.8),(.42,.05,.24),white)
cube('Exposed engine block',(x+.65,-1.7,2.4),(1.5,1.8,1.0),steel,.10)
for yy in [-2.2,-1.8,-1.4]:
 tube('Engine cylinder bank',(x+.05,yy,2.6),(x+1.2,yy,2.9),.17,black,16)
 tube('Engine pipe',(x+.2,yy,3),(x+1.2,yy,3),.06,rust)
hood=cube('Raised engine bonnet',(x+.65,-.7,3.55),(1.9,2.5,.15),gold,.05);hood.rotation_euler.x=math.radians(65)
for z in [.4,.8,1.2,1.6]:cube('Cab access step',(x-2.4,-1.8,z),(.5,.7,.10),steel)
for yy in [-3.8,6.2]:cube('Maintenance bay marking',(x,yy,.01),(6,.07,.025),gold,0)
label('PARKED / ENGINE SERVICE',(x,-4.0,.4),.27,gold)
# Perimeter workshops with recognisable machine and service silhouettes.
for x,y,title in [(-13,10,'ELECTRICAL SERVICES'),(-13,-9,'HYDRAULICS'),(11,-12,'MECHANICAL WORKSHOP')]:
 cube('Workshop backboard',(x,y+1,2.1),(8,.18,4.2),steel)
 label(title,(x,y+.88,3.5),.30,gold)
 cube('Worktop',(x,y,1.05),(7,1.0,.12),timber)
 for xx in [x-3,x+3]:cube('Bench support',(xx,y,.5),(.12,.8,1),steel)
 for xx in [x-2,x,x+2]:
  cube('Service cabinet',(xx,y+.75,2.25),(1.35,.35,1.25),wall)
  for z in [1.9,2.2,2.5]:cube('Panel controls',(xx,y+.54,z),(.85,.06,.08),black)
 for xx in [x-2.7,x+2.7]:
  tube('Workshop pipe riser',(xx,y+.6,.15),(xx,y+.6,3.1),.06,blue)
# Central seated area stays open and protected.
for x in [-3.3,3.3]:
 for y in [-7,-3]:tube('Central safety bollard',(x,y,0),(x,y,.75),.075,gold)
for x in [-3.5,3.5]:cube('Central viewing zone stripe',(x,-5,.015),(.06,5,.03),gold,0)

# Collapse static geometry by material to keep prototype rendering costs bounded.
bpy.ops.object.select_all(action='DESELECT')
groups={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':groups.setdefault(o.data.materials[0].name if o.data.materials else 'none',[]).append(o)
for name,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name=name
(out/'authoring').mkdir(exist_ok=True);(out/'authoring/.gdignore').write_text('')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'authoring/mining-prototype.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'mining-prototype.glb'),export_format='GLB',export_yup=True,export_apply=True)
report={'prototype':True,'people':0,'depth_metres':28,'triangles':sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons),'mesh_objects':len([o for o in bpy.context.scene.objects if o.type=='MESH']),'rock_material_source':'https://polyhaven.com/a/rock_boulder_dry','license':'CC0','not_integrated':True}
(out/'report.json').write_text(json.dumps(report,indent=2));print(report)
