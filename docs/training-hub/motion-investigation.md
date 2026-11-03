# Stationary-worker report on release .24

Status: the headset report remains unresolved. No animation fix is claimed.

## What was inspected

The release `.24` APK was extracted to an isolated temporary project. Its compiled
GDScript and exported binary scenes were loaded directly, without substituting
source scripts or the empty-animation lifecycle fixture.

- Four actors retained their named clips and 53-bone skeletons.
- The actual exported hub manager loaded four actors and their automatic clocks
  advanced through 2/4/6/8 seconds, with processing enabled, without seeking.
- Sampling the exported poses at 0/5/10/15 seconds changed 4/6/4/4 bones respectively.
- Evaluating the exported mesh skin weights and bind matrices showed jacket/body
  displacements between 0 and 7 seconds of approximately 10 cm electrical, 6 cm plumbing,
  17 cm carpentry and24 cm mechanical. Feet and trousers remained planted.
- Skin-deformation results matched the source scene numerically across 20 meshes.

These results rule out stripped clips and lost skin bindings in the APK on the
host. They do not establish that the Quest renders the updated skins or that its
live application gates remain open. The isolated macOS probe lacked the APK's
Android-only OpenXR vendor binary; those extension-load errors were expected and
were not treated as a passing full app or headset test.

Local evidence logs are `/tmp/verto-apk24-clock.log`, `/tmp/verto-apk24-skin.log`
and `/tmp/verto-source-skin.log`; the temporary probe project is not shipped.

## Optional on-headset diagnostic

The existing session-only Background performance toggle now also reports:

- The actual media/Jess/presence/application/passthrough/focus blocking reasons.
- Scene visibility and process mode.
- Each actor's elapsed clock, current clip position, visibility, effective process
  state and physics-process state.
- Actual changed-bone count since the previous sample and the greatest sampled
  angular change, with the bone name.

This is read-only pose observation. It never seeks animations, updates skeletons
or bypasses safety/lifecycle suspension. The display explicitly labels CPU bone
changes as distinct from verified GPU movement. Physics processing being off is
normal for these process-driven animations. A visible menu can show a blocked
focus state; diagnostics still hide during Jess/media, headset absence,
application pause and passthrough.

## Regression coverage

`test_training_hub_real_motion.gd` loads the real shipped scene and all four rigs,
waits three seconds without calling seek/advance, and requires both clock advance
and changed bone poses for every actor. It also verifies frozen clocks/bones under
suspension and safe diagnostic visibility. This complements the original empty-clip
fixture, which tests loader/scheduling behavior but cannot establish actual rig
motion. Both tests passed the strict host completion/error checks after this
instrumentation change. Headset observation is still required to locate the fault.
