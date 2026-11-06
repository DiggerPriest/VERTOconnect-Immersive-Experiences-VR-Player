# Expanded mining factory export

The optional mining environment selects `mining_facility_density/mining_facility.tscn`. Its GLB is the reviewed expanded revision of the existing mining factory, with procedural additions authored in `tools/training_hub/densify_factory.py`. Existing asset and texture provenance remains applicable; this pass adds locally constructed equipment rather than newly downloaded third-party models.

The source-preserving export pipeline is `tools/training_hub/build_density_export.py`: native scene copy, roof and lettering simplification, vertex ambient occlusion, static material batching, then shared animated mesh export. The editable Blender source is included at `assets/authoring/mining_factory.blend`, separately from these disposable export stages; see `native-authoring.md`.

Reviewed GLB SHA-256: `88f778104020c43e05809dab0aa5752b4fbb18d866c5efeb392e7728085b3aac`.

Thirteen added belt sections, service workcells, ventilation branches, guarded machinery and a second service crane expand approximately twice the original projected equipment coverage across six fixed views. Layout, machinery motion, material preservation and desktop rendering checks are recorded in the density performance passport. Desktop performance evidence does not establish Quest frame rate.

The Quest export preset excludes the previous mining environment to avoid packaging both scenes. A standalone exported resource pack successfully loads the selected scene and the existing user-supplied 30-second background audio. The resource pack is not an APK; an isolated beta build and headset review remain necessary before production promotion.
