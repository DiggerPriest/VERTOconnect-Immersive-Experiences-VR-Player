# Immivio 360 fork

This is a modified build of [Immivio](https://github.com/NorthBoundWisdom/immivio),
based on v0.9.4 and distributed under its GPL-3.0 license.

For the intended headset library, videos with no recognized projection or stereo
information default to 360-degree monoscopic playback. A mono/2D marker without
a projection also uses 360 degrees. Recognized projection/stereo format tags,
stereo metadata, mode lock and saved per-video choices still take precedence.
The application has its own package ID and signing key so it can be installed
alongside the original Immivio.

When supported by the headset's OpenXR runtime, a headset removal pauses the
current video and putting it back on restarts that same video at the beginning.
The saved projection and the queue remain intact. This requires real-device
validation; opening a system menu alone must not count as headset removal.

On Android the library opens the current profile's shared-storage
`Managed files` directory. Device and Android permission policies still apply;
if it cannot be read, use the local storage access controls or navigate to a
different folder. Settings choice taps allow modest pointer movement while
retaining same-control release and scroll cancellation.

The interface uses VERTO yellow and charcoal, with a lightweight 3D room as the
default menu scenery. The room is hidden during immersive playback and
passthrough. Original background choices remain available.

The Quest opening screen presents the VERTOconnect Immersive Experiences
VR Player wordmark over the VERTOconnect website's hero artwork, with a
five-second hold and an animated indicator. The library sidebar
shows Immersive Videos and Settings; managed-library browsing starts with a
video-only filter and does not expose the All/Video/Images controls.

Use the Android tag workflow to build the APK. Future updates require the same
release signing key; its repository secrets and the local backup are not part of
this source tree.
