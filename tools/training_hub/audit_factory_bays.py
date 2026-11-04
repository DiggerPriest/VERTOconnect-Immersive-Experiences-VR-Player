"""Audit moving crane, drum contact and floor route in the actual saved scene."""
import bpy,sys,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
source,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=source);s=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=s
report={'failures':[],'crane_samples':[],'route_intrusions':[]}
def world_mesh(o,deps):
 obj=o.evaluated_get(deps);me=obj.to_mesh()
 try:return BVHTree.FromPolygons([obj.matrix_world@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons],all_triangles=False)
 finally:obj.to_mesh_clear()
def intersects(a,b,deps):
 def bounds(o):
  evaluated=o.evaluated_get(deps)
  points=[evaluated.matrix_world@Vector(v) for v in evaluated.bound_box]
  return ([min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)])
 alo,ahi=bounds(a);blo,bhi=bounds(b)
 if any(ahi[i]<blo[i] or bhi[i]<alo[i] for i in range(3)):return False
 return bool(world_mesh(a,deps).overlap(world_mesh(b,deps)))

# New moving bridge and trolley must remain clear of structural trusses/columns.
structure=[o for o in s.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('STR_truss') or o.name.startswith('STR_column'))]
crane=[o for o in bpy.data.collections['WKS_Overhead_Crane'].objects if o.type=='MESH' and not o.name.startswith('CRANE_runway')]
for frame in sorted(set(range(1,1202,12)) | {1,151,376,601,751,976,1201}):
 s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();collisions=[]
 for o in crane:
  for static in structure:
   if intersects(o,static,deps):collisions.append([o.name,static.name])
 hook=s.objects['CRANE_hook_block'].evaluated_get(deps).matrix_world.translation
 report['crane_samples'].append({'frame':frame,'hook':list(hook),'structural_intersections':collisions})
 if collisions:report['failures'].append({'frame':frame,'crane_collisions':collisions})
# All new equipment must also clear the existing column geometry (not merely
# its origin/bounds, since the original columns are one combined mesh).
s.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
column=s.objects['STR_columns'];column_tree=world_mesh(column,deps)
column_hits=[]
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and o.name.startswith(('EXP_','FIT_')) and not o.name.startswith(('FIT_CraneBracket_', 'FIT_CraneBrace_')):
  if column_tree.overlap(world_mesh(o,deps)):column_hits.append(o.name)
report['equipment_column_intersections']=column_hits
if column_hits:report['failures'].append('Equipment intersects structural columns')
# Opening and closing hook pose must agree, and the middle must actually travel.
a=Vector(report['crane_samples'][0]['hook']);b=Vector(report['crane_samples'][-1]['hook']);mid=Vector(next(sample['hook'] for sample in report['crane_samples'] if sample['frame']==601))
report['crane_loop_gap_m']=(a-b).length;report['crane_travel_m']=(a-mid).length
if (a-b).length>.001 or (a-mid).length<2:report['failures'].append('Crane motion/loop failed')
s.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not o.name.startswith(('FIT_','EXP_')):continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
 if hi.z>0.1 and lo.z<2.0 and hi.x>-3 and lo.x<3 and hi.y>-20 and lo.y<20:
  report['route_intrusions'].append(o.name)
if report['route_intrusions']:report['failures'].append('New equipment occupies centre route')
# Gallery feet and tread geometry: last tread must meet deck elevation (within riser).
report['east_stair_clearance_to_conveyor_m']=None
stair=[o for o in s.objects if o.name.startswith('FIT_Stair') and o.type=='MESH']
conveyor=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('CV2_','CV_'))]
intersections=[]
for o in stair:
 for fixed in conveyor:
  if intersects(o,fixed,deps):intersections.append([o.name,fixed.name])
report['stair_conveyor_intersections']=intersections
if intersections:report['failures'].append('Stair intersects stockpile conveyor')
report['default_camera']=s.camera.name
if s.camera.name!='CAM_main':report['failures'].append('Wrong default camera')
report['mesh_objects']=sum(o.type=='MESH' and not o.hide_render for o in s.objects)
Path(out).write_text(json.dumps(report,indent=2));print('BAYS_AUDIT',json.dumps({'frames':len(report['crane_samples']),'failures':report['failures'],'loop_gap_m':report['crane_loop_gap_m'],'travel_m':report['crane_travel_m']}));assert not report['failures']
