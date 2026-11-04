"""Measure authored rotation and fixed supports independently of the viewport."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];bpy.ops.wm.open_mainfile(filepath=args[0]);scene=bpy.data.scenes['VERTO_Higgsfield_Mining_Concept'];bpy.context.window.scene=scene
results={};failures=[]
for i in range(2):
 rotor=scene.objects[f'EXP_Screen_{i}_Rotor'];child=scene.objects[f'EXP_Screen_{i}_Panel_0'];samples=[]
 for f in [1,151,301,451,600,601]:
  scene.frame_set(f);bpy.context.view_layer.update();c=child.evaluated_get(bpy.context.evaluated_depsgraph_get());samples.append({'frame':f,'rotation_y':rotor.rotation_euler.y,'point':list(c.matrix_world@c.data.vertices[0].co)})
 origin=Vector(samples[0]['point']);seam=(origin-Vector(samples[-1]['point'])).length
 motion=(origin-Vector(samples[2]['point'])).length
 if seam>.0001 or motion<1:failures.append(f'Rotor {i} motion/loop mismatch')
 results[f'rotor_{i}']={'samples':samples,'loop_gap_m':seam,'half_cycle_travel_m':motion}
scene.frame_set(1)
results['objects_added']=len(bpy.data.collections['EXP_Processing'].objects)
results['failures']=failures
Path(args[1]).write_text(json.dumps(results,indent=2));print(json.dumps(results))
assert not failures
