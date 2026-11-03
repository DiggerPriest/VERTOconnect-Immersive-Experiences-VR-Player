"""Author guarded axial ventilation assemblies in the isolated factory scene."""
import bpy, math
from mathutils import Vector
s=bpy.data.scenes['VERTO_MiningFactory'];bpy.context.window.scene=s
if bpy.data.collections.get('PRP_ventilation'):raise RuntimeError('Inspect existing ventilation before rebuilding')
c=bpy.data.collections.new('PRP_ventilation');s.collection.children.link(c)
def mesh(name,vs,fs,col):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();o=bpy.data.objects.new(name,m);c.objects.link(o);o.color=(*col,1);return o
def ring(name,x,y,z,r,length,color,thick=.06):
 vs=[];n=48
 for yy,rr in [(y,r),(y+length,r),(y,r-thick),(y+length,r-thick)]:
  vs.extend([(x+rr*math.cos(i*math.tau/n),yy,z+rr*math.sin(i*math.tau/n)) for i in range(n)])
 fs=[]
 for i in range(n):
  j=(i+1)%n
  fs.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(j,i,2*n+i,2*n+j),(n+i,n+j,3*n+j,3*n+i)])
 return mesh(name,vs,fs,color)
def rod(name,a,b,r,col):
 d=Vector(b)-Vector(a);q=d.to_track_quat('Z','Y');vs=[];n=8
 for z in [0,d.length]:
  for i in range(n):vs.append(tuple(Vector(a)+q@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z))))
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,col)
for side in [-1,1]:
 x=side*7;y=14.4;z=1.65;prefix='FAN_'+str(side)
 ring(prefix+'_housing',x,y,z,1.42,2.7,(.72,.43,.055))
 for yy in [y-.07,y+2.65]:ring(prefix+'_flange',x,yy,z,1.52,.12,(.14,.18,.2),.15)
 # Connected duct runs towards portal then bends inward into tunnel.
 ring(prefix+'_duct',x,y+2.7,z,1.32,2.9,(.24,.29,.32),.04)
 for yy in [18,19.5]:ring(prefix+'_duct_band',x,yy,z,1.35,.09,(.11,.14,.16),.07)
 # Flexible sweep from side service run through portal opening.
 points=[Vector((x,20,1.65)),Vector((side*5.5,20.8,2)),Vector((side*1.65,22,2.9)),Vector((side*1.65,29,2.9))]
 vs=[];n=32
 for k,p in enumerate(points):
  tangent=points[min(k+1,len(points)-1)]-points[max(0,k-1)];q=tangent.to_track_quat('Z','Y')
  radius=1.1 if k<2 else .65
  vs.extend([tuple(p+q@Vector((radius*math.cos(i*math.tau/n),radius*math.sin(i*math.tau/n),0))) for i in range(n)])
 fs=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(points)-1) for i in range(n)]
 mesh(prefix+'_duct_elbow',vs,fs,(.22,.27,.29))
 rotor=bpy.data.objects.new(prefix+'_rotor',None);c.objects.link(rotor);rotor.location=(x,y+.4,z)
 for blade in range(7):
  a=blade*math.tau/7;vs=[]
  for radius,angle,depth in [(.28,a-.1,-.05),(.42,a+.35,.12),(1.3,a+.26,.06),(1.28,a-.07,-.08)]:vs.append((radius*math.cos(angle),depth,radius*math.sin(angle)))
  o=mesh(prefix+'_blade_'+str(blade),vs,[(0,1,2,3)],(.38,.43,.46));o.parent=rotor
 ring(prefix+'_hub',x,y+.25,z,.3,.4,(.12,.15,.17),.29)
 for r in [.38,.72,1.05,1.35]:ring(prefix+'_guard_'+str(r),x,y-.13,z,r,.035,(.1,.12,.13),.018)
 for i in range(12):
  a=i*math.tau/12;rod(prefix+'_guard_spoke_'+str(i),(x,y-.15,z),(x+1.4*math.cos(a),y-.15,z+1.4*math.sin(a)),.015,(.11,.13,.14))
 for dx in [-.9,.9]:
  for yy in [y+.3,y+2.3]:rod(prefix+'_mount',(x+dx,yy,.05),(x+dx,yy,.65),.12,(.12,.16,.18))
 rotor.rotation_euler[1]=0;rotor.keyframe_insert('rotation_euler',index=1,frame=1)
 rotor.rotation_euler[1]=math.tau*(15 if side<0 else 17);rotor.keyframe_insert('rotation_euler',index=1,frame=901)
 for layer in rotor.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
 proxy=s.objects['PROXY_fan_'+str(side)];proxy.hide_render=True;proxy.hide_set(True)
s.render.fps=30;s.frame_end=900;s.frame_set(1)
s.render.filepath='/tmp/verto-factory-fans.png';bpy.ops.render.render(write_still=True)
result={'objects_created':len(c.objects),'rotors':[o.name for o in c.objects if o.type=='EMPTY'],'preview':s.render.filepath}
