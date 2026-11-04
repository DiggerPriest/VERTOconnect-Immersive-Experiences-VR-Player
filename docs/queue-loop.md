# Queue loop

The queue panel now contains a **Loop videos** Off/On control. Off is the default for existing installations. When enabled, automatic completion plays the first item after the final item; this works for every supported queue length (up to the existing 500-item cap), including one item.

Queue order, entries, custom-queue mode, shuffle and loop preferences persist in the existing app settings file. Shuffle repeats the current shuffled traversal; toggling loop does not reshuffle it. Manual previous/next retain their existing boundaries. The developer-only current-video loop continues to take precedence if explicitly enabled.

Automatic advancement still waits for the final presented frame and opens each next entry at zero. It rejects stale completion callbacks and off-head advancement. Headset removal/put-on retains the same active video and restarts it at zero through the existing handover path.

Validation: 399 playback-tools checks passed, including queue lengths 1/2/3/4/10, EOF gates, single-entry reopen from zero, absence handling and loading saved queue settings in a new Main instance. Both hosts passed the full native/workflow/JVM/Godot pipeline for production 0.9.6/code36. The signed production APK and its compiled queue script were independently checked; actual bytecode passed single-entry and two-entry wrap cases. Ryan accepted code35 on 4 November 2026 and requested promotion. The tested scene, audio and playback implementation are retained. See [the production receipt](devices/production-0.9.6.md) for source, APK, checksum and validation limits.

The visual review uses the actual player menu. Shuffle and Loop videos share the existing options row; all controls stay within the original headset canvas capture envelope.
