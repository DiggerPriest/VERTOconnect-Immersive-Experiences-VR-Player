SCENE
- intent: dense, believable mining processing and maintenance hall based on supplied references.
- deliverable: editable Blender scene checkpoint, then reviewed game export. Existing production release stays pinned.
- units: metres; axes: right-handed Z-up
- render: preserve source lighting, camera and colour management; review renders 1280x720; 30fps.
- dynamic: yes; slow screening drums, guarded motor drives, existing fans and coal transport, crane travel after clearance audit.

HIERARCHY
- collection/object naming: EXP_Processing, EXP_ServiceGallery, EXP_CompressedAir; semantic EXP_ names.
- parent/child relationships: screen rotor children inherit one rotation rig per unit. Fixed feed/discharge hoods never rotate.
- protected existing objects: portal/signs/traffic lights, conveyor route/hopper, fans/wall penetrations, floor wear, yard, rear service plant and overhead crane; CAM_main.

ASSETS
- A01 Existing hall | [EXISTING] detailed | 40x44x12m | origin | preserved | original scene | context
- A02 Screen A | [BLOCK] detailed target | 4x7x5m | (-12,3,0) | Y axis | grounded feet | EXP_Processing | primary rear-west machinery
- A03 Screen B | [BLOCK] detailed target | 4x7x5m | (-12,11,0) | Y axis | grounded feet | EXP_Processing | repeated processing line
- A04 West service gallery | [BLOCK] detailed target | 1.5x21x4.1m | (-16.5,5.5,0) | wall parallel | deck z4.1 | EXP_ServiceGallery | links rear service platform
- A05 Compressor/receiver skid | [BLOCK] detailed target | 5x3x3.5m | (14,11,0) | grounded | EXP_CompressedAir | right-rear plant
- A06 Service workbenches/parts | [BLOCK] detailed target | 2x6x2m | (18,5,0) | grounded | EXP_CompressedAir | right wall detail
- generation: none, zero credits.

SHOT
- active camera: preserve CAM_main portal-facing default.
- framing/lens/target: preserve source; added review camera faces rear-west from centre eye height.
- foreground: clear central floor; machinery occupies side bays; rear gallery gives upper depth.

LOOK
- material roles: existing yellow safety paint, graphite machinery, galvanized deck/handrails, grey concrete, cool teal motors, subdued red isolation controls.
- route: existing materials reused where possible; new plain Principled materials export safely.
- texture scale: preserve existing concrete and rock PBR.
- relief: bevelled edges and recessed panels, no displacement.
- metallic/roughness: painted equipment roughness .45-.65, bare steel .3-.5; no mirror chrome.
- world/background: preserve.

LIGHTING
- focal subject: portal in default view, processing line in rear view; lower service recesses remain darker.
- mood: daylight through existing high windows plus industrial practicals.
- environment: existing, no generation.
- key/fill/exposure: preserve source pending A/B renders.
- new fixtures: emissive task strips under gallery, no unbounded dynamic light additions.

MOTION
- slow constant drums; 1 revolution/20s, opposing phases; no zero scale keys.
- fixed camera for VR; no camera drift.
- crane: assess before animation; no speculative moving load.

ACCEPTANCE
- structural: supported equipment, connected gallery/stairs with rails/toeboards; central pedestrian route and door approaches remain clear; no unrelated removals.
- motion: inspect evaluated first/mid/end poses and loop seams; no moving fixed hoods, detached drive shafts or intersections.
- visual: full 360 review at eye level; no primitive placeholders in final deliverable; realistic material distinction, contact and sensible equipment connections.
- lighting: source comparison, no clipped new emissive fixtures; retain portal sign read.

References: user supplied plant/crane screenshots; Metso, Designing for efficient mill maintenance (accessed 4 November 2026), https://www.metso.com/insights/blog/mining-and-metals/reline-your-thinking-44-designing-for-efficient-mill-maintenance/ . Applied as access/platform/utility-routing inspiration, not a claim that this fictional hall is an engineered plant.
refs_read: blender-scene, blender-scene-spec, blender-modeling, blender-lookdev, blender-lighting-camera, blender-animation, blender-audit-finalize.
Phases: A specification complete; B source checkpoint preserved; C blockout pending visual gate; D detailed assets pending; E audits pending.

Progress: blockout rendered and reviewed; two detailed drum rigs, gallery/stairs, compressor/receiver, headers and benches are present in build/factory-expansion/VERTO_processing_detail.blend. Detail render reviewed. Whole-room density, guards/transfer connections, additional machinery, motion/contact audit, lighting cleanup and runtime export remain open. Source preview reports EEVEE shadow-buffer overflow; no headset performance claim is made.
