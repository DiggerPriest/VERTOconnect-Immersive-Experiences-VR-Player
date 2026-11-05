"""Prepare a disposable roof-detail export copy; source meshes remain intact."""
import bpy,json,collections
from pathlib import Path
import sys
source,target=sys.argv[sys.argv.index('--')+1:]
assert not Path(target).exists()
bpy.ops.wm.open_mainfile(filepath=source)

from mathutils.bvhtree import BVHTree
from mathutils import Vector
rows=[]
def snap(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];e.to_mesh_clear();return v,f
def samples(v,f):
 return v+[(v[a]+v[b]+v[c])/3 for a,b,c in f]+[point for a,b,c in f for point in [(v[a]+v[b])/2,(v[b]+v[c])/2,(v[c]+v[a])/2]]
for o in bpy.context.scene.objects:
 if not o.name.startswith('STR_truss_'):continue
 v,f=snap(o);tree=BVHTree.FromPolygons(v,f,all_triangles=True)
 mod=o.modifiers.new('QuestRoofDetail','DECIMATE');mod.ratio=.5;mod.use_collapse_triangulate=True
 bpy.context.view_layer.update();v2,f2=snap(o);tree2=BVHTree.FromPolygons(v2,f2,all_triangles=True)
 distances=[tree2.find_nearest(p)[3] for p in samples(v,f)]+[tree.find_nearest(p)[3]for p in samples(v2,f2)]
 rows.append({'name':o.name,'before':len(f),'after':len(f2),'max_sampled_deviation_m':max(distances)})
assert len(rows)==8 and all(r['max_sampled_deviation_m']<.007 for r in rows),rows
bpy.ops.wm.save_as_mainfile(filepath=target,copy=True)
Path(target).with_suffix('.roof-audit.json').write_text(json.dumps({'source':source,'method':'reversible roof-only decimation; bidirectional vertices, centroids and all edge midpoints sampled','objects':rows},indent=2))
print('ROOF_DETAIL_PASS',sum(r['before']-r['after']for r in rows))
