"""Denoise a rendered lighting atlas using the shared Blender bake pipeline."""
import bpy,ast,sys
from pathlib import Path
root=Path(__file__).resolve().parent
source,destination=map(Path,sys.argv[sys.argv.index('--')+1:])
if destination.exists(): raise RuntimeError('Refusing to overwrite atlas')
module=ast.parse((root/'build_hub.py').read_text())
function=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='denoise_atlas')
exec(compile(ast.Module(body=[function],type_ignores=[]),str(root/'build_hub.py'),'exec'))
image=bpy.data.images.load(str(source.resolve()),check_existing=False)
denoise_atlas(image,destination.resolve())
print('DENOISE_COMPLETE',flush=True)
