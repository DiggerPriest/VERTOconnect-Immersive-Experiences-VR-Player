import json
from pathlib import Path
import struct
import tempfile
import unittest
from configs import training_hub_textures as policy


class HubTexturePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.folder = self.project / 'environments/training_hub'
        self.folder.mkdir(parents=True)
        image = {'name': 'Baked_wall', 'mimeType': 'image/png', 'bufferView': 0}
        payload = json.dumps({'images': [image]}).encode()
        data = b'glTF' + struct.pack('<II', 2, len(payload) + 20) + struct.pack('<I', len(payload)) + b'JSON' + payload
        for stem in policy.ASSETS:
            (self.folder / (stem + '.glb')).write_bytes(data)
            (self.folder / (stem + '_Baked_wall.png')).write_bytes(b'png')
            (self.folder / (stem + '_Baked_wall.png.import')).write_text('[params]\ncompress/mode=0\nmipmaps/generate=false\ndetect_3d/compress_to=0\n')

        (self.folder / 'surface_detail.png').write_bytes(b'authored')
        (self.folder / 'surface_detail.png.import').write_text('[params]\ncompress/mode=0\nmipmaps/generate=false\ndetect_3d/compress_to=0\n')

    def valid_outputs(self):
        policy.configure(self.project)
        cache = self.project / '.godot/imported'
        cache.mkdir(parents=True, exist_ok=True)
        for texture in policy.texture_paths(self.project):
            output = cache / (texture.name + '.etc2.ctex')
            output.write_bytes(b'nonempty-compressed-fixture')
            imp = texture.with_suffix('.png.import')
            imp.write_text(imp.read_text() + '\n"vram_texture": true\npath.etc2="res://.godot/imported/' + output.name + '"\n')

    def test_scoped_and_idempotent(self):
        outside = self.project / 'unrelated.png.import'
        outside.write_text('compress/mode=0')
        self.assertEqual(policy.configure(self.project), 6)
        # A pending reimport remains pending until importer records VRAM output.
        self.assertEqual(policy.configure(self.project), 6)
        for texture in policy.texture_paths(self.project):
            imp = texture.with_suffix('.png.import')
            imp.write_text(imp.read_text() + '\n"vram_texture": true\n# imported_formats etc2_astc alone is not proof\n')
        self.assertEqual(policy.configure(self.project), 0)
        self.assertEqual(outside.read_text(), 'compress/mode=0')
        for p in policy.texture_paths(self.project):
            text = p.with_suffix('.png.import').read_text()
            self.assertIn('compress/mode=2', text)
            self.assertIn('mipmaps/generate=true', text)

    def test_incomplete_extraction_fails(self):
        policy.texture_paths(self.project)[0].unlink()
        with self.assertRaisesRegex(RuntimeError, 'extract'):
            policy.configure(self.project)

    def test_verify_requires_actual_android_compressed_output(self):
        policy.configure(self.project)
        with self.assertRaisesRegex(RuntimeError, 'not VRAM compressed'):
            policy.verify(self.project)
        for p in policy.texture_paths(self.project):
            imp = p.with_suffix('.png.import')
            imp.write_text(imp.read_text() + '\n"vram_texture": true\n# imported_formats etc2_astc alone is not proof\n')
        with self.assertRaisesRegex(RuntimeError, 'lacks Android'):
            policy.verify(self.project)
        for p in policy.texture_paths(self.project):
            imp = p.with_suffix('.png.import')
            imp.write_text(imp.read_text() + '\npath.etc2="res://.godot/imported/test.etc2.ctex"\n')
        with self.assertRaisesRegex(RuntimeError, 'output missing'):
            policy.verify(self.project)
        cache = self.project / '.godot/imported'
        cache.mkdir(parents=True)
        (cache / 'test.etc2.ctex').write_bytes(b'actual-test-output')
        policy.verify(self.project)

    def test_missing_empty_and_traversal_outputs_rejected(self):
        for case in ['missing', 'empty', 'traversal', 'absolute', 'symlink', 'mipmaps']:
            with self.subTest(case=case):
                # Reset metadata so repeated case setup cannot add duplicate paths.
                for texture in policy.texture_paths(self.project):
                    texture.with_suffix('.png.import').write_text('compress/mode=0\nmipmaps/generate=false\ndetect_3d/compress_to=1\n')
                self.valid_outputs()
                texture = policy.texture_paths(self.project)[0]
                output = self.project / '.godot/imported' / (texture.name + '.etc2.ctex')
                imp = texture.with_suffix('.png.import')
                if case == 'missing':
                    output.unlink()
                elif case == 'empty':
                    output.write_bytes(b'')
                elif case == 'traversal':
                    imp.write_text(imp.read_text().replace(output.name, '../outside.ctex'))
                elif case == 'absolute':
                    imp.write_text(imp.read_text().replace('res://.godot/imported/' + output.name, '/tmp/outside.ctex'))
                elif case == 'symlink':
                    outside = self.project / 'outside.ctex'
                    outside.write_bytes(b'outside')
                    output.unlink()
                    output.symlink_to(outside)
                else:
                    imp.write_text(imp.read_text().replace('mipmaps/generate=true', 'mipmaps/generate=false'))
                with self.assertRaises(RuntimeError):
                    policy.verify(self.project)
                if output.is_symlink():
                    output.unlink()

    def test_authored_detail_is_required(self):
        (self.folder / 'surface_detail.png').unlink()
        with self.assertRaisesRegex(RuntimeError, 'surface_detail'):
            policy.configure(self.project)

    def test_absent_feature_is_noop(self):
        self.assertEqual(policy.configure(self.project / 'absent'), 0)
        policy.verify(self.project / 'absent')


if __name__ == '__main__':
    unittest.main()
