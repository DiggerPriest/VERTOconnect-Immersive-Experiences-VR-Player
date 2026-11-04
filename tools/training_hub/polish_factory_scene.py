"""Final editable labelling and restrained in-drum material motion; new copy only."""
import bpy,sys,math,random,json
from pathlib import Path
source,target=sys.argv[sys.argv.index('--')+1:];assert not Path(target).exists();assert source!=target
bpy.ops.wm.open_mainfile(filepath=source);s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s
c=bpy.data.collections.new('FIT_Labelling_MaterialMotion');s.collection.children.link(c)
white=bpy.data.materials['FIT_OffWhite'];dark=bpy.data.materials['EXP_Graphite'];coal=bpy.data.materials.get('FIT_Coal') or bpy.data.materials.new('FIT_Coal');coal.diffuse_color=(.018,.021,.025,1);coal.use_nodes=True;cp=coal.node_tree.nodes.get('Principled BSDF');cp.inputs['Base Color'].default_value=coal.diffuse_color;cp.inputs['Roughness'].default_value=.82
def text(name,body,loc,rotation,size=.14):
 font=bpy.data.curves.new(name,'FONT');font.body=body;font.size=size;font.align_x='CENTER';font.extrude=.001;font.resolution_u=3
 o=bpy.data.objects.new(name,font);c.objects.link(o);font.materials.append(white);o.location=loc;o.rotation_euler=rotation;return o
for i,y in enumerate([3,11]):text(f'FIT_Tag_Screen_{i}',f'SCREEN 0{i+1}',(-8.5 if i==0 else -9,y-.13,1.52),(math.pi/2,0,0),.1)
for j in range(5):text(f'FIT_Tag_MCC_{j}',f'MCC 0{j+1}',(17.655,13.8+j*1.35,2.5),(math.pi/2,0,-math.pi/2),.11)
text('FIT_Tag_TestBench','MOTOR TEST BAY',(-8.2,-6.27,1.0),(math.pi/2,0,0),.17)
text('FIT_Tag_PumpSkid','DUTY / STANDBY', (8.2,3.235,.18),(math.pi/2,0,0),.14)
# Individual tumbling lumps remain inside the screening cylinder at every frame.
# Staggered phases describe lifting and falling while the drum continues rotating.
rng=random.Random(418)
path=[(-.3,-1.20),(-1.0,-.65),(-1.0,.45),(-.4,.2),(.35,-.65),(-.3,-1.20)]
times=[0,.25,.5,.65,.8,1]
report={'rocks':[],'lighting_before':{'engine':s.render.engine,'shadow_pool':s.eevee.shadow_pool_size,'samples':s.eevee.taa_render_samples}}
for drum,y in enumerate([3,11]):
 for i in range(12):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1)
  o=bpy.context.object;o.name=f'FIT_DrumOre_{drum}_{i:02d}'
  for old in list(o.users_collection):old.objects.unlink(o)
  c.objects.link(o);o.data.materials.append(coal)
  for v in o.data.vertices:v.co*=rng.uniform(.09,.15)
  depth=-2.0+(i%6)*.75;phase=rng.random();maximum=0
  for f in range(1,242,10):
   t=((f-1)/240+phase)%1
   k=next(k for k in range(5) if times[k]<=t<times[k+1]);a=(t-times[k])/(times[k+1]-times[k]);x=path[k][0]*(1-a)+path[k+1][0]*a;z=path[k][1]*(1-a)+path[k+1][1]*a
   o.location=(-12+x,y+depth,2.6+z);o.keyframe_insert(data_path='location',frame=f)
   o.rotation_euler=(t*math.tau,t*math.pi,phase*math.tau);o.keyframe_insert(data_path='rotation_euler',frame=f)
   maximum=max(maximum,math.hypot(x,z)+.15)
  for slot in o.animation_data.action.slots:
   for layer in o.animation_data.action.layers:
    for strip in layer.strips:
     bag=strip.channelbag(slot)
     if bag:
      for fc in bag.fcurves:
       for key in fc.keyframe_points:key.interpolation='LINEAR'
       fc.modifiers.new('CYCLES')
  assert maximum<1.5
  report['rocks'].append({'name':o.name,'max_envelope_radius_m':maximum})
# Review noise was sample starvation in the source's EEVEE settings. This is
# a Blender-only render setting, independent of Quest runtime lighting.
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64;s.eevee.shadow_pool_size='1024'
s.camera=s.objects['CAM_main'];s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
Path(target).with_suffix('.polish.json').write_text(json.dumps(report,indent=2))
print('POLISH',target,'internal animated lumps',len(report['rocks']))
