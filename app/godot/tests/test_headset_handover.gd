extends SceneTree

const Handover := preload("res://scripts/headset_handover.gd")

class FakeMedia:
	extends RefCounted
	var session_id := 7
	var state := "playing"
	func accepts(id: int) -> bool:
		return id > 0 and id == session_id and state not in ["closed", "failed"]

class FakeVideo:
	extends RefCounted
	var media := FakeMedia.new()
	var local_uri := "file:///video.mp4"
	var requested_play := true
	var geometry := "360 mono"
	var queue := ["one", "two"]
	var seeks: Array[int] = []
	var pauses := 0
	func toggle_play() -> void:
		requested_play = not requested_play
		pauses += 1
	func seek_absolute(position: int) -> bool:
		seeks.append(position)
		return true

class FakeJessPlugin:
	extends RefCounted
	var removals := 0
	func jess_headset_removed() -> void:
		removals += 1

var failures := 0


func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		push_error(message)


func _initialize() -> void:
	if not preload("res://tests/support/test_result.gd").prepare(self):
		return
	var handover := Handover.new()
	var video := FakeVideo.new()
	handover.presence_changed(true, video)
	check(video.seeks.is_empty(), "Startup presence does not restart playback")
	handover.presence_changed(false, video)
	handover.presence_changed(false, video)
	check(not video.requested_play and video.pauses == 1, "Removal pauses once")
	handover.presence_changed(true, video)
	check(video.requested_play and video.seeks == [0], "Put-on restarts from zero")
	check(video.geometry == "360 mono" and video.queue == ["one", "two"], "Mode and queue remain")
	handover.presence_changed(true, video)
	check(video.seeks.size() == 1, "Repeated presence does not restart again")
	handover.presence_changed(false, video)
	video.media.session_id = 8
	handover.presence_changed(true, video)
	check(video.seeks.size() == 1, "A different video session is never restarted")
	handover.presence_changed(false, null)
	handover.presence_changed(true, video)
	check(video.seeks.size() == 1, "Absence without an active video does nothing")
	var main := preload("res://scripts/main.gd").new()
	var jess := FakeJessPlugin.new()
	main.platform_plugin = jess
	main._on_user_presence_changed(true)
	check(jess.removals == 0, "Putting headset on does not end Jess")
	main._on_user_presence_changed(false)
	check(jess.removals == 1, "Removing headset notifies Jess panel")
	check(main._handover_recenter_after == 0, "No recenter occurs while headset is off")
	main._on_user_presence_changed(true)
	check(main._handover_recenter_after > Time.get_ticks_msec(), "New wearer schedules recenter after settling")
	check("unknown" in main._presence_diagnostic_text(), "No callback does not claim presence evidence")
	main._jess_opened = true
	main._on_native_presence_changed(false, "screen_off")
	check("absent" in main._presence_diagnostic_text() and "screen_off" in main._presence_diagnostic_text(), "Diagnostic identifies removal source and state")
	check(main._jess_opened, "Presence diagnostic does not mutate browser return state")
	main._on_user_presence_changed(true)
	check(not main._hub_wearer_present, "XR presence cannot override native confirmed absence")
	check(main._handover_recenter_after == 0, "No return while native display is off")
	main._on_native_presence_changed(true, "screen_on")
	check(main._hub_wearer_present, "Native return releases absence gate")
	check("Last off: screen_off" in main._presence_diagnostic_text(), "On-screen return retains removal evidence")
	check(main._jess_diagnostic_until > Time.get_ticks_msec(), "Presence return makes diagnostic visible for test")
	main._on_openxr_presence_changed(false)
	check("Source: OpenXR" in main._presence_diagnostic_text(), "XR events are labelled separately")
	main.free()
	print("Headset handover failures: ", failures)
	preload("res://tests/support/test_result.gd").finish(self, 1 if failures else 0)
