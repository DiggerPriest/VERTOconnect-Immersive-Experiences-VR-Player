# Mining factory scene passport

Status: construction specification, not a finished-scene acceptance record.

## Scene and hierarchy

Deliver an offline, surrounding Quest environment assembled in Blender and exported to Godot. Metres, right-handed Z-up in Blender; GLB performs the engine axis conversion. Preview at 1920 × 1080, 30 FPS, frames 1–900. The viewer camera stays stationary at (0, 0, 1.25); only physical headset movement changes the delivered view.

Use a separate `VERTO_MiningFactory` scene. Protect the existing default Scene, Cube, Camera and Light. Semantic collections: ENV_shell, ENV_portal, PRP_workshops, HERO_truck, RIG_fans, LGT_preview. Keep animation roots separate from static geometry; consolidate static export geometry by material only in the export copy.

## Asset layout

Coordinates below are Blender coordinates; positive Y faces the mine portal. Proxy dimensions are footprints, not permission to ship primitive placeholders.

| Asset | Route | Dimensions m | Location m | Final fidelity and audit |
|---|---|---|---|---|
| Factory shell | BLOCK to authored geometry | 40 × 44 × 12 | 0, 0, 6 | Detailed steel columns, roof trusses, skylights, wall panels; enclosing reverse views |
| Mine portal | EXISTING prototype adapted | 10 × 2 × 7 | 0, 20, 3.5 | Continuous opening into tunnel; no wall across entrance |
| Tunnel | EXISTING prototype adapted | 6 × 30 × 5 | 0, 36, 2.5 | Rock, supports and receding practical lights; believable depth |
| Twin ventilation assemblies | BLOCK to authored geometry | each 3 × 4 × 3 | -7, 16, 1.5 and 7, 16, 1.5 | Duct connection, guards, separate rotor pivots; visible rotation |
| Parked haul truck | GEN with retained proxy | 7 × 12 × 6 | 11, 5, 3 | Recognisable truck silhouette, tyres, open engine access; generated intake pending |
| Mechanical workshop | BLOCK to authored geometry | 6 × 12 × 3 | -16, 3, 1.5 | Workbenches, cabinets, service equipment, tool hierarchy |
| Rear service stores | BLOCK to authored geometry | 30 × 4 × 4 | 0, -19, 2 | Shelving, parts and service doors; reverse view remains convincing |
| VERTOconnect sign | BLOCK to authored lettering | 7 × 0.2 × 1 | 0, 19, 8 | Exact lettering, legible contrast, real geometry |

Generated truck estimate/submission: none. Live catalogue verified 2 November 2026; connector exposes text-to-3D but lacks its required pre-submission estimate tool. No credits spent. Keep proxy until generated or replacement asset passes scale, silhouette and material inspection.

## Look and lighting

Concrete, charcoal steel, restrained safety yellow, worn painted equipment and cool daylight. Use real-scale repeating textures at approximately 1–2 metre coverage, selective unique textures on hero assets, and roughness variation. Preserve source provenance. No baked UI or branding in textures.

Portal is the primary visual destination; truck is secondary. Clear central floor gives the menu negative space. Tunnel recesses are the darkest region, with progressively smaller light fixtures showing depth. Skylights motivate the broad overhead key; workshop practicals recover equipment readability. Lock AgX and exposure for preview comparisons. Validate world-only, zero-world, key-only and full lighting before baking/export. Avoid expensive transparent fog in the Quest scene.

## Motion

Two fan rotors turn continuously at independent rates with guarded blades; evaluate aliasing at headset refresh rates. Workshop status indicators and a restrained truck service beacon have independent timing. Truck remains parked, camera never animates, no cranes, no people required, no sound. Exported motion must be verified in Godot, not inferred from Blender keys.

## Acceptance

Inspect seated forward, left, right and reverse views before detail work. Check real dimensions, contact, tunnel continuity and central clearance. Final assets must not read as unresolved primitive proxies. Inspect motion samples and loop seams. Measure Godot draw calls and frame time, then test a Quest session, scenery switching, video/Jess return and wearer removal. Hidden scenery must stop processing. Keep the working panorama default until the user approves the completed world; then make this world the default. APK release and SHA-256 remain required deliverables.
