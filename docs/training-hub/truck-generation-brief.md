# Mining truck replacement — generation brief

Status: prepared, not submitted. The connector currently lacks the estimate tool required by its generation workflow. Do not claim a generated model exists.

## Reference and fit

Use a low-profile articulated underground haul truck, rather than a tall rigid-frame surface mining truck. Primary reference: https://www.cat.com/en_US/products/new/equipment/underground-hard-rock/underground-mining-trucks/104983.html
Manufacturer spec sheet: https://s7d2.scene7.com/is/content/Caterpillar/CM20200731-92f02-ce6fb

Existing Blender truck comprises 121 mesh objects, with world-space bounds approximately (-16.894,-20.872,-0.060) to (-9.142,-10.016,5.095) metres. These are rotated bounds, not vehicle dimensions. Preserve the service bay and seated viewing clearance; inspect local dimensions before fitting. Keep the old model until replacement passes visual checks.

## Single-object prompt

Create one highly detailed, realistic modern underground articulated mining haul truck for a real-time VR maintenance workshop. Use the proportions and mechanical arrangement of a low-profile AD45-class underground truck: elongated articulated chassis, four large deeply treaded mining tyres, compact protected cab at the front, low dump body at the rear, visible central articulation and hydraulic connections. Industrial yellow painted panels with restrained wear, dark steel chassis, rubber tyres, convincing radiator grille, steps, handholds, access rails, headlamps, hydraulic cylinders and hose routing. Parked with wheels straight, dump body fully lowered, engine stopped. One engine service access panel open to reveal a coherent diesel engine assembly and radiator; do not raise the entire dump body to expose the engine. No people, workshop, terrain, background, lettering, logos, cranes, smoke or motion blur. Complete object from every side, with believable underside and no floating or disconnected components. Prefer clean UV-mapped PBR materials and separated wheels/access panel if the selected model supports this. Metre-scale proportions. We will optimise topology and materials after import; visual detail must come from coherent geometry and textures, not dense random surface noise.

## Intake gates

- Confirm actual output format, textures and licence/provenance before adding to public repository.
- Check all sides, cab/body arrangement, tyre count, panel hinge and engine placement.
- Match the bay without non-uniformly stretching the truck.
- Reduce material count and geometry for Quest after measuring the output.
- Preview from the seated app viewpoint and close-up before removing the original truck.
- Do not promise separately riggable parts merely because the prompt requests them.
