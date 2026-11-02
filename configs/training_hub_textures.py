"""Reproducible import policy for textures extracted from the reviewed hub GLBs.

No source PNG duplication: Godot extracts them; this sets per-texture VRAM import
options before a second import. No files outside the hub directory are touched.
"""
import json
from pathlib import Path, PurePosixPath
import re
import struct

ASSETS = ("training_hub", "electrical_worker", "plumbing_worker", "carpentry_worker", "mechanical_worker")


def texture_paths(project):
    folder = Path(project) / "environments/training_hub"
    paths = []
    if not (folder / "training_hub.glb").exists():
        return paths
    for stem in ASSETS:
        data = (folder / (stem + ".glb")).read_bytes()
        if data[:4] != b"glTF" or data[16:20] != b"JSON":
            raise ValueError("Invalid hub GLB: " + stem)
        document = json.loads(data[20:20 + struct.unpack_from("<I", data, 12)[0]])
        for image in document.get("images", []):
            name = image.get("name", "")
            if not name or any(c in name for c in '/\\:') or name in (".", ".."):
                raise ValueError("Unsafe or unnamed hub texture")
            if image.get("mimeType") != "image/png" or "bufferView" not in image:
                raise ValueError("Hub texture must be embedded PNG")
            paths.append(folder / (stem + "_" + name + ".png"))
    paths.append(folder / "surface_detail.png")
    return paths


def configure(project):
    """Return count of import files changed, failing if extraction is incomplete."""
    changed = 0
    for texture in texture_paths(project):
        settings = texture.with_suffix(".png.import")
        if not texture.is_file() or not settings.is_file():
            raise RuntimeError("Godot must extract hub textures before configuring: " + texture.name)
        source = settings.read_text()
        updated = source
        for key, value in (("compress/mode", "2"), ("mipmaps/generate", "true"), ("detect_3d/compress_to", "1")):
            pattern = r"(?m)^" + re.escape(key) + r"=.*$"
            if not re.search(pattern, updated):
                raise RuntimeError("Missing import parameter: " + key)
            updated = re.sub(pattern, key + "=" + value, updated)
        if updated != source or '"vram_texture": true' not in source:
            settings.write_text(updated)
            changed += 1
    return changed


def verify(project):
    project = Path(project).resolve()
    cache = (project / ".godot/imported").resolve()
    # Do not follow an imported-directory symlink outside the project either.
    if not cache.is_relative_to(project):
        raise RuntimeError("Unsafe imported texture directory")
    for texture in texture_paths(project):
        source = texture.with_suffix(".png.import").read_text()
        if not re.search(r"(?m)^compress/mode=2$", source) or '\"vram_texture\": true' not in source:
            raise RuntimeError("Hub texture not VRAM compressed: " + texture.name)
        if not re.search(r"(?m)^mipmaps/generate=true$", source):
            raise RuntimeError("Hub texture mipmaps disabled: " + texture.name)
        variants = re.findall(r'(?m)^path\.(?:etc2|astc)="([^"\r\n]+)"$', source)
        if not variants:
            raise RuntimeError("Hub texture lacks Android compressed variant: " + texture.name)
        for declared in variants:
            prefix = "res://.godot/imported/"
            relative = declared[len(prefix):] if declared.startswith(prefix) else ""
            path = PurePosixPath(relative)
            if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
                raise RuntimeError("Unsafe Android texture output path: " + texture.name)
            output = (cache / relative).resolve()
            if not output.is_relative_to(cache) or not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError("Android texture output missing, empty or unsafe: " + texture.name)
