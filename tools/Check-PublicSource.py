"""Check tracked public files for excluded assets, private paths and credentials."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

FORBIDDEN_PARTS = {
    ".git",
    ".cache",
    ".venv",
    ".godot",
    ".gradle",
    ".cxx",
    "__pycache__",
    "prompt",
    "artifacts",
    "build",
    "tmp",
    "backups",
    "keystore",
    "releases",
    "credentials",
    "research",
}
FORBIDDEN_SUFFIXES = {
    ".onnx",
    ".mnn",
    ".pt",
    ".pth",
    ".ckpt",
    ".safetensors",
    ".bin",
    ".param",
    ".apk",
    ".aar",
    ".so",
    ".keystore",
    ".jks",
    ".p12",
    ".pfx",
    ".hdr",
    ".log",
    ".zip",
    ".7z",
    ".rar",
    ".key",
    ".pem",
}
# MIT-licensed glTF mesh buffers, not inference weights. Only these exact bytes qualify.
HAND_BUFFER_PINS = {
    "app/godot/models/hands/LeftHandHumanoid.bin": "05f96e5aae870c8f2fde8a1fea337b060c7fde3e659b124a5ed979f0ffa1222a",
    "app/godot/models/hands/RightHandHumanoid.bin": "89468a6868afbd6a9d5e545e7fdd5dadd7d7abab6d4389d8acc14a7804901e41",
}
# Bundled Inter font, distributed with its SIL Open Font License notice.
FONT_PINS = {
    "app/godot/branding/fonts/Inter.ttf": "29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031",
}
# Reviewed local training geometry and CC0 character exports; never a general GLB exemption.
TRAINING_HUB_PINS = {
    "app/godot/environments/mining_facility_density/mining_facility.glb": "2bef01d1ecabd0850d710ad2cbce9940696e5cf0ebe5598fbdc0ebf974f7b4f8",
    "app/godot/environments/mining_facility/mining_facility.glb": "4c2789eeccdd975f1e6c23d997e3c9d4abe8c9f77fe05e32e0c64d72ed525834",
    "app/godot/environments/training_hub/carpentry_worker.glb": "b64568c1897a61f1c872fdba1fe1496aea64e43702db4be1f7cc8e100b1bd3e3",
    "app/godot/environments/training_hub/electrical_worker.glb": "ad2be90e297d8d3b5b713bfb1c236242f5cdbe47c3819f16e1f7d805cae74558",
    "app/godot/environments/training_hub/mechanical_worker.glb": "309864a9a2c0eecc24f57bfdbbb9b38db31d7dfa1809d75978a0c3abc052225e",
    "app/godot/environments/training_hub/plumbing_worker.glb": "a24f52b01146cef43bd6d0e6e72fb35b33d7cda7afc637dd8b75f9d0d75b10de",
    "app/godot/environments/training_hub/training_hub.glb": "26bb5f2a03eb9cdd5b168384b7539968a71d5199ce79777e21b892b56eab3226",
}
USER_AUDIO_PINS = {
    "app/godot/audio/mining_background.mp3": "4270756480a1566c0788383eb1c7d5ff4797008fc03399cda247fa23d947cb98",
}
TRAINING_HUB_REQUIRED = {
    "tools/training_hub/densify_factory.py",
    "tools/training_hub/build_density_export.py",
    "docs/training-hub/density-export.md",
    "tools/training_hub/build_hub.py",
    "tools/training_hub/build_worker.py",
    "tools/training_hub/audit_glb.py",
    "tools/training_hub/reimport_textures.gd",
    "configs/training_hub_textures.py",
    "app/godot/environments/training_hub/surface_detail.png",
    "app/godot/scripts/training_hub_surfaces.gd",
    "app/godot/shaders/training_hub_surface.gdshader",
    "docs/training-hub/design.md",
    "docs/training-hub/environment.md",
    "docs/training-hub/worker.md",
    "third_party/player-licenses/training-hub/MakeHuman-ASSETS.md",
}
PATTERNS = {
    "private machine path": re.compile(
        r"(?i)(?:[CG]:[/\\]+(?:Users[/\\]+dennis|devtools|GIT|code[/\\]+VRPassthroughPlayer)|/mnt/"
        + r"g/|/opt/"
        + r"quest-mpv)"
    ),
    "GitHub credential": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"
    ),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "hardcoded signing password": re.compile(
        r"""(?im)(?:THRU3D_SIGNING_PASSWORD|IMMIVIO_SIGNING_PASSWORD|GODOT_ANDROID_KEYSTORE_(?:DEBUG|RELEASE)_PASSWORD)\s*(?:=|:)\s*['"][^'"\r\n]+['"]|-(?:storepass|keypass)\s+['"][^'"$\r\n]+['"]"""
    ),
    "private signing key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "private handover link": re.compile(
        r"(?i)(?:HANDOVER_\d{8}|docs/(?:store|archive|branding)/)"
    ),
}


def check_files(files):
    errors = []
    for name, data in files.items():
        path = PurePosixPath(name)
        if path.parts and path.parts[0].lower() == "freecm":
            errors.append(f"{name}: use the vendored FreeCM subset under third_party/freecm")
        if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
            errors.append(f"{name}: unsafe path")
        approved_mesh = name in HAND_BUFFER_PINS
        approved_font = name in FONT_PINS
        approved_hub = name in TRAINING_HUB_PINS and hashlib.sha256(data).hexdigest() == TRAINING_HUB_PINS[name]
        approved_audio = name in USER_AUDIO_PINS and hashlib.sha256(data).hexdigest() == USER_AUDIO_PINS[name]
        if name in USER_AUDIO_PINS and not approved_audio:
            errors.append(f"{name}: audio differs from pinned user-provided asset")
        if name in TRAINING_HUB_PINS and not approved_hub:
            errors.append(f"{name}: training hub mesh differs from reviewed asset")
        if path.suffix.lower() == ".glb" and name not in TRAINING_HUB_PINS:
            errors.append(f"{name}: unreviewed GLB asset")
        if approved_font and hashlib.sha256(data).hexdigest() != FONT_PINS[name]:
            errors.append(f"{name}: font differs from pinned asset")
        if approved_mesh and (
            len(data) != 38584
            or hashlib.sha256(data).hexdigest() != HAND_BUFFER_PINS[name]
        ):
            errors.append(f"{name}: hand mesh differs from reviewed MIT asset")
        if FORBIDDEN_PARTS.intersection(part.lower() for part in path.parts) or (
            path.suffix.lower() in FORBIDDEN_SUFFIXES and not approved_mesh
        ):
            errors.append(f"{name}: excluded directory or binary asset")
        if name.startswith(
            tuple("docs/" + item + "/" for item in ("store", "branding", "archive"))
        ) or name.startswith("tools/record_"):
            errors.append(f"{name}: private development or promotion content")
        if name.endswith("store_capture_debug.gd") or "local.properties" == path.name:
            errors.append(f"{name}: local-only configuration/tool")
        if path.name.lower() in {"signing-identities.json", ".env"} or (
            path.name.lower().startswith(("thru3d", "immivio"))
            and path.name.lower().endswith("-signing.json")
        ):
            errors.append(
                f"{name}: excluded signing identity or local credential configuration"
            )
        if path.name.lower().startswith(("readme", "changelog")) and name not in {
            "README.md",
            "CHANGELOG.md",
            "third_party/README.md",
        }:
            errors.append(f"{name}: internal documentation excluded")
        limit_mib = 50 if approved_hub else 25
        if len(data) > limit_mib * 1024 * 1024:
            errors.append(f"{name}: unexpected file over {limit_mib} MiB")
        try:
            value = data.decode("utf-8")
        except UnicodeDecodeError:
            if (
                path.suffix.lower()
                not in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".jar"}
                and not approved_mesh and not approved_font and not approved_hub and not approved_audio
            ):
                errors.append(f"{name}: unreviewed binary type")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(value):
                errors.append(f"{name}: {label}")  # Never print the matched credential.
    if HAND_BUFFER_PINS.keys() & files.keys():
        for name in (
            "LICENSE.txt",
            "NOTICE.txt",
            "hand.png",
            "LeftHandHumanoid.gltf",
            "RightHandHumanoid.gltf",
        ):
            asset = "app/godot/models/hands/" + name
            if asset not in files:
                errors.append(f"{asset}: hand mesh dependency/notice missing")
        for buffer in HAND_BUFFER_PINS:
            gltf = str(PurePosixPath(buffer).with_suffix(".gltf"))
            if gltf in files:
                try:
                    declared = json.loads(files[gltf])["buffers"]
                    if declared != [
                        {"byteLength": 38584, "uri": PurePosixPath(buffer).name}
                    ]:
                        errors.append(f"{gltf}: unexpected hand buffer reference")
                except (ValueError, KeyError, TypeError):
                    errors.append(f"{gltf}: invalid hand buffer contract")
    if FONT_PINS.keys() & files.keys() and "app/godot/branding/fonts/Inter-OFL.txt" not in files:
        errors.append("app/godot/branding/fonts/Inter-OFL.txt: font license missing")
    if TRAINING_HUB_PINS.keys() & files.keys():
        for name in sorted(TRAINING_HUB_REQUIRED):
            if not files.get(name, b"").strip():
                errors.append(f"{name}: training hub source/provenance missing")
    required = {
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "docs/BUILD.md",
        "docs/LICENSING.md",
        "app/godot/project.godot",
        "android/player-plugin/build.gradle",
        "native/mpv/CMakeLists.txt",
        "native/CMakeLists.txt",
    }
    errors.extend(
        f"{name}: required public file missing"
        for name in sorted(required - files.keys())
    )
    if "LICENSE" in files and b"Version 3, 29 June 2007" not in files["LICENSE"]:
        errors.append("LICENSE: expected complete GPL v3 text")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    names = subprocess.check_output(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            "ls-files",
            "-z",
        ],
        text=True,
    ).split("\0")
    files = {}
    for name in filter(None, names):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"{name}: tracked file is missing or redirected")
        files[name] = path.read_bytes()
    errors = check_files(files)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Public source boundary checks passed: {len(files)} tracked files")


if __name__ == "__main__":
    main()
