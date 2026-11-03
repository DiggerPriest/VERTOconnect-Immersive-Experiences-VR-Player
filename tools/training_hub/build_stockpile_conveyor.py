import bpy,math,random
from mathutils import Vector
from datetime import datetime
s=bpy.context.scene
root='/Users/rpriest/Library/CloudStorage/OneDrive-VertoPtyLtd/Documents/ChatGPT/immivio-360-player/build/training-hub/'
bpy.ops.wm.save_as_mainfile(filepath=root+'source-checkpoints/before_incline_'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.blend',copy=True)
col=bpy.data.collections.new('CV2_StockpileConveyor');s.collection.children.link(col)
start=Vector((7.3,-6.3,.27));end=Vector((32,1,7.2));delta=end-start;axis=delta.normalized();side=Vector((-axis.y,axis.x,0)).normalized();up=side.cross(axis).normalized()
if up.z<0:up=-up
steel=bpy.data.materials['M_steel_charcoal'];yellow=bpy.data.materials['M_safety_yellow'];coal=bpy.data.materials['YARD_Coal']
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.materials.append(m);o=bpy.data.objects.new(n,d);col.objects.link(o);return o
def beam(n,a,b,w,h,m):
 a=Vector(a);b=Vector(b);q=(b-a).to_track_quat('Z','Y');u=q@Vector((w/2,0,0));v=q@Vector((0,h/2,0));verts=[tuple(p+su*u+sv*v) for p in [a,b] for su,sv in [(-1,-1),(-1,1),(1,1),(1,-1)]]
 return mesh(n,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
beam('CV2_carry_belt',start,end,1.1,.09,steel)
for sign in [-1,1]:
 offset=side*.7*sign-up*.12
 beam('CV2_frame_'+str(sign),start+offset,end+offset,.14,.25,yellow)
 beam('CV2_spill_guard_'+str(sign),start+side*.59*sign+up*.12,end+side*.59*sign+up*.12,.045,.27,steel)
for i in range(1,9):
 p=start+delta*i/9
 for sign in [-1,1]:
  top=p+side*.75*sign-up*.2;bottom=Vector((top.x,top.y,0))
  beam('CV2_support_'+str(i)+'_'+str(sign),bottom,top,.17,.17,steel)
 beam('CV2_crossmember_'+str(i),p-side*.8-up*.3,p+side*.8-up*.3,.15,.15,steel)
# Door is an existing full-height opening. Keep its structural jambs.
for n in ['ENV_roller_stores_shutter','CV_Hopper_outlet_gate']:
 o=s.objects[n];o.hide_render=True;o.hide_set(True)
# Coal instances follow the carry surface, drop into pile, then recycle invisibly.
source=s.objects['CV_Hopper_OreBed_00'];random.seed(4)
for i in range(42):
 o=bpy.data.objects.new('CV2_COAL_'+str(i).zfill(3),source.data.copy());col.objects.link(o);o.data.materials.clear();o.data.materials.append(coal)
 o.rotation_euler=(random.random(),random.random(),random.random());offset=side*random.uniform(-.35,.35)
 for f in range(1,602):
  t=((f-1)/600+i/42)%1
  if t<.92:
   o.location=start+delta*(t/.92)+up*.14+offset;o.scale=(1,1,1)
  elif t<.975:
   k=(t-.92)/.055;o.location=end+axis*k*.8+Vector((0,0,-2*k*k))+offset;o.scale=(1,1,1)
  else:o.location=end+Vector((0,0,-4));o.scale=(0,0,0)
  o.keyframe_insert(data_path='location',frame=f);o.keyframe_insert(data_path='scale',frame=f)
 action=o.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for cb in strip.channelbags:
    for fc in cb.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
# Receiving stockpile outside the opening; existing coal heap copied with its material.
pile=s.objects['YARD_ore_stockpile_2'];copy=pile.copy();copy.data=pile.data.copy();copy.name='CV2_receiving_coal_stockpile';col.objects.link(copy);copy.location=(32,-51,0)
# Ground beneath the outside conveyor, in the existing earth material.
beam('CV2_exterior_apron',(25,-10,-.16),(25,12,-.16),28,.3,bpy.data.materials['YARD_ochre_earth'])
s.frame_set(180)
result={'created':len(col.objects),'animated_coal':42,'start':list(start),'end':list(end),'opening_crossing_height':.27+(20-7.3)/24.7*6.93}
