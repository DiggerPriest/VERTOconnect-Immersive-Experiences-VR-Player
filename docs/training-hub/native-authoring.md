# Editable mining factory source

`assets/authoring/mining_factory.blend` is the reviewed native scene, saved with Blender 5.1.2. It contains 6,522 objects in named machinery, structure and service collections, reusable materials and native animation actions. Nine file textures are packed; there are no linked libraries, and fonts are packed or built in. Open the file directly in Blender. No Higgsfield generation account is needed to edit or export it.

The file lives outside `app/godot` so Godot does not import a second copy into the application. It is stored as an ordinary, checksum-reviewed Git asset, like the existing GLB. Keep incremental working copies outside the repository; replace this one only after a reviewed export.

Source SHA-256: `af99efac55b47d856f86eef438838462a17f8245a4f9a3c30ab10742d08bd87a`.

The source includes viewport-only noticeboard preview objects. They are hidden from export. The application creates the interactive board and populates it from playback history; Blender cannot display the headset's live history. Preview labels are not video titles.

Three historical conveyor text blocks are retained: a geometry helper, prebuild audit and scene passport. None auto-run. Their exact contents are reviewed and pinned by `audit_native_dependencies.py`; they are historical authoring context, not the current rebuild procedure. Do not rerun the old helper to recreate the whole facility.

## Rebuild from the repository root

Use Python 3 and Blender 5.1.2. Choose a fresh output directory/label; intermediate export files are disposable and must not overwrite the editable source.

```sh
python3 tools/training_hub/build_density_export.py assets/authoring/mining_factory.blend /tmp/factory-export review --blender /path/to/Blender
```

The pipeline simplifies distant roof detail and lettering, bakes bounded vertex ambient occlusion, batches static surfaces, packs solid colours and shares animated meshes. It verifies the native source is unchanged. Copy the resulting `review.glb` to `app/godot/environments/mining_facility_density/mining_facility.glb`, run the Godot editor import, and repeat the runtime checks before updating the asset checksum in `tools/Check-PublicSource.py`. Binary-identical regenerated exports are not assumed across Blender or exporter versions.

Current reviewed runtime SHA-256: `88f778104020c43e05809dab0aa5752b4fbb18d866c5efeb392e7728085b3aac`.

The source preserves existing concrete/rock texture provenance documented with the mining environment. New factory equipment is constructed locally. The material polish makes paint dielectric, reduces skylight glare and removes the obsolete central metal inlay and isolated baseplate. Welding screens are parked beside the inactive fabrication bay to expose its workbench and the conveyor; all screen components remain present.

The application preserves its fixed origin, tracked headset pose and portal-facing initial direction. Desktop review uses a 1.6 m eye height. Development captures and timings do not establish physical Quest performance or comfort.
