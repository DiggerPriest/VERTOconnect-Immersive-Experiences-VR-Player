"""Exact reviewed-asset exemptions must not weaken the public-source boundary."""
import hashlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("public_source", ROOT / "tools/Check-PublicSource.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def base_files():
    names = {"LICENSE", "README.md", "CHANGELOG.md", "docs/BUILD.md", "docs/LICENSING.md",
             "app/godot/project.godot", "android/player-plugin/build.gradle",
             "native/mpv/CMakeLists.txt", "native/CMakeLists.txt"}
    return {name: (ROOT / name).read_bytes() for name in names}


class TrainingHubBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.files = base_files()
        self.files.update({name: (ROOT / name).read_bytes() for name in checker.TRAINING_HUB_REQUIRED})
        self.asset = "app/godot/environments/training_hub/electrical_worker.glb"
        self.files[self.asset] = (ROOT / self.asset).read_bytes()

    def test_reviewed_asset_with_sources_passes(self):
        self.assertEqual(checker.check_files(self.files), [])

    def test_all_current_exports_match_their_reviewed_pins(self):
        self.files.update({name: (ROOT / name).read_bytes() for name in checker.TRAINING_HUB_PINS})
        self.assertEqual(checker.check_files(self.files), [])

    def test_changed_bytes_are_rejected(self):
        self.files[self.asset] += b"changed"
        self.assertTrue(any("differs from reviewed" in e for e in checker.check_files(self.files)))

    def test_copy_at_another_path_is_rejected(self):
        self.files["app/godot/environments/unreviewed.glb"] = self.files[self.asset]
        self.assertTrue(any("unreviewed GLB" in e for e in checker.check_files(self.files)))

    def test_missing_or_empty_provenance_and_sources_rejected(self):
        for required in checker.TRAINING_HUB_REQUIRED:
            with self.subTest(required=required):
                candidate = dict(self.files)
                del candidate[required]
                self.assertTrue(any(required in e and "provenance missing" in e for e in checker.check_files(candidate)))
                candidate[required] = b"  \n"
                self.assertTrue(any(required in e and "provenance missing" in e for e in checker.check_files(candidate)))

    def test_large_exemption_only_for_exact_pin_and_capped_at_50_mib(self):
        for size_mib, accepted in [(26, True), (51, False)]:
            data = b"\xff" * (size_mib * 1024 * 1024)
            self.files[self.asset] = data
            with patch.dict(checker.TRAINING_HUB_PINS, {self.asset: hashlib.sha256(data).hexdigest()}):
                errors = checker.check_files(self.files)
                self.assertEqual(not errors, accepted, errors)
            self.assertTrue(any("over 25 MiB" in e for e in checker.check_files(self.files)))

    def test_regular_asset_still_has_25_mib_limit(self):
        self.files["app/godot/large.jpg"] = b"\xff" * (26 * 1024 * 1024)
        self.assertTrue(any("large.jpg: unexpected file over 25 MiB" in e for e in checker.check_files(self.files)))

    def test_blender_source_requires_exact_bytes_path_and_provenance(self):
        asset = "assets/authoring/mining_factory.blend"
        self.files.update({name: (ROOT / name).read_bytes() for name in checker.BLENDER_SOURCE_REQUIRED})
        self.files[asset] = (ROOT / asset).read_bytes()
        self.assertEqual(checker.check_files(self.files), [])
        altered = dict(self.files)
        altered[asset] += b"changed"
        self.assertTrue(any("Blender source differs" in e for e in checker.check_files(altered)))
        copied = dict(self.files)
        copied["assets/authoring/unreviewed.blend"] = self.files[asset]
        self.assertTrue(any("unreviewed Blender" in e for e in checker.check_files(copied)))
        for required in checker.BLENDER_SOURCE_REQUIRED:
            missing = dict(self.files)
            del missing[required]
            self.assertTrue(any(required in e and "provenance missing" in e for e in checker.check_files(missing)))

    def test_blender_source_size_exception_is_capped(self):
        asset = "assets/authoring/mining_factory.blend"
        self.files.update({name: (ROOT / name).read_bytes() for name in checker.BLENDER_SOURCE_REQUIRED})
        for size, accepted in [(26, True), (51, False)]:
            self.files[asset] = b"\xff" * (size * 1024 * 1024)
            with patch.dict(checker.BLENDER_SOURCE_PINS, {asset: hashlib.sha256(self.files[asset]).hexdigest()}):
                self.assertEqual(not checker.check_files(self.files), accepted)


if __name__ == "__main__":
    unittest.main()
