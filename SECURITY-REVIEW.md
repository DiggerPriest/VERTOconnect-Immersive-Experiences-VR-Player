# Focused security review — 29 October 2026

This is a targeted static review of Immivio v0.9.4 and the fork's changes, not
an independent penetration test or a guarantee that the app is safe.

- Searched the Android app, Godot scripts and native source for network
  destinations, sockets, dynamic code loading, process execution and common
  analytics libraries. No hard-coded China-hosted telemetry or remote-control
  endpoint was identified in the reviewed application source.
- Network access is still present: the original player supports user-selected
  HTTP/HTTPS, SMB, DLNA and Plex sources. LAN discovery and cleartext HTTP
  remain available in the code, though their navigation entries are hidden.
- The local HTTP stream server binds to 127.0.0.1 and uses random source tokens.
  The source review does not establish the security of every possible caller.
- The app requests media permissions and can request broad All files access.
  Android and Meta device policy decide whether access can be granted.
- The earlier Quest APK's eight packaged mpv/FFmpeg libraries matched the hashes
  in the project's dependency manifest. Hashes establish byte identity, not
  the trustworthiness of the upstream binaries.
- Scanned strings in that earlier APK's native libraries and DEX files for
  obvious endpoints and SDK names. Strings alone do not reveal all runtime
  behaviour or obfuscated destinations. No packet capture or real-device
  behavioural test was performed.

The project includes third-party Godot, OpenXR, mpv and FFmpeg binaries and
build-time dependencies. Their full source and compiled behaviour were not
independently audited. Test the new APK on a controlled headset and, if network
assurance is required, inspect its network traffic while exercising local
playback. Meta services may generate separate traffic on the same device.
