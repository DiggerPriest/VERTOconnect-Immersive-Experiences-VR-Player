"""Populate the remaining bays, retaining the reviewed source and all prior assets.
Run in a separate Blender process: source.blend output.blend blockout|detail.
"""
import bpy, math, sys, json
from mathutils import Vector
from pathlib import Path
source,target,stage=sys.argv[sys.argv.index('--')+1:]
assert Path(source).resolve()!=Path(target).resolve()
assert not Path(target).exists(), 'Use a fresh checkpoint path'
bpy.ops.wm.open_mainfile(filepath=source)
s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s
assert not bpy.data.collections.get('FIT_ServicePlant'), 'Already populated; choose the original input'
c=bpy.data.collections.new('FIT_ServicePlant');s.collection.children.link(c)
created=[]
def material(name,color,metal=.4,rough=.55,emission=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
steel=material('EXP_Galvanized',(.32,.39,.42),.75,.4)
dark=material('EXP_Graphite',(.035,.055,.06))
yellow=material('EXP_SafetyYellow',(.72,.48,.018))
teal=material('EXP_MotorPaint',(.035,.16,.17))
white=material('FIT_OffWhite',(.65,.7,.69),.15,.6)
red=material('FIT_IsolationRed',(.42,.025,.015),.1)
green=material('FIT_RunGreen',(.02,.5,.1),.1,emission=1.5)
lightmat=material('FIT_TaskLight',(.7,.82,1),0,emission=2)
coal=material('FIT_Coal',(.018,.021,.025),.1,.82)
def add(o,name,m):
 o.name=name.replace('.','p');created.append(o.name)
 for coll in list(o.users_collection):coll.objects.unlink(o)
 c.objects.link(o)
 if m:o.data.materials.append(m)
 return o
def box(name,pos,size,m,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=add(bpy.context.object,name,m)
 for v in o.data.vertices:v.co.x*=size[0];v.co.y*=size[1];v.co.z*=size[2]
 if bev:mod=o.modifiers.new('Folded edge','BEVEL');mod.width=bev;mod.segments=2
 return o
def pipe(name,a,b,r,m,n=16):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=(b-a).length,location=(a+b)/2);o=add(bpy.context.object,name,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def beam(name,a,b,w,m):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,w,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def skin(name,rings,m,n=32):
 # Closed body of revolution, Z axis, rounded/chamfered ends from explicit profile.
 verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z,r in rings for i in range(n)]
 faces=[]
 for row in range(len(rings)-1):
  for i in range(n):faces.append((row*n+i,row*n+(i+1)%n,(row+1)*n+(i+1)%n,(row+1)*n+i))
 faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);c.objects.link(o);created.append(o.name);me.materials.append(m)
 for p in me.polygons:p.use_smooth=len(p.vertices)==4
 return o
def funnel(name,centre,top,bottom,zs,m):
 verts=[]
 for dims,z in [(bottom,zs[0]),(top,zs[1])]:
  for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:verts.append((centre[0]+x*dims[0]/2,centre[1]+y*dims[1]/2,z))
 faces=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(m);o=bpy.data.objects.new(name,me);c.objects.link(o);created.append(o.name)
 mod=o.modifiers.new('Plate thickness','SOLIDIFY');mod.thickness=.04;return o
def rig(name,location):
 o=bpy.data.objects.new(name,None);c.objects.link(o);o.location=location;created.append(o.name);bpy.context.view_layer.update();return o
def parent(o,r):
 bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=r;o.matrix_world=w

def animate(o,path,index,keys,linear=False):
 for frame,value in keys:
  getattr(o,path)[index]=value;o.keyframe_insert(data_path=path,index=index,frame=frame)
 action=o.animation_data.action
 for slot in action.slots:
  for layer in action.layers:
   for strip in layer.strips:
    bag=strip.channelbag(slot)
    if bag:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR' if linear else 'BEZIER'
      if not fc.modifiers:fc.modifiers.new('CYCLES')

# Footprints kept entirely in side bays, outside the central route and door approaches.
box('FIT_PumpSkid_Base',(8.2,5.5,.16),(3.8,4.5,.32),dark)
for x in [12.2,15]:
 o=skin('FIT_ProcessTank_'+str(x),[(0,.9),(.2,1.1),(.45,1.18),(3.5,1.18),(3.8,1.05),(4,.6),(4.05,.2)],white)
 o.location=(x,5,0)
box('FIT_EastGallery_Deck',(16.6,6.8,4.05),(1.2,9,.14),steel)
for y in [2.3,6.8,11.3]:
 for x in [16.05,17.15]:box(f'FIT_GalleryLeg_{x}_{y}',(x,y,2),(.13,.13,4),dark)
for j in range(5):box(f'FIT_MCC_Cabinet_{j}',(19,13.8+j*1.35,1.35),(1.4,1.2,2.7),white,.035)
box('FIT_TestBench_Base',(-8.2,-5.2,.6),(3.5,2.1,1.2),dark,.04)

if stage=='detail':
 # Twin-duty pump motors, volutes, couplings and isolation valves.
 for i,y in enumerate([4.1,6.9]):
  name=f'FIT_Pump_{i}'
  for x in [7.1,9.3]:box(name+f'_Mount_{x}',(x,y,.48),(.6,1,.3),steel,.015)
  motor=skin(name+'_Motor',[(0,.34),(.1,.44),(.85,.44),(1.0,.33)],teal)
  motor.location=(7,y,1);motor.rotation_euler=(0,math.pi/2,0)
  for j in range(8):pipe(name+f'_MotorFin_{j}',(7.15+j*.09,y,1),(7.18+j*.09,y,1),.47,teal,24)
  pipe(name+'_Coupling',(7.95,y,1),(8.65,y,1),.13,steel)
  pipe(name+'_Volute',(8.7,y-.27,1),(8.7,y+.27,1),.62,teal,40)
  pipe(name+'_Suction',(8.7,y,1),(10.3,y,1),.19,steel)
  pipe(name+'_Discharge',(8.7,y,1.5),(8.7,y,2.4),.15,steel)
  pipe(name+'_Riser',(8.7,y,2.4),(12.2,y,2.4),.15,steel)
  pipe(name+'_TankBranch',(12.2,y,2.4),(12.2,5,2.4),.15,steel)
  for x in [9.2,10]:pipe(name+f'_Flange_{x}',(x-.045,y,1),(x+.045,y,1),.27,dark,24)
  pipe(name+'_ValveStem',(9.6,y,1),(9.6,y,1.62),.04,steel)
  wheel=skin(name+'_ValveWheel',[(0,.21),(.04,.21)],red,16);wheel.location=(9.6,y,1.62)
  # Guarded coupling has a visible shaft behind a static mesh cage.
  spin=rig(name+'_ShaftMotion',(8.3,y,1))
  collar=pipe(name+'_CouplingStripe',(8.25,y,1),(8.35,y,1),.17,yellow);parent(collar,spin)
  for a in [0,math.pi/2]:
   fin=box(name+f'_ShaftKey_{a}',(8.3,y+.12*math.cos(a),1+.12*math.sin(a)),(.12,.1,.1),dark);parent(fin,spin)
  animate(spin,'rotation_euler',0,[(1,0),(181,2*math.pi)],True)
  for x in [8.02,8.2,8.38,8.56]:
   for z in [.86,1.16]:beam(name+f'_GuardBar_{x}_{z}',(x,y-.25,z),(x,y+.25,z),.022,yellow)
  for yy in [y-.26,y+.26]:box(name+f'_GuardSide_{yy}',(8.3,yy,1),(.7,.025,.5),yellow)
 # Tank flanges, access covers, stiffening bands, level gauges and common service header.
 for i,x in enumerate([12.2,15]):
  for z in [.5,3.45]:
   pipe(f'FIT_Tank_{i}_Band_{z}',(x,5,z-.045),(x,5,z+.045),1.21,steel,40)
  pipe(f'FIT_Tank_{i}_Manway',(x,5,4.02),(x,5,4.18),.38,dark,24)
  pipe(f'FIT_Tank_{i}_Level',(x-1.18,4.6,.6),(x-1.18,4.6,3.2),.06,yellow)
  pipe(f'FIT_Tank_{i}_Out',(x,5,.7),(x,7,.7),.16,steel)
  pipe(f'FIT_Tank_{i}_Return',(x,5,3.65),(x,7,3.65),.12,steel)
  pipe(f'FIT_Tank_{i}_ReturnRiser',(x,7,3.65),(x,7,5.5),.12,steel)
 pipe('FIT_ProcessReturnHeader',(12.2,7,5.5),(15,7,5.5),.12,steel)
 pipe('FIT_ProcessReturnToPlant',(15,7,5.5),(15,16.8,5.5),.12,steel)
 pipe('FIT_ProcessReturnEnd',(15,16.8,5.5),(10.2,16.8,5.5),.12,steel)
 # Gallery rails and stairs approach from the front, clear of the conveyor exit route.
 for x in [16.02,17.18]:
  for z in [4.65,5.2]:pipe(f'FIT_GalleryRail_{x}_{z}',(x,2.3,z),(x,11.3,z),.03,yellow)
  box(f'FIT_GalleryToe_{x}',(x,6.8,4.18),(.035,9,.18),yellow)
  for j in range(7):pipe(f'FIT_GalleryPost_{x}_{j}',(x,2.3+j*1.5,4.1),(x,2.3+j*1.5,5.2),.03,yellow)
 for j in range(21):
  y=-3.3+j*.28;z=(j+1)*4.1/21
  box(f'FIT_StairTread_{j}',(16.6,y,z-.04),(1.12,.3,.08),steel)
 for x in [16.02,17.18]:
  beam(f'FIT_Stringer_{x}',(x,-3.55,.05),(x,2.4,4.03),.13,dark)
  pipe(f'FIT_StairRail_{x}',(x,-3.55,1.1),(x,2.4,5.2),.03,yellow)
  for j in [0,5,10,15,20]:
   y=-3.3+j*.28;z=(j+1)*4.1/21;pipe(f'FIT_StairPost_{x}_{j}',(x,y,z),(x,y,z+1.1),.03,yellow)
 # MCC hinged faces, louvers, isolation handles and trays feed into the existing utility route.
 for j in range(5):
  y=13.8+j*1.35
  box(f'FIT_MCC_Door_{j}',(18.275,y,1.5),(.045,1.05,2.25),steel,.015)
  box(f'FIT_MCC_HMI_{j}',(18.24,y,2.1),(.035,.55,.3),dark,.008)
  box(f'FIT_MCC_Run_{j}',(18.21,y-.12,2.1),(.025,.12,.09),green)
  box(f'FIT_MCC_Isolator_{j}',(18.2,y+.35,1.5),(.09,.12,.3),red)
  for k in range(5):box(f'FIT_MCC_Louver_{j}_{k}',(18.235,y,.55+k*.09),(.02,.7,.025),dark)
  pipe(f'FIT_MCC_Conduit_{j}',(19,y,2.7),(19,y,6.4),.045,dark)
 for x in [18.55,19.4]:beam(f'FIT_CableTrayRail_{x}',(x,-17,6.4),(x,20,6.4),.065,steel)
 for j in range(75):
  y=-17+j*.5;box(f'FIT_CableTrayRung_{j}',(18.975,y,6.4),(.9,.045,.045),steel)
 for x in [18.7,18.9,19.1,19.25]:pipe(f'FIT_CableTrayCable_{x}',(x,-17,6.48),(x,20,6.48),.025,dark,8)
 for j in range(8):beam(f'FIT_CableTrayBracket_{j}',(20,-16+j*5,6.15),(18.5,-16+j*5,6.15),.07,dark)
 # Motor rebuild/test bench with a shaft behind an enclosure, not an exposed spinner.
 box('FIT_TestBench_Top',(-8.2,-5.2,1.28),(3.7,2.2,.16),steel,.025)
 body=skin('FIT_TestMotor',[(0,.44),(.1,.54),(1.35,.54),(1.5,.44)],teal)
 body.location=(-9.4,-5.2,1.95);body.rotation_euler=(0,math.pi/2,0)
 for x in [-9.1,-8.8,-8.5,-8.2]:
  pipe(f'FIT_TestMotorFin_{x}',(x,-5.2,1.95),(x+.04,-5.2,1.95),.57,teal,32)
 r=rig('FIT_TestBench_Rotor',(-7.45,-5.2,1.95))
 for k in range(6):
  a=k*math.tau/6;o=box(f'FIT_TestBench_Blade_{k}',(-7.45,-5.2+.29*math.cos(a),1.95+.29*math.sin(a)),(.04,.35,.09),steel);o.rotation_euler.x=a;parent(o,r)
 animate(r,'rotation_euler',0,[(1,0),(241,math.tau)],True)
 pipe('FIT_TestBench_Shaft',(-8,-5.2,1.95),(-7.45,-5.2,1.95),.12,steel)
 for x in [-7.6,-7.3]:
  for k in range(12):
   a=k*math.tau/12;b=(k+1)*math.tau/12;pipe(f'FIT_TestBench_Guard_{x}_{k}',(x,-5.2+.5*math.cos(a),1.95+.5*math.sin(a)),(x,-5.2+.5*math.cos(b),1.95+.5*math.sin(b)),.02,yellow,8)
 for k in range(12):
  a=k*math.tau/12;pipe(f'FIT_TestBench_GuardBar_{k}',(-7.6,-5.2+.5*math.cos(a),1.95+.5*math.sin(a)),(-7.3,-5.2+.5*math.cos(a),1.95+.5*math.sin(a)),.015,steel,8)
 box('FIT_TestBench_Controls',(-6.9,-6.15,1.6),(.6,.25,.5),dark,.02)
 # Screening unders hoppers now sit directly beneath the mesh, with enclosed outlets.
 for i,y in enumerate([3,11]):
  funnel(f'FIT_Screen_{i}_Unders',(-12,y),(3.5,5),(1.1,2.1),(.25,1.05),dark)
  pipe(f'FIT_Screen_{i}_Discharge',(-12,y,.25),(-12,y-.8,.25),.3,steel,24)
  # Smaller cross bands give a screening grid, rather than the previous empty cage silhouette.
  rotor=bpy.data.objects[f'EXP_Screen_{i}_Rotor']
  for k in range(1,20):
   yy=-2.3+k*.23
   # Radial profile mesh uses Z axis, rotate to Y and inherit the drum rig.
   band=skin(f'FIT_Screen_{i}_MeshHoop_{k}',[(0,1.605),(.025,1.605)],dark,32)
   # Remove cap polygons; ring is an open screen support, never a full opaque plate.
   import bmesh
   bm=bmesh.new();bm.from_mesh(band.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES');bm.to_mesh(band.data);bm.free()
   band.rotation_euler=(math.pi/2,0,0);band.location=(-12,y+yy,2.6);parent(band,rotor)
  # Existing feed box becomes an open-topped hopper feeding the upper end throat.
  old=bpy.data.objects[f'EXP_Screen_{i}_Feed'];old.hide_render=True;old.hide_set(True)
  funnel(f'FIT_Screen_{i}_FeedHopper',(-12,y+2.8),(2.25,1.5),(.85,.6),(2.9,4.25),steel)
  box(f'FIT_Screen_{i}_FeedChute',(-12,y+2.45,2.85),(.9,.8,.18),dark)
 import importlib.util
 spec=importlib.util.spec_from_file_location('fit_crane_runway',Path(__file__).with_name('fit_crane_runway.py'));crane_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(crane_module);crane_module.fit_crane(s)
 # Empty crane runs slowly in a bounded part of the hall, with all ropes and hook following the trolley.
 crane=bpy.data.collections['WKS_Overhead_Crane']
 moving=[o for o in crane.objects if not o.name.startswith('CRANE_runway')]
 bridge=rig('FIT_CraneBridgeMotion',(0,9.45,8.1));trolley=rig('FIT_CraneTrolleyMotion',(-3,9.45,8.53));parent(trolley,bridge)
 trolley_names=('CRANE_trolley','CRANE_hoist_motor','CRANE_wire_rope','CRANE_hook')
 for o in moving:parent(o,trolley if o.name.startswith(trolley_names) else bridge)
 animate(bridge,'location',1,[(1,9.45),(151,9.45),(601,7.2),(751,7.2),(1201,9.45)])
 # Local trolley X is -3 because the bridge origin is at world X0; preserve other axes.
 animate(trolley,'location',0,[(1,-3),(151,-3),(601,-6),(751,-6),(1201,-3)])
 # Emissive task strips: local practical read without adding any dynamic lights.
 for x,y in [(16.6,3),(16.6,8),(-16.5,1),(-16.5,9)]:
  box(f'FIT_TaskHousing_{x}_{y}',(x,y,3.9),(.4,1.5,.1),dark)
  box(f'FIT_TaskLens_{x}_{y}',(x,y,3.84),(.3,1.35,.025),lightmat)

# Measured column clearances: original column foot at (9.5,2.75)
# and wall feet near x20 require these offsets, without moving architecture.
for obj in c.objects:
 if obj.name.startswith('FIT_MCC_') and not obj.parent:obj.location.x-=.6
for obj in s.objects:
 if obj.name.startswith(('EXP_Screen_0_Control', 'EXP_Screen_0_Pushbutton')):
  obj.location.x+=.5
if stage=='detail':
 for j in range(5):
  y=13.8+j*1.35;pipe(f'FIT_MCC_TrayLink_{j}',(18.4,y,6.4),(19,y,6.4),.045,dark)

s.frame_end=1201 if stage=='detail' else s.frame_end;s.frame_set(1)
# Restore the existing portal-facing production camera in the saved scene.
s.camera=bpy.data.objects['CAM_main']
Path(target).parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
# Review cameras are temporary for this process, never override the saved main camera.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
# Source has >30 shadowed lights: use a larger atlas for offline review; game uses its own light policy.
if hasattr(s.eevee,'shadow_pool_size'):s.eevee.shadow_pool_size='1024'
for label,look in [('rear_west',(-12,8,2.3)),('rear_east',(13,7,2.3)),('front',(0,-22,2.0))]:
 cam=s.objects['CAM_expansion_review'];cam.location=(0,0,1.65);cam.rotation_euler=(Vector(look)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20;s.camera=cam
 s.render.filepath=str(Path(target).with_name(Path(target).stem+'_'+label+'.png'));bpy.ops.render.render(write_still=True)
report={'objects_added':len(created),'names':created,'stage':stage,'checkpoint':target};Path(target).with_suffix('.json').write_text(json.dumps(report,indent=2));print('BAYS_BUILD',json.dumps({'stage':stage,'count':len(created),'checkpoint':target}))
