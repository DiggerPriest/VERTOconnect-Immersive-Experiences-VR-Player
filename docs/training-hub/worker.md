# Four-trade worker prototypes

The worker is a real rigged MakeHuman character, with separate jacket, trousers,
boots, safety helmet, chest pockets, zipper, belt, meter and test probe geometry.
The jacket is a regularly modelled cloth shell with reflective bands, not a skin
texture painted over a naked body. Four variants share this rig and garment construction, with different skin and uniform colours, tools, trajectories and task timing. They remain prototypes pending headset review.

## Source and redistribution

- MakeHuman/MPFB 2.0.18 core body and game-engine skeleton, from
  https://github.com/makehumancommunity/mpfb2/tree/v2.0.18/src/mpfb/data
- The core asset licence is CC0:
  https://github.com/makehumancommunity/mpfb2/blob/v2.0.18/LICENSE.ASSETS.md
- The MPFB program is GPL; it is an authoring dependency and is not packaged into
  the player. No third-party clothing library or Mixamo downloads were used.
- Jacket topology, uniform micro-weave pixels, accessories, animation and export
  automation were made specifically for this project.

## Reproduction

Install the official Blender 4.5.3 arm64 release and MPFB 2.0.18 into Blender's
`user_default` extensions repository. The builder checks both version numbers.
Run from the repository root:

```sh
/Users/rpriest/Applications/Blender-4.5.3.app/Contents/MacOS/Blender \
  --background --offline-mode --python-exit-code 1 \
  --python tools/training_hub/build_worker.py -- \
  --mpfb /tmp/verto-mpfb/mpfb2-2.0.18/src --output build/training-hub --trade electrical
```

Repeat with `--trade plumbing`, `--trade carpentry` and `--trade mechanical`.
The source Blender file, exported GLB and per-trade validation report are written to
`build/training-hub`. Copy only the verified GLB into
`app/godot/environments/training_hub/<trade>_worker.glb`.
The `--mpfb` argument is validated: a deterministic content hash of the supplied
`src/mpfb` directory must match the installed extension byte-for-byte (excluding
Python caches). The hash is recorded in the report. The runtime imports the
installed `bl_ext.user_default.mpfb` extension, not an unregistered Python module.
No network access or paid account is used during generation.

## Animation and integration

| Asset | Clip | Activity |
|---|---|---|
| electrical_worker.glb | Electrical_inspection_20s | Meter glance and probe test |
| plumbing_worker.glb | Plumbing_adjust_fitting_24s | Reach, wrench adjustment cycles, inspect, withdraw |
| carpentry_worker.glb | Carpentry_measure_mark_18s | Measure hold, pencil marking strokes, withdraw |
| mechanical_worker.glb | Mechanical_tablet_inspection_26s | Tablet check/tap, machine inspection reach, return to checklist |

The four loops are independently authored, not retimed electrical clips. Each has
its own first/last pose and uses the same tested planted lower-body rig.


`Electrical_inspection_20s` is a 20-second baked skeletal loop. It checks the meter,
raises the test probe, pauses, then returns. The root and feet remain planted.
Godot must explicitly play this animation; loading the scene alone shows its rest
pose. Frame 241 (8 seconds) is the raised-probe phase.

The worker faces Blender -Y / Godot +Z. The agreed scene placement is Godot
`Vector3(1.1, 0, -7.9)`, yaw `PI`, facing the electrical station. This keeps the
worker clear of the bench. The terminal is staged around Blender world
`(1.34, 8.3, 1.2)`. Tool offsets refine the final tip position; visual contact with
the station must still be checked in the combined scene.

## Verified and remaining

The builder checks every exported floating-point GLB accessor for finite values,
including vertex data, inverse bind matrices and animation channels. It also
checks planted foot positions over six sampled times and matching pose matrices
at the loop endpoints. The final worker has 53 bones and approximately 20,000
triangles, within the initial 10–20k worker geometry target. Meshes are limited to
four bone influences per vertex before export.

Blender's bundled glTF exporter prints numerical warnings during a temporary
matrix operation on this machine; the resulting binary accessors are validated
and finite. These warnings have not been hidden. The generated report contains
the exact mesh/triangle counts for the latest run.

Close-up renders were used to find and fix loose shoulder openings, fingertip
geometry accidentally selected as trousers, and wrist-mounted tool positions. A second integrated-preview review added opaque
shoulder coverage and shaped leather toe/ankle geometry. A further Godot review
replaced the spherical shoulder patches with a welded, smoothed jacket surface,
transferred skin weights, a wider hem and straight trouser cuffs. Reflective bands
retain their regular ring topology rather than following irregular remesh faces. Accessories sharing a bone are consolidated to reduce draw work.
Remaining limits: this is custom prototype tailoring, with visible garment seams
and simplified face/skin materials, not a photoreal scanned worker. The four-trade contact poses are staged against station target coordinates; these are visual routines rather than physically simulated tool constraints. Final hand/tool
contact must be reviewed in Godot with the station. Quest frame-time, heat and
long-session tests have not been performed. Do not describe it as production ready.

## Final desktop Godot review (2026-11-02)

Rendered the actual Compatibility scene using `tests/render_training_hub.gd` and
inspected all twelve per-worker screenshots at runtime samples 0, 8 and 16 seconds.
The welded shoulders and widened jacket hems no longer show the separate shoulder
balls or jagged waistband seen in the earlier render. No large body/bench
intersections or displaced feet were visible in these samples.

The initial side-camera review exposed gaps at the wrench and probe. These were
corrected with hand-orientation constraints and per-frame wrist targets derived
from the actual rigid tool tip/throat offset. The probe now points horizontally
into the socket. Wrench jaws were resized to surround the existing hex fitting.
Actual Godot side/front screenshots show these contacts in
`build/output/training-hub/contacts/`. The carpenter pencil reaches the timber
marking plane in the side view. The tablet screen correctly faces its operator; the upper view confirms the extended
index finger touches that screen during the tap. Grips now use stronger finger
curl and the close front view was also used to align the visible irises.

Baked contact validation checks every contact frame against the authoritative
station coordinates (including the electrical mat's 0.0305 m lift): 121 probe
frames, 318 wrench frames, and 34 mechanical index-finger tablet tap frames.
Maximum errors are recorded in each worker's report and must be below 0.003 m.
Only the deliberate contact ranges are constrained: inspection/withdrawal phases
move away from the target. Tool accessories remain attached to their hand bones.

These are desktop geometry and pose checks, not headset stereoscopic validation
or performance measurements. Garments and faces remain simplified mobile meshes;
final visual acceptance and Quest testing are still outstanding.
