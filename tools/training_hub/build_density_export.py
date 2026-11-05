"""Build an optimised disposable export without altering the native source.

python3 build_density_export.py SOURCE.blend OUTPUT_FOLDER LABEL --blender PATH
This prepares assets only; it does not select a runtime asset or publish a build.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output_folder', type=Path)
    parser.add_argument('label')
    parser.add_argument('--blender', required=True, type=Path)
    args = parser.parse_args()
    assert args.source.is_file() and args.blender.is_file()
    assert args.label and all(c.isalnum() or c in '-_' for c in args.label)
    folder = args.output_folder.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent
    source = args.source.resolve()
    outputs = {key: folder / (args.label + suffix) for key, suffix in [
        ('roof', '_roof.blend'), ('sign', '_sign.blend'), ('ao', '_ao.blend'),
        ('glb', '.glb'), ('manifest', '.build.json')]}
    assert all(not p.exists() for p in outputs.values()), 'Use a fresh label; existing exports are preserved'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    steps = [
        ('prepare_factory_roof_lod.py', [source, outputs['roof']], 'ROOF_DETAIL_PASS'),
        ('prepare_factory_sign_lod.py', [outputs['roof'], outputs['sign']], 'SIGN_DETAIL_PASS'),
        ('bake_factory_vertex_ao.py', [outputs['sign'], outputs['ao']], 'VERTEX_AO'),
        ('export_higgsfield_checkpoint.py', [outputs['ao'], outputs['glb'],
            '--batch-static', '--pack-solid-colors', '--deduplicate-animated-meshes'], 'CHECKPOINT_EXPORT')]
    for script, parameters, marker in steps:
        log = folder / (args.label + '-' + script + '.log')
        with log.open('w') as stream:
            result = subprocess.run([str(args.blender), '--background', '--factory-startup',
                '--python', str(root / script), '--', *map(str, parameters)],
                stdout=stream, stderr=subprocess.STDOUT)
        assert result.returncode == 0 and marker in log.read_text(), f'Stage failed; inspect {log}'
        print(marker, flush=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash, 'Native source changed'
    audit = json.loads(outputs['glb'].with_suffix('.audit.json').read_text())
    outputs['manifest'].write_text(json.dumps({
        'native_editable_source': str(source), 'native_sha256': source_hash,
        'export_source': str(outputs['ao']), 'glb': str(outputs['glb']),
        'sha256': hashlib.sha256(outputs['glb'].read_bytes()).hexdigest(),
        'static_batches': audit['static_after'], 'animation_clips': audit['exported_clips'],
        'runtime_verified': False, 'quest_verified': False, 'released': False}, indent=2) + '\n')
    print('DENSITY_EXPORT_BUILT', outputs['manifest'])


if __name__ == '__main__':
    main()
