# Queue loop

The queue panel now contains a **Loop videos** Off/On control. Off is the default for existing installations. When enabled, automatic completion plays the first item after the final item; this works for every supported queue length (up to the existing 500-item cap), including one item.

Queue order, entries, custom-queue mode, shuffle and loop preferences persist in the existing app settings file. Shuffle repeats the current shuffled traversal; toggling loop does not reshuffle it. Manual previous/next retain their existing boundaries. The developer-only current-video loop continues to take precedence if explicitly enabled.

Automatic advancement still waits for the final presented frame and opens each next entry at zero. It rejects stale completion callbacks and off-head advancement. Headset removal/put-on retains the same active video and restarts it at zero through the existing handover path.

Validation: 399 playback-tools checks passed, including queue lengths 1/2/3/4/10, EOF gates, single-entry reopen from zero, absence handling and loading saved queue settings in a new Main instance. Both production and dev/test 1.0.0/code37 passed Windows/macOS native/workflow/JVM/Godot pipelines. Both signed APKs and their actual compiled queue scripts were independently checked; bytecode passed single-entry and two-entry wrap cases. Ryan accepted the code35 headset test and approved promotion of the unchanged functionality. See [the 1.0.0 release receipt](devices/release-1.0.0.md) for both APKs, checksums, source and validation limits.

The visual review uses the actual player menu. Shuffle and Loop videos share the existing options row; all controls stay within the original headset canvas capture envelope.
