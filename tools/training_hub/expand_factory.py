"""Direct Blender build on an existing checkpoint. Never overwrites the input.
Stages: blockout -> visually review -> detail. No network/generation required.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
source, target, stage=args[:3]
assert Path(source).resolve()!=Path(target).resolve()
bpy.ops.wm.open_mainfile(filepath=source)
scene=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=scene
for c in list(bpy.data.collections):
 if c.name.startswith('EXP_'):
  for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.collections.remove(c)
col=bpy.data.collections.new('EXP_Processing');scene.collection.children.link(col)
def mat(name,color,metal=.0,rough=.55):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
yellow=mat('EXP_SafetyYellow',(.72,.48,.018),.35)
steel=mat('EXP_Galvanized',(.32,.39,.42),.75,.4)
dark=mat('EXP_Graphite',(.035,.055,.06),.4)
teal=mat('EXP_MotorPaint',(.035,.16,.17),.45)
def link(o,name,material):
 o.name=name.replace(".", "p")
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.data.materials.append(material);return o
def box(name,pos,dims,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=link(bpy.context.object,name,m)
 # Mesh dimensions instead of unapplied nonuniform scale (bevels remain metric).
 for v in o.data.vertices:v.co.x*=dims[0];v.co.y*=dims[1];v.co.z*=dims[2]
 return o
def cyl(name,pos,r,depth,m,axis='Y',vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=pos)
 o=link(bpy.context.object,name,m);o.rotation_euler=(math.pi/2,0,0) if axis=='Y' else (0,0,0)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
for i,y in enumerate([3,11]):
 cyl(f'EXP_Screen_{i}_Envelope',(-12,y,2.6),1.6,5,dark)
 for yy in [y-2,y+2]:
  box(f'EXP_Screen_{i}_Plinth_{yy}',(-12,yy,.18),(3.9,1,.36),steel)
  for xx in [-13.3,-10.7]:box(f'EXP_Screen_{i}_Support_{xx}_{yy}',(xx,yy,.9),(.4,.6,1.5),yellow)
 box(f'EXP_Screen_{i}_Feed',(-12,y+3,3.25),(2.1,1.1,2),steel)
 box(f'EXP_Screen_{i}_Collection',(-12,y-3,.7),(3.4,1.2,1.4),dark)
box('EXP_WestGallery_Envelope',(-16.5,5.5,4.05),(1.5,21,.15),steel)
for y in [-4,1,6,11,16]:
 for x in [-17.15,-15.85]:box(f'EXP_Gallery_Leg_{x}_{y}',(x,y,2),(.14,.14,4),dark)
box('EXP_Compressor_Envelope',(14,11,1.2),(3.5,2.2,2.4),teal)
cyl('EXP_AirReceiver_Envelope',(17,11,1.8),.7,3.4,steel,axis='Z')
if stage == 'detail':
 def beam(name,a,b,width,m):
  a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,width,(b-a).length),m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
 def bevel(o,w=.025):
  mod=o.modifiers.new('Machined edge radii','BEVEL');mod.width=w;mod.segments=2
 def attach(o,parent):
  world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
 def ring(name,pos,r,width,m):
  # Annular closed band with an open centre, axial Y.
  verts=[];faces=[];n=48
  for yoff,rad in [(-width/2,r),(width/2,r),(-width/2,r-.075),(width/2,r-.075)]:
   verts.extend([(rad*math.cos(i*2*math.pi/n),yoff,rad*math.sin(i*2*math.pi/n)) for i in range(n)])
  for i in range(n):
   j=(i+1)%n
   faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.location=pos;me.materials.append(m);return o
 for i,y in enumerate([3,11]):
  prefix=f'EXP_Screen_{i}'
  bpy.data.objects.remove(bpy.data.objects[prefix+'_Envelope'],do_unlink=True)
  rig=bpy.data.objects.new(prefix+'_Rotor',None);col.objects.link(rig);rig.location=(-12,y,2.6);bpy.context.view_layer.update()
  # Perforated panels make the machine read as a screening drum, with open end throats.
  for k in range(32):
   theta=k*2*math.pi/32;half=.065;verts=[]
   for yy,rr in [(-2.5,1.3),(-2.3,1.6),(2.3,1.6),(2.5,1.3)]:
    for angle in [theta-half,theta+half]:verts.append((rr*math.cos(angle),yy,rr*math.sin(angle)))
   faces=[(j,j+1,j+3,j+2) for j in [0,2,4]]
   me=bpy.data.meshes.new(prefix+f'_Panel_{k}');me.from_pydata(verts,[],faces);me.materials.append(dark)
   o=bpy.data.objects.new(me.name,me);col.objects.link(o);o.parent=rig
   solid=o.modifiers.new('Screen panel thickness','SOLIDIFY');solid.thickness=.035
  for j,dy in enumerate([-2.3,-1.5,-.5,.5,1.5,2.3]):
   o=ring(prefix+f'_Hoop_{j}',(-12,y+dy,2.6),1.67,.13,yellow);bpy.context.view_layer.update();attach(o,rig)
  for frame,angle in [(1,0),(601,2*math.pi)]:
   rig.rotation_euler.y=angle;rig.keyframe_insert(data_path='rotation_euler',index=1,frame=frame)
  action=rig.animation_data.action
  for slot in action.slots:
   for layer in action.layers:
    for strip in layer.strips:
     bag=strip.channelbag(slot)
     if bag:
      for fc in bag.fcurves:
       for key in fc.keyframe_points:key.interpolation='LINEAR'
       fc.modifiers.new('CYCLES')
  # Fixed drive module and guarded roller supports, mechanically separate from rotating shell.
  for dy in [-2,2]:
   for xx in [-13.3,-10.7]:cyl(prefix+f'_SupportRoller_{xx}_{dy}',(xx,y+dy,1.48),.24,.65,steel)
  for xx in [-13.3,-10.7]:
   box(prefix+f'_LongitudinalFrame_{xx}',(xx,y,.68),(.22,5.8,.28),yellow)
  motor=cyl(prefix+'_DriveMotor',(-9.9,y-1.9,1.2),.38,1.05,teal);bevel(motor,.015)
  for j in range(7):cyl(prefix+f'_CoolingFin_{j}',(-9.9,y-2.3+j*.12,1.2),.405,.035,teal)
  box(prefix+'_DriveGuard',(-10.3,y-2,1.65),(.7,1.1,.4),yellow)
  for dy in [-3,3]:
   hood=bpy.data.objects.get(prefix+('_Feed' if dy>0 else '_Collection'));bevel(hood)
  box(prefix+'_ControlStand',(-9,y,.7),(.09,.09,1.4),steel)
  panel=box(prefix+'_ControlPanel',(-9,y,1.42),(.65,.25,.48),dark);bevel(panel,.02)
  for j,m in enumerate([teal,yellow]):cyl(prefix+f'_Pushbutton_{j}',(-9.15+j*.3,y-.15,1.42),.055,.04,m)
 # Gallery handrails, toeboards, intermediate landing and stairs join the existing rear platform.
 for x in [-17.2,-15.8]:
  for z in [4.67,5.2]:beam(f'EXP_Gallery_Rail_{x}_{z}',(x,-5,z),(x,16,z),.055,yellow)
  box(f'EXP_Gallery_Toeboard_{x}',(x,5.5,4.18),(.045,21,.17),yellow)
  for j in range(15):
   y=-5+j*1.5;beam(f'EXP_Gallery_Post_{x}_{j}',(x,y,4.1),(x,y,5.2),.055,yellow)
 for j in range(21):
  y=-10.6+j*.28;z=(j+1)*4.1/21
  box(f'EXP_Gallery_Stair_{j}',(-16.5,y,z-.04),(1.4,.3,.08),steel)
 for x in [-17.2,-15.8]:
  beam(f'EXP_Gallery_Stringer_{x}',(x,-10.9,.08),(x,-4.9,4.02),.16,dark)
  beam(f'EXP_Gallery_StairRail_{x}',(x,-10.9,1.1),(x,-4.9,5.2),.055,yellow)
  for j in [0,5,10,15,20]:
   y=-10.6+j*.28;z=(j+1)*4.1/21
   beam(f'EXP_Gallery_StairPost_{x}_{j}',(x,y,z),(x,y,z+1.1),.055,yellow)
 # Compressor casing details: recessed dark vent field, louvers, separation panels and receiver bands.
 o=bpy.data.objects['EXP_Compressor_Envelope'];bevel(o,.07)
 box('EXP_Compressor_VentRecess',(14,9.88,1.25),(2.7,.04,1.5),dark)
 for j in range(10):box(f'EXP_Compressor_Louver_{j}',(14,9.84,.64+j*.135),(2.5,.06,.045),steel)
 box('EXP_Compressor_Controls',(15.25,9.82,1.9),(.55,.06,.5),dark)
 for x in [12.6,15.4]:box(f'EXP_Compressor_Foot_{x}',(x,11,.1),(.3,2.4,.2),dark)
 for z in [.5,3.1]:cyl(f'EXP_Receiver_Collar_{z}',(17,11,z),.73,.12,dark,axis='Z')
 for x in [16.5,17.5]:box(f'EXP_Receiver_Foot_{x}',(x,11,.15),(.22,1,.3),dark)
 # Pipe joins compressor to receiver, then along wall to existing utility riser region.
 for j,(a,b) in enumerate([((15.7,11,2),(17,11,2)),((17,11,3.5),(17,11,5.6)),((17,11,5.6),(17,16.8,5.6)),((17,16.8,5.6),(10.2,16.8,5.6))]):beam(f'EXP_AirHeader_{j}',a,b,.095,steel)
 for y in [1,4,7]:
  box(f'EXP_Bench_Top_{y}',(18.6,y,1),(1.6,2.2,.12),steel)
  for xx in [18,19.2]:
   for yy in [y-.9,y+.9]:box(f'EXP_Bench_Leg_{xx}_{yy}',(xx,yy,.48),(.07,.07,.96),dark)
  for j in range(4):box(f'EXP_Bench_Drawer_{y}_{j}',(18.1,y,.22+j*.18),(.55,1.7,.16),teal)
  cyl(f'EXP_Bench_SpareBearing_{y}',(18.7,y,1.24),.3,.35,dark,axis='Z')
 scene.frame_end=max(scene.frame_end,601);scene.frame_set(1)

cam=bpy.data.objects.get('CAM_expansion_review')
if not cam:
 d=bpy.data.cameras.new('CAM_expansion_review');cam=bpy.data.objects.new('CAM_expansion_review',d);scene.collection.objects.link(cam)
cam.location=(0,0,1.65);cam.rotation_euler=(Vector((-12,9,2.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22
# Useful inspectable checkpoint; restore production camera before copy-save.
scene.camera=bpy.data.objects.get('CAM_main') or scene.camera
Path(target).parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
scene.camera=cam
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.filepath=str(Path(target).with_suffix('.png'))
bpy.ops.render.render(write_still=True)
print('EXPANSION_BLOCKOUT',json.dumps({'objects':len(col.objects),'checkpoint':target,'render':scene.render.filepath}))
