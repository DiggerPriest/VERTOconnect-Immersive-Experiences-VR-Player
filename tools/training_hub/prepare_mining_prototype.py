"""Prepare isolated review project; download only SHA-pinned CC0 rock maps."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

FILES = {
    'diff': '2787cfdf899ea12442e67e337e32712d6e25f4a0763ab3df63fd9306a02e156f',
    'nor_gl': '440e81881c0681f9dc7efbc5bcf97c9585801bcbdc95b7bd74d6d18657e46f20',
    'rough': '69588fbeb8672ed0d448af7fbf28e834cc1e8dfde45bd1c5dbf6bf50d2674130',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='build/training-hub/mining-prototype')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    textures = output / 'textures'
    textures.mkdir(parents=True, exist_ok=True)
    records = []
    for role, digest in FILES.items():
        filename = f'rock_boulder_dry_{role}_4k.jpg'
        url = f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/rock_boulder_dry/{filename}'
        target = textures / filename
        if not target.exists():
            urllib.request.urlretrieve(url, target)
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise RuntimeError(f'Unexpected asset bytes: {target}')
        records.append(dict(file=filename, url=url, sha256=digest, bytes=len(data)))
    (textures / 'provenance.json').write_text(json.dumps(dict(
        source='https://polyhaven.com/a/rock_boulder_dry',
        license='https://polyhaven.com/license', files=records), indent=2))
    (output / 'project.godot').write_text('''config_version=5
[application]
config/name="Isolated mining review"
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
''')
    shutil.copyfile(Path(__file__).with_name('render_mining_prototype.gd'), output / 'render.gd')
    print(output)

if __name__ == '__main__':
    main()
