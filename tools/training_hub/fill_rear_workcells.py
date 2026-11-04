"""Fill the inner rear floor with substantial mining maintenance workcells.
All new objects stay in FIT_Rear_Workcells; earlier checkpoints are preserved.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
source,target,stage=sys.argv[sys.argv.index('--')+1:];assert not Path(target).exists();assert source!=target
bpy.ops.wm.open_mainfile(filepath=source);s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s;s.frame_set(1)
c=bpy.data.collections.new('FIT_Rear_Workcells');s.collection.children.link(c)
def plain(name,color,metal=.4):
 m=bpy.data.materials.get(name)
 if m:return m
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.5;return m
steel=plain('EXP_Galvanized',(.32,.39,.42),.75);dark=plain('EXP_Graphite',(.035,.055,.06));yellow=plain('EXP_SafetyYellow',(.72,.48,.018));teal=plain('EXP_MotorPaint',(.035,.16,.17));white=plain('FIT_OffWhite',(.65,.7,.69),.15)

def move(o,name,m):
 o.name=name
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m);return o
def box(name,p,size,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=move(bpy.context.object,name,m)
 for v in o.data.vertices:v.co.x*=size[0];v.co.y*=size[1];v.co.z*=size[2]
 if bevel:a=o.modifiers.new('Folded/machined corners','BEVEL');a.width=bevel;a.segments=2
 return o
def pipe(name,a,b,r,m,n=24):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2);o=move(bpy.context.object,name,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def beam(name,a,b,w,m):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,w,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
# These footprints intentionally move equipment inward from the wall, without blocking the door lane.
box('FIT_Rear_CylinderBench_Base',(4.8,12.8,.15),(3,5.4,.3),dark)
box('FIT_Rear_ComponentStand_Base',(-4.8,11,.15),(3.1,4.8,.3),dark)
box('FIT_Rear_LinerStorage_Base',(-5,18.3,.2),(3,2.5,.4),steel)
box('FIT_Rear_HydraulicPlant_Base',(7,18,.15),(3,2.4,.3),dark)
box('FIT_Rear_ControlDesk',(-4.8,6.7,.7),(2.6,1.2,1.4),teal,.04)
# Rear service bridge adds an upper layer; its underside is above the existing door clearance.
box('FIT_Rear_ServiceBridge_Deck',(0,17.2,6.02),(34.4,1.2,.16),steel)
for j,x in enumerate([-16.6,-9,9,16.6]):
 box(f'FIT_Rear_ServiceBridge_Leg_{j}',(x,17.2,2.9),(.18,.18,5.8),dark)
 box(f'FIT_Rear_ServiceBridge_Foot_{j}',(x,17.2,.07),(.5,.5,.14),steel)
 box(f'FIT_Rear_ServiceBridge_Crosshead_{j}',(x,17.2,5.85),(.22,1.5,.2),dark)
for j,y in enumerate([16.7,17.7]):
 for k,z in enumerate([5.53,5.93]):box(f'FIT_Rear_BridgeFlange_{j}_{k}',(0,y,z),(34.4,.18,.045),dark)
 box(f'FIT_Rear_BridgeWeb_{j}',(0,y,5.73),(34.4,.04,.35),dark)
if stage=='blockout':
 pipe('FIT_Rear_WheelEnvelope',(-4.8,10.4,1.95),(-4.8,11.6,1.95),1.35,dark)
 pipe('FIT_Rear_CylinderEnvelope',(4.8,12.3,1.65),(4.8,14.9,1.65),.4,teal)
 box('FIT_Rear_FilterPlantEnvelope',(7,18,1.9),(2.5,1.9,3.2),teal)
else:
 # Bridge rail/toeboard gap aligns with the west stair, so its landing is actually usable.
 for y,start in [(16.6,-15.8),(17.8,-17.2)]:
  for z in [6.65,7.2]:pipe(f'FIT_Rear_BridgeRail_{y}_{z}'.replace('.','p'),(start,y,z),(17.2,y,z),.03,yellow)
  box(f'FIT_Rear_BridgeToe_{y}'.replace('.','p'),((start+17.2)/2,y,6.2),(17.2-start,.035,.18),yellow)
  for j in range(24):
   x=-17.2+j*1.49
   if x<start:continue
   pipe(f'FIT_Rear_BridgePost_{y}_{j}'.replace('.','p'),(x,y,6.1),(x,y,7.2),.03,yellow)
 for j in range(10):
  y=14.35+j*.28;z=4.1+(j+1)*.2
  box(f'FIT_Rear_BridgeStair_{j}',(-16.5,y,z-.04),(1.1,.3,.08),steel)
 for x in [-17.1,-15.9]:
  beam(f'FIT_Rear_BridgeStringer_{x}'.replace('.','p'),(x,14.1,4.1),(x,17.05,6.02),.12,dark)
  pipe(f'FIT_Rear_BridgeStairRail_{x}'.replace('.','p'),(x,14.1,5.2),(x,17.05,7.2),.03,yellow)
  for j in [0,3,6,9]:
   y=14.35+j*.28;z=4.1+(j+1)*.2
   pipe(f'FIT_Rear_BridgeStairPost_{x}_{j}'.replace('.','p'),(x,y,z),(x,y,z+1.1),.03,yellow)
 # Heavy wheel/shaft components on braced retaining stands.
 for y in [9.4,12.6]:
  for x in [-5.9,-3.7]:
   box(f'FIT_Rear_WheelFoot_{x}_{y}'.replace('.','p'),(x,y,.4),(.65,.7,.25),steel)
   beam(f'FIT_Rear_WheelAFrame_{x}_{y}'.replace('.','p'),(x,y,.52),(-4.8,y,1.95),.16,yellow)
 pipe('FIT_Rear_ComponentAxle',(-4.8,9.1,1.95),(-4.8,12.9,1.95),.21,steel)
 for j,y in enumerate([10,11.5]):
  # Lathed tyre/rim profile has an open centre and raised sidewalls, rather than a solid cylinder.
  verts=[];faces=[];n=48
  profile=[(-.4,.45),(-.4,1.15),(-.32,1.35),(.32,1.35),(.4,1.15),(.4,.45)]
  for yy,r in profile:verts.extend([(-4.8+r*math.cos(i*math.tau/n),y+yy,1.95+r*math.sin(i*math.tau/n)) for i in range(n)])
  for k in range(len(profile)):
   nxt=(k+1)%len(profile)
   for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,nxt*n+(i+1)%n,nxt*n+i))
  me=bpy.data.meshes.new(f'FIT_Rear_HeavyWheel_{j}');me.from_pydata(verts,[],faces);me.materials.append(dark);o=bpy.data.objects.new(me.name,me);c.objects.link(o)
  pipe(f'FIT_Rear_WheelHub_{j}',(-4.8,y-.42,1.95),(-4.8,y+.42,1.95),.48,steel,32)
  for k in range(8):
   a=k*math.tau/8;xx=-4.8+.31*math.cos(a);zz=1.95+.31*math.sin(a);pipe(f'FIT_Rear_HubBolt_{j}_{k}',(xx,y-.48,zz),(xx,y-.4,zz),.055,yellow,6)
  for k in range(24):
   a=k*math.tau/24;o=box(f'FIT_Rear_Tread_{j}_{k}',(-4.8+1.36*math.cos(a),y,1.95+1.36*math.sin(a)),(.13,.65,.07),dark);o.rotation_euler.y=-a
 # Hydraulic cylinder bench: barrel remains fixed; only the guided rod and end clevis move.
 for x in [3.65,5.95]:
  box(f'FIT_Rear_BenchRail_{x}'.replace('.','p'),(x,12.8,1.1),(.16,5,.25),yellow)
  for y in [10.5,12.8,15.1]:box(f'FIT_Rear_BenchLeg_{x}_{y}'.replace('.','p'),(x,y,.66),(.18,.25,.72),steel)
 for j,y in enumerate([12.6,14.5]):
  box(f'FIT_Rear_Saddle_{j}',(4.8,y,1.15),(1.2,.4,.35),dark)
 pipe('FIT_Rear_HydraulicBarrel',(4.8,12.3,1.65),(4.8,14.9,1.65),.4,teal,40)
 for j,y in enumerate([12.3,14.9]):pipe(f'FIT_Rear_CylinderCap_{j}',(4.8,y-.08,1.65),(4.8,y+.08,1.65),.47,steel,32)
 rig=bpy.data.objects.new('FIT_Rear_RamMotion',None);c.objects.link(rig);rig.location=(4.8,12.3,1.65);bpy.context.view_layer.update()
 for o in [pipe('FIT_Rear_PistonRod',(4.8,11.2,1.65),(4.8,13.2,1.65),.13,steel,32),box('FIT_Rear_RodClevis',(4.8,11.1,1.65),(.5,.35,.4),teal,.04)]:
  bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=rig;o.matrix_world=w
 for f,y in [(1,12.3),(61,12.3),(181,11.75),(241,11.75),(361,12.3)]:rig.location.y=y;rig.keyframe_insert(data_path='location',index=1,frame=f)
 for slot in rig.animation_data.action.slots:
  for layer in rig.animation_data.action.layers:
   for strip in layer.strips:
    bag=strip.channelbag(slot)
    if bag:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='BEZIER'
      fc.modifiers.new('CYCLES')
 for x in [3.7,5.9]:
  for z in [1.25,2.3]:pipe(f'FIT_Rear_RamGuardRail_{x}_{z}'.replace('.','p'),(x,10.25,z),(x,12.15,z),.025,yellow)
  for j in range(9):pipe(f'FIT_Rear_RamGuard_{x}_{j}'.replace('.','p'),(x,10.3+j*.23,1.25),(x,10.3+j*.23,2.3),.014,steel,8)
 # Powerpack, twin filters, gauges and connected rear header.
 box('FIT_Rear_HydraulicReservoir',(7,18,.95),(2.5,1.9,1.6),teal,.06)
 for j,x in enumerate([6.35,7.65]):
  pipe(f'FIT_Rear_Filter_{j}',(x,18,1.7),(x,18,3.5),.27,steel,32)
  pipe(f'FIT_Rear_FilterCap_{j}',(x,18,3.45),(x,18,3.6),.31,dark,24)
  pipe(f'FIT_Rear_FilterGaugeStem_{j}',(x,17.72,2.8),(x,17.5,2.8),.035,steel)
  pipe(f'FIT_Rear_FilterGauge_{j}',(x,17.5,2.8),(x,17.44,2.8),.14,white,24)
 pipe('FIT_Rear_PowerPackHeader',(7,18,3.6),(7,18,5.6),.09,steel)
 pipe('FIT_Rear_PowerPackHeaderReturn',(7,18,5.6),(7,20.8,5.6),.09,steel)
 for y in [13,14.6]:
  pipe(f'FIT_Rear_CylinderHose_{y}'.replace('.','p'),(5.15,y,1.65),(6.3,y,1.65),.04,dark)
  pipe(f'FIT_Rear_CylinderHoseDrop_{y}'.replace('.','p'),(6.3,y,1.65),(6.3,y,.55),.04,dark)
  pipe(f'FIT_Rear_CylinderHoseRun_{y}'.replace('.','p'),(6.3,y,.55),(6.3,17.1,.55),.04,dark)
 # Stepped stacks of heavy liners and rack dividers populate the rear laydown bay.
 for j in range(4):
  for k in range(5):
   box(f'FIT_Rear_Liner_{j}_{k}',(-5.95+j*.63,18.3,.55+k*.23),(.5,1.85,.18),dark,.035)
 for x in [-6.45,-3.55]:
  for y in [17.15,19.45]:box(f'FIT_Rear_StoragePost_{x}_{y}'.replace('.','p'),(x,y,1.1),(.08,.08,1.8),yellow)
 # SCADA/service desk: angled console, three screens and floor cable drop.
 box('FIT_Rear_DeskWorktop',(-4.8,6.7,1.45),(2.8,1.35,.12),steel,.025)
 for i,x in enumerate([-5.65,-4.8,-3.95]):
  box(f'FIT_Rear_ScreenStand_{i}',(x,7,1.72),(.07,.07,.5),dark)
  box(f'FIT_Rear_ScadaScreen_{i}',(x,6.95,2.02),(.78,.08,.5),dark,.025)
  box(f'FIT_Rear_ScadaDisplay_{i}',(x,6.899,2.02),(.68,.012,.39),teal)
  for k in range(3):box(f'FIT_Rear_DisplayBar_{i}_{k}',(x-.22+k*.2,6.89,1.96+k*.045),(.08,.006,.14+k*.03),yellow)
 pipe('FIT_Rear_DeskCable',(-5.8,7,1.2),(-5.8,7,.12),.05,dark)

s.camera=s.objects['CAM_main'];s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.eevee.shadow_pool_size='1024';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
cam=s.objects['CAM_expansion_review'];cam.location=(0,0,1.65);cam.data.lens=18;cam.rotation_euler=(Vector((0,15,2))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.filepath=str(Path(target).with_suffix('.png'));bpy.ops.render.render(write_still=True)
print('REAR_INFILL',stage,len(c.objects),target)
