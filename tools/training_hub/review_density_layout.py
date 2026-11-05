"""Review-only six-view renders and equipment masks; never saves source.
blender --background --factory-startup --python this.py -- source.blend folder label
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
import numpy as np
source,folder,label=sys.argv[sys.argv.index('--')+1:]
folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=source)
s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s;s.frame_set(1)
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.eevee.shadow_pool_size='1024'
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('DENS_REVIEW_CAMERA');cam=bpy.data.objects.new(data.name,data);s.collection.objects.link(cam)
cam.location=(0,0,1.25);data.sensor_fit='VERTICAL';data.sensor_height=24;data.lens=12/math.tan(math.radians(85)/2);s.camera=cam
views={'portal':(-1,-22,2),'fans':(-16,-14,2.4),'conveyor':(13,-4,2),'rear':(1,22,2),'processing':(-12,8,2.5),'plant':(12,7,2.5)}
def render(view,mode):
 cam.rotation_euler=(Vector(views[view])-cam.location).to_track_quat('-Z','Y').to_euler()
 path=folder/(label+'_'+mode+'_'+view+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);return path
for view in views:render(view,'color')
def flat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
white=flat('DENS_MASK_EQUIPMENT',(1,1,1));black=flat('DENS_MASK_ARCHITECTURE',(0,0,0))
equipment_collections={'VENT','WORKSHOP','PROPS','CV_Conveyor','CV2_StockpileConveyor'}
for obj in s.objects:
 if obj.type in {'MESH','CURVE','FONT'}:
  names=[c.name for c in obj.users_collection]
  equipment=any(n in equipment_collections or n.startswith(('WKS_','EXP_','FIT_','DENS_')) for n in names)
  # A shared material slot is replaced consistently for each shared data block.
  obj.data.materials.clear();obj.data.materials.append(white if equipment else black)
for obj in s.objects:
 if obj.type=='LIGHT':obj.hide_render=True
s.world=bpy.data.worlds.new('DENS_MASK_WORLD');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(0,0,0,1)
s.view_settings.view_transform='Standard';s.view_settings.exposure=0;s.view_settings.gamma=1
coverage={}
for view in views:
 path=render(view,'mask');image=bpy.data.images.load(str(path),check_existing=False)
 pixels=np.asarray(image.pixels[:],dtype=np.float32).reshape(-1,4)
 coverage[view]=float(np.mean(np.min(pixels[:,:3],axis=1)>.5))
 bpy.data.images.remove(image)
report={'source':source,'label':label,'scope':'same six seated cameras,85deg vertical FOV; projected equipment coverage, not object count','coverage':coverage,'mean_coverage':sum(coverage.values())/len(coverage)}
(folder/(label+'_coverage.json')).write_text(json.dumps(report,indent=2))
print('DENSITY_VIEW_REVIEW',json.dumps(report))
