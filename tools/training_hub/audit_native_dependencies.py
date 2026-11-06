"""Blender --background --python this.py -- SOURCE.blend REPORT.json"""
import json
import hashlib
from pathlib import Path
import sys
import bpy

source, destination = map(Path, sys.argv[sys.argv.index("--") + 1:])
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
images = [{"name": image.name, "packed": bool(image.packed_file), "path": image.filepath}
          for image in bpy.data.images if image.source == "FILE"]
assert all(image["packed"] for image in images), "Unpacked file image"
assert not bpy.data.libraries, "External linked Blender library"
assert all(font.filepath == "<builtin>" or font.packed_file for font in bpy.data.fonts), "External font"
reviewed_texts = {
    "CV_helpers.py": "80be6ba03d071be3f0b38b0f6dd613d7e9fd8b3bf50b2a8ed98984dc126bc477",
    "CV_PrebuildAudit.json": "6b8e7798c8237025cbb8a2c96352ac7f9d4572cd4bbbe660646540b124accf61",
    "CV_ScenePassport.json": "47a84488735d2b0cd665c97e7b2fd2339c327930a027f2f483a2a879676e7586",
}
for text in bpy.data.texts:
    assert not text.use_module, "Embedded text must not auto-run"
    assert hashlib.sha256(text.as_string().encode()).hexdigest() == reviewed_texts.get(text.name), "Unreviewed embedded text"
report = {"images": images, "libraries": len(bpy.data.libraries),
          "objects": len(bpy.context.scene.objects), "actions": len(bpy.data.actions),
          "collections": [collection.name for collection in bpy.data.collections],
          "unit_scale": bpy.context.scene.unit_settings.scale_length,
          "reviewed_non_autorun_texts": [text.name for text in bpy.data.texts]}
destination.write_text(json.dumps(report, indent=2) + "\n")
print("NATIVE_DEPENDENCIES_PASS", len(images), report["objects"])
