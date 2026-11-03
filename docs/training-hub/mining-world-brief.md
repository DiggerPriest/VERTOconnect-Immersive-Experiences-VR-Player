# Mining factory world — current user brief

This brief supersedes the standalone tunnel and four-worker training-bay layouts.
It records the user's latest direction; it is not a completion report.

## Composition

- A very large modern mining maintenance factory encloses the viewer on all sides.
- The viewer sits in the middle, with natural head rotation and leaning. No scripted camera movement.
- A mine portal is integrated into the factory, with a real tunnel and lights receding into its depth.
- Two large ventilation fans feed fresh air toward the mine portal, with visible duct connections.
- Workshops, service equipment, tools and machinery surround the central viewing area.
- A large parked CAT-style mining truck has its engine compartment open for maintenance. Its exposed engine, access platform, tyres and service equipment must be recognisable at seated viewing distance.
- No cranes. People are not required.
- Maintain a clear central viewing space and readable menu. Look around hides the menu, with an accessible return control.

## Motion

Fans provide continuous purposeful motion. Equipment indicators and restrained workshop effects use independent timing and pauses. Keep the truck parked. No single synchronised whole-scene loop, approaching vehicles, artificial locomotion or scenery audio competing with Jess/video.

Pause animation and scenery rendering during video playback, Jess, wearer absence and application focus loss. Test actual exported motion in Godot, not only authoring keyframes in Blender.

## Asset workflow and evidence

Blender authors the actual scene; Godot renders it on Quest. Higgsfield can supply reference images or downloadable 3D assets once available, but images alone do not provide the requested surrounding geometry. Generated mesh availability, price and topology must be checked before spending. Do not label procedural models as Higgsfield-generated assets.

Use inspected redistributable assets and record source/licence/hash. Preserve editable source and export GLB for reproducible application builds. Keep assets offline at runtime.

The first preview must show the factory from the centre toward the portal and truck, plus reverse/side views proving that the space surrounds the viewer. Label layout placeholders honestly. Final quality requires detailed equipment, believable scale/materials/lighting, verified motion and Quest performance testing.

The current working panorama remains the default until the completed replacement is reviewed and approved. The final approved world should become the default, as requested by the user.
