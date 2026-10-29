# Immivio 360 fork

This is a modified build of [Immivio](https://github.com/NorthBoundWisdom/immivio),
based on v0.9.4 and distributed under its GPL-3.0 license.

For the intended headset library, videos with no recognized projection or stereo
information default to 360-degree monoscopic playback. Recognized format tags,
stereo metadata, mode lock and saved per-video choices still take precedence.
The application has its own package ID and signing key so it can be installed
alongside the original Immivio.

When supported by the headset's OpenXR runtime, a headset removal pauses the
current video and putting it back on restarts that same video at the beginning.
The saved projection and the queue remain intact. This requires real-device
validation; opening a system menu alone must not count as headset removal.

Use the Android tag workflow to build the APK. Future updates require the same
release signing key; its repository secrets and the local backup are not part of
this source tree.
