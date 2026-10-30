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
	main.free()
	print("Headset handover failures: ", failures)
	preload("res://tests/support/test_result.gd").finish(self, 1 if failures else 0)
