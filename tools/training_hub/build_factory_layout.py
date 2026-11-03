import bpy, math
from mathutils import Vector
name='VERTO_MiningFactory'
if name in bpy.data.scenes:
 raise RuntimeError('Factory already exists; inspect before rebuilding')
s=bpy.data.scenes.new(name)
bpy.context.window.scene=s
s.unit_settings.system='METRIC'
c=bpy.data.collections.new('ENV_shell');s.collection.children.link(c)
def box(name,loc,dim):
 x,y,z=[v/2 for v in dim]
 vs=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
 fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
 o=bpy.data.objects.new(name,m);c.objects.link(o);o.location=loc;return o
box('ENV_concrete_floor',(0,0,-.15),(40,44,.3))
for x in [-20,20]:box('ENV_side_wall_'+str(x),(x,0,6),(.25,44,12))
box('ENV_rear_wall',(0,-22,6),(40,.25,12))
for x in [-12.5,12.5]:box('ENV_portal_wall_'+str(x),(x,22,6),(15,.25,12))
box('ENV_portal_lintel',(0,22,9.5),(10,.25,5))
for x in [-18,18]:
 for y in [-20,-12,-4,4,12,20]:box('ENV_column_%s_%s'%(x,y),(x,y,6),(.45,.45,12))
for y in [-20,-12,-4,4,12,20]:
 box('ENV_roof_beam_'+str(y),(0,y,11.4),(36,.35,.7))
for x in [-15,-9,9,15]:box('ENV_roof_panel_'+str(x),(x,0,12),(5.9,44,.15))
# Central skylight strip is deliberately open in this massing study.
for side in [-1,1]:
 box('PROXY_fan_'+str(side),(side*7,16,1.5),(3,4,3))
box('PROXY_haul_truck',(11,5,3),(7,12,6))
box('PROXY_mechanical_workshop',(-16,3,1.5),(6,12,3))
box('PROXY_rear_service_stores',(0,-19,2),(30,4,4))
# Tunnel extends beyond portal and remains physically open towards the viewer.
box('ENV_tunnel_floor',(0,37,-.1),(10,30,.2))
for x in [-5,5]:box('ENV_tunnel_side_'+str(x),(x,37,3.5),(.3,30,7))
box('ENV_tunnel_roof',(0,37,7),(10,30,.3))
cam=bpy.data.cameras.new('CAM_seated');o=bpy.data.objects.new('CAM_seated',cam);s.collection.objects.link(o);o.location=(0,0,1.25);o.rotation_euler=(Vector((0,22,3))-o.location).to_track_quat('-Z','Y').to_euler();cam.lens=22;s.camera=o
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True
for o in s.objects:
 if o.type=='MESH':o.color=(.6,.63,.65,1) if not o.name.startswith('PROXY') else (.85,.49,.06,1)
s.render.image_settings.file_format='PNG';s.render.filepath='/tmp/verto-factory-layout.png'
bpy.ops.render.render(write_still=True)
result={'scene':s.name,'objects':len(s.objects),'preview':s.render.filepath,'status':'massing only; detailed asset replacement pending'}
