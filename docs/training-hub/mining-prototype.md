# Isolated underground mine composition study

This is a local preview, not a finished bay or a headset-tested environment. It is not selected by the player and has not replaced any live asset. There are no people.

The scene contains real 28-metre curved tunnel geometry, support arches, rail sleepers and rails, water services, power cables, ventilation duct, practical light housings, rescue cabinet and an elevated VERTOconnect sign. The camera uses a 1.65-metre eye height. The second view moves the camera to demonstrate actual depth.

Rock surfaces use **downloaded** [Poly Haven Rock Boulder Dry](https://polyhaven.com/a/rock_boulder_dry) diffuse, OpenGL normal and roughness maps under [CC0](https://polyhaven.com/license). The preparation script pins each downloaded file by SHA-256 and writes a provenance manifest. All geometry is authored in the reproducible Blender script. This is not an AI image projected onto a plane.

## Reproduction

Run from the repository root, with Blender 4.5.3 and Godot 4.7.2 available:

```sh
python3 tools/training_hub/prepare_mining_prototype.py
blender --background --python-exit-code 1 --python tools/training_hub/build_mining_prototype.py -- --output build/training-hub/mining-prototype
godot --headless --xr-mode off --path build/training-hub/mining-prototype --import
godot --xr-mode off --path build/training-hub/mining-prototype --script render.gd
```

Output remains under ignored `build/training-hub/mining-prototype/`: GLB, authoring blend, JSON geometry report and two actual Godot Compatibility screenshots. The authoring directory has `.gdignore` to avoid accidental Blender import by Godot.

## Remaining work

The silhouette and close-up equipment are still prototype geometry. Metal and sleeper surfaces need their own authored or CC0 roughness/detail materials; rock layering, practical-light spill and the transition into the hub need art refinement. Current preview uses runtime lights and has not established Quest lighting cost. No animation, moving machinery, sparks or water effects are included in this bay study. Texture compression, export size, baking, headset frame rate and long-session behaviour have not been validated for this prototype. Do not treat the screenshot as release approval or completion of the visual revision.
