# Training hub architecture and four trade bays

## Source and ownership

The geometry in `tools/training_hub/build_hub.py` is custom, script-authored geometry for this project. It does not contain models extracted from the user's reference photographs or from another game. No third-party equipment mesh has been embedded. Concrete, plaster and timber textures are original procedural Blender materials, baked into portable surface textures. Text uses Blender's bundled Bfont. The character is a separate asset and has separate provenance.

This is an architectural/equipment prototype, not a validated electrical training simulation. Labelled instruments and panels provide visual context; their placement and apparent wiring are not instructional diagrams.

## Rebuilding

Pinned authoring runtime: Blender 4.5.3 LTS (official arm64 macOS distribution).

```sh
/Users/rpriest/Applications/Blender-4.5.3.app/Contents/MacOS/Blender --background --python-exit-code 1 --python tools/training_hub/build_hub.py -- --output build/training-hub --bake
```

The command produces:

- `training_hub_authoring.blend`: full procedural materials, geometry and lighting before surface baking.
- `training_hub.blend`: baked export source.
- `training_hub.glb`: geometry with embedded textures for Godot/Quest.
- `baked_*.png`: inspectable surface-lighting atlases.
- `architecture-report.json`: generation provenance and counts.

Only the exported GLB belongs in the shipped Godot environment directory. Blender is not a runtime headset dependency. Running without `--bake` produces the geometry-only diagnostic variant with normal materials, not the intended visual result.

## Current visual work

- Upper galleries with tubular balustrades, glazed classroom partitions and diagonal steel bracing.
- Clerestory windows, timber utility-room doors and service storage.
- Electrical DIN-rail boards with individually modelled breakers, levers, terminal screws and circuit-schedule labels.
- Main isolation enclosures, conduit clips and suspended cable trays.
- Drawer tool trolley, castors, parts bins, screwdrivers, meter and probes.
- Low-voltage practice terminal positioned for the worker animation contact.
- Plumbing circuits with pressure gauges and compression fittings, sink/tap/waste trap, hot-water cylinder and bench valve.
- Carpentry framed doorway, noggins/bracing, timber racks, vice, hand plane, hammer and measuring workpiece.
- Mechanical finned motor, coupling guard, pump and bolted flanges, inspection console and tool boards.
- Procedural concrete, timber and plaster colour/normal variation.
- View-independent 96-sample Cycles diffuse lighting bake with room and task-light shadows; the export uses unlit textures to avoid runtime GI and shadow-map costs.

## Actor placement contract

Blender coordinates are Z-up. The electrical worker stands at `(1.1, 7.9, 0)`, facing +Y. Its right-hand probe target is near `(1.34, 8.3, 1.20)`, at the front of the low test terminal. Corresponding Godot placement is approximately `(1.1, 0, -7.9)`, rotation Y = PI. The bench spans Y 8.1–8.9; moving the worker to Y 8.5 intersects the worktop.

## Limits and next visual checks

All four bays now have custom modelled task equipment. This remains a visual prototype pending integrated worker/contact review. Trade details, baked shadows and textured surfaces must be inspected in the actual Godot render and headset. Baked lighting cannot react to moving workers; the actor needs its own inexpensive lighting/contact-shadow treatment. Metallic surfaces use a diffuse approximation in the static bake; this does not provide physical view-dependent reflections. No headset performance certification is implied by the export.

## Export validation (current prototype)

- 52,020 triangles across 18 mesh primitives.
- 18 materials, including 15 explicitly marked `KHR_materials_unlit` for baked surfaces.
- 15 embedded texture atlases, OIDN denoised through Blender's compositor.
- 28,881,344-byte GLB; no external runtime texture URLs.
- All exported float geometry/transform data passed finite-number validation with `audit_glb.py`.
- These are asset counts, not measured headset draw calls or FPS. Godot appearance and device performance remain the integration/review gate.

The refined lighting pass uses roof-area energy 450 (previously 1800), task lights 50 (previously 130), softer surface bump and 96 bake samples. This avoids clipping the concrete/plaster and reduces indirect-light sampling noise on neutral charcoal steel.

## Four-worker placement contract

All workers stand at station-local Blender `(1.1, -.1, 0)`, facing local +Y. Plumbing lever is `(1.34, .30, 1.20)`; animated wrench hex-fitting contact is `(1.26, .40, 1.38)`; carpentry board top is 1.06 m with ruler top 1.071 m; mechanical is a non-contact tablet inspection. Godot worker roots are electrical `(1.1,0,-7.9)`, plumbing `(7.9,0,1.1)`, carpentry `(-1.1,0,7.9)`, mechanical `(-7.9,0,-1.1)`. Electrical mat top is .0305 m; other feet stand at floor level.

## Texture memory budget

Four 2048-square and eleven 1024-square RGB atlas images: 27 Mi pixels total, approximately 108 MiB decoded RGBA base levels, 144 MiB including full mip chains before GPU compression. Embedded PNG file bytes are not GPU memory. The existing 18 material batches and 15 atlas dimensions are retained for the four-bay expansion; use mobile VRAM texture compression and measure actual Quest memory in the integration build. No 4K/8K scenery atlas is added.

## Broad surface refinement

Concrete now bakes a uniform base with diffuse lighting and shadows. `training_hub_surfaces.gd` replaces exactly three architecture materials with a Compatibility shader: concrete receives subtle world-coordinate repeated detail; graphite receives restrained neutral contrast; skylight receives a soft daylight gradient. Trade geometry and contact coordinates are unchanged.

`tools/training_hub/build_surface_detail.py` generates the original deterministic 512-square texture from seed 421. No downloaded imagery is used. Source is lossless PNG; shipped GPU texture uses mipmapped VRAM compression and an Android ETC2 variant. Additional uncompressed RGBA mip-chain budget is about 1.33 MiB. One extra texture lookup on floor/steel, no extra draw calls or lights.

Actual main-app previews from `tests/render_training_hub_menu.gd` show the real managed-library menu with synthetic example titles, look-around and returned menu states. Desktop screenshots validate layout and shader compilation, not Quest hand interaction or sustained performance.
