"""Sample authored fan motion and write evidence; run after factory scripts."""
import bpy,json,math
from pathlib import Path
s=bpy.data.scenes['VERTO_MiningFactory']
out=Path('/tmp/verto-factory-audit');out.mkdir(exist_ok=True)
rotors=[s.objects['FAN_'+str(side)+'_rotor'] for side in [-1,1]]
samples=[]
for frame in [1,16,31,450,900,901]:
 s.frame_set(frame)
 samples.append({'frame':frame,'rotations_y':[o.rotation_euler.y for o in rotors]})
for i,o in enumerate(rotors):
 assert abs(samples[1]['rotations_y'][i]-samples[0]['rotations_y'][i])>.1,'No fan motion'
 assert abs(math.remainder(samples[-1]['rotations_y'][i],math.tau))<1e-4,'Loop seam mismatch'
for frame in [1,16,31]:
 s.frame_set(frame);s.render.filepath=str(out/f'fans-{frame:03d}.png');bpy.ops.render.render(write_still=True)
s.frame_set(1)
(out/'motion.json').write_text(json.dumps({'samples':samples,'scope':'Blender transforms only; GLB/Godot/headset pending'},indent=2))
print('FACTORY_MOTION_AUDIT_PASS')
