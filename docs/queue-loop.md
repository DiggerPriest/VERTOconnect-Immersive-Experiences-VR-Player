# Queue loop

The queue panel now contains a **Loop videos** Off/On control. Off is the default for existing installations. When enabled, automatic completion plays the first item after the final item; this works for every supported queue length (up to the existing 500-item cap), including one item.

Queue order, entries, custom-queue mode, shuffle and loop preferences persist in the existing app settings file. Shuffle repeats the current shuffled traversal; toggling loop does not reshuffle it. Manual previous/next retain their existing boundaries. The developer-only current-video loop continues to take precedence if explicitly enabled.

Automatic advancement still waits for the final presented frame and opens each next entry at zero. It rejects stale completion callbacks and off-head advancement. Headset removal/put-on retains the same active video and restarts it at zero through the existing handover path.

Validation: 399 playback-tools checks passed, including queue lengths 1/2/3/4/10, EOF gates, single-entry reopen from zero, absence handling and loading saved queue settings in a new Main instance. The initial queue-only change passed all 84 local Godot cases. The expanded scene adds a dedicated real-export motion case. Both Windows and macOS CI passed on source 0bee805, and the published code35 beta's compiled queue script and bundled scene/audio were independently checked. Ryan reported the beta "worked 100% perfect" on 4 November 2026 and explicitly requested production promotion. Version 0.9.6/code36 changes release metadata and the distribution identity; the tested scene, audio and playback implementation are retained.

The visual review uses the actual player menu. Shuffle and Loop videos share the existing options row; all controls stay within the original headset canvas capture envelope.
