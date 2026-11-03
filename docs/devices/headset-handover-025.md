# .25 headset-removal investigation

## Evidence and change

The .24 headset test reported video continuing after removal. Source inspection found that handover pause/restart was reached only from OpenXR `user_presence_changed`. The extension is requested, but callback delivery on the managed headset was not established. Android activity pause already pauses both native video backends; removal can leave the activity resumed, so this was not an adequate fallback. This identifies an uncovered transition, not proof of which sensor the device exposes.

The candidate adds a native standard proximity listener when Android exposes one, plus Android display-off/display-on broadcasts. Removal stops both native backends immediately and clears requested playback before forwarding the event to Godot. Returning follows the existing same-session seek-to-zero path. Native absence blocks an inconsistent OpenXR-present event, and native return cannot resume a paused Android activity. Hand visibility and window focus are not interpreted as physical wearer presence. Existing Jess return/focus recovery is unchanged.

## Visible diagnostics without USB

The existing temporary return diagnostic now includes:

`Wearer: present/absent/unknown | Source: proximity/screen_off/screen_on/OpenXR | Last off: ... | Off events: ...`

After an absence event, the diagnostic remains visible for 30 seconds on return. It preserves the last removal source so the tester can report evidence after putting the headset back on. The diagnostic timer does not alter Jess state. Before any callback, state is explicitly unknown rather than guessed. Reports also retain this text. Counts represent absence callbacks, not unique people or sessions.

Test while a video plays: remove the headset, listen for playback stopping, put it back on, confirm restart at zero and record the presence line. Repeat with casting off and on. Also close to library before passing the headset, reselect the video, and confirm zero start. Repeat Jess close and hand selection to check regression.

## Validation and limits

Godot `test_headset_handover.gd` passes: pause deduplication, same-session zero restart, changed-session protection, native absence gate, separately labelled sources, last-off retention, diagnostic timer, and no Jess-state mutation. This does not emulate Android sensors.

Native compilation is pending GitHub CI; no local JDK/Android SDK is configured. No physical headset validation has been completed for this change. Quest may not expose a standard proximity sensor. Display-off fallback depends on the managed device's display/sleep policy and may be delayed; it cannot promise instant removal detection. A source/event report from the headset is required before claiming the removal bug fixed.

## Native review follow-up

Initial display state now reads PowerManager after receiver registration, so a headset already asleep at startup is handled without waiting for another SCREEN_OFF broadcast. Native callbacks stop before touching media after plugin close. Main-looper listener cleanup no longer depends on the Activity still existing; the monitor and state gate reject queued callbacks after close.

Added four Android-independent Kotlin JUnit cases for initial screen-off, far-proximity plus screen wake, unavailable-sensor display fallback, and queued events after close. These test production state transitions, but have not run locally because no JDK is configured. GitHub CI must run them and compile the Android adapter. Existing Godot suite results do not establish native compilation.
