"""Simplify baked sign meshes in a disposable export copy, with shape checks."""
import bpy,json,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
source,target=sys.argv[sys.argv.index('--')+1:]
assert source!=target and not Path(target).exists()
bpy.ops.wm.open_mainfile(filepath=source)
def snapshot(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];e.to_mesh_clear();return v,f
def samples(v,f):
 return v+[(v[a]+v[b]+v[c])/3 for a,b,c in f]+[point for a,b,c in f for point in [(v[a]+v[b])/2,(v[b]+v[c])/2,(v[c]+v[a])/2]]
rows=[]
for name,limit in [('SGN_VERTOconnect',.002),('SGN_letters_decline',.0005)]:
 o=bpy.data.objects[name];assert o.type=='MESH' and not o.animation_data
 v,f=snapshot(o);tree=BVHTree.FromPolygons(v,f,all_triangles=True);original_samples=samples(v,f);attempts=[]
 mod=o.modifiers.new('QuestSignDetail','DECIMATE');mod.use_collapse_triangulate=True
 for ratio in [.25,.5,.75]:
  mod.ratio=ratio;bpy.context.view_layer.update();v2,f2=snapshot(o);tree2=BVHTree.FromPolygons(v2,f2,all_triangles=True)
  distances=[tree2.find_nearest(p)[3] for p in original_samples]+[tree.find_nearest(p)[3]for p in samples(v2,f2)]
  error=max(distances);attempts.append({'ratio':ratio,'triangles':len(f2),'max_sampled_deviation_m':error})
  if error<=limit:break
 else:raise RuntimeError('No acceptable sign reduction: '+str(attempts))
 # These signs can own children and bypass the exporter's static-leaf bake.
 # Materialise only this disposable copy so glTF cannot omit the modifier.
 deps=bpy.context.evaluated_depsgraph_get()
 o.data=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
 o.modifiers.clear();bpy.context.view_layer.update()
 assert len(snapshot(o)[1])==len(f2), 'Reduction did not persist'
 rows.append({'name':name,'before':len(f),'after':len(f2),'tolerance_m':limit,'attempts':attempts,'selected_ratio':ratio})
bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
Path(target).with_suffix('.sign-audit.json').write_text(json.dumps({'source':source,'scope':'Bidirectional vertex, centroid and all edge-midpoint surface samples; not exhaustive shape proof','objects':rows},indent=2))
print('SIGN_DETAIL_PASS',sum(r['before']-r['after']for r in rows))
